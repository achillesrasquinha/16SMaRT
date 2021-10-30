import os.path as osp
import csv
import itertools

from jinja2 import Template
import tqdm as tq

from geomeat.config  import PATH
from geomeat.const   import CONST
from geomeat import const
from geomeat import __name__ as NAME

from bpyutils.util.ml      import get_data_dir
from bpyutils.util._dict   import dict_from_list, AutoDict
from bpyutils.util.array   import squash
from bpyutils.util.types   import lmap, lfilter, auto_typecast, build_fn
from bpyutils.util.system  import (
    ShellEnvironment,
    makedirs,
    make_temp_dir, get_files, copy, write, read,
    extract_all
)
from bpyutils.util.string  import get_random_str
from bpyutils.util.request import download_file
from bpyutils.util.environ import getenv
from bpyutils.util._json   import JSONLogger
from bpyutils._compat import iteritems
from bpyutils import parallel, log

logger  = log.get_logger(name = NAME)

CACHE   = PATH["CACHE"]

_DATA_DIR_NAME_FILTERED = "filtered"

def get_csv_data(sample = False):
    path_data = osp.join(PATH["DATA"], "sample.csv" if sample else "data.csv")
    data      = []
    
    with open(path_data) as f:
        reader = csv.reader(f)
        header = next(reader, None)

        data = lmap(lambda x: dict_from_list(header, lmap(auto_typecast, x)), reader)

    return data

def get_fastq(meta, data_dir = None, *args, **kwargs):
    sra, layout = meta["sra"], meta["layout"]

    jobs     = kwargs.get("jobs", CONST["jobs"])
    data_dir = get_data_dir(NAME, data_dir)

    data_logger = JSONLogger(path = osp.join(data_dir, "datalog.json"))

    with ShellEnvironment(cwd = data_dir) as shell:
        sra_dir = osp.join(data_dir, sra)

        if not data_logger[sra]["prefetched"]:
            logger.info("Performing prefetch for SRA %s in directory %s." % (sra, sra_dir))
            shell("prefetch -O {output_dir} {sra}".format(output_dir = sra_dir, sra = sra))

            data_logger[sra]["prefetched"] = True
            data_logger.save()

            logger.success("Successfully prefeteched SRA %s." % sra)

        if not data_logger[sra]["validated"]:
            logger.info("Performing vdb-validate for SRA %s in directory %s." % (sra, sra_dir))
            shell("vdb-validate {dir}".format(dir = data_dir))

            data_logger[sra]["validated"]  = True
            data_logger.save()

            logger.success("Successfully validated SRA %s." % sra)

        if not data_logger[sra]["fastq_path"]:
            logger.info("Downloading FASTQ file(s) for SRA %s..." % sra)
            args = "--split-files" if layout == "paired" else "" 
            shell("fasterq-dump {args} {sra}".format(
                threads = jobs, args = args, sra = sra), cwd = sra_dir)

            data_logger[sra]["fastq_path"] = squash(get_files(sra_dir, "*.fastq"))
            data_logger.save()

            logger.success("Successfully downloaded FASTQ file(s) for SRA %s." % sra)

        data_logger.save()

def get_data(data_dir = None, check = False, *args, **kwargs):
    jobs     = kwargs.get("jobs", CONST["jobs"])

    data_dir = get_data_dir(NAME, data_dir)
    logger.info("Created data directory at %s." % data_dir)

    data     = get_csv_data(sample = check)

    logger.info("Fetching FASTQ files...")
    with parallel.no_daemon_pool(processes = jobs) as pool:
        length   = len(data)

        function = build_fn(get_fastq, data_dir = data_dir, *args, **kwargs)
        results  = pool.imap(function, data)

        list(tq.tqdm(results, total = length))

def _render_template(*args, **kwargs):
    script = kwargs["template"]

    template_path = osp.join(PATH["DATA"], "templates", script)
    template = Template(read(template_path))
    
    rendered = template.render(*args, **kwargs)

    return rendered

def _get_fastq_file_line(fname):
    prefix, _ = osp.splitext(fname)
    prefix    = osp.basename(prefix)

    return "%s %s" % (prefix, fname)

def _mothur_filter_files(config):
    files      = config.pop("files")
    target_dir = config.pop("target_dir")

    primer_f   = config.pop("primer_f")
    primer_r   = config.pop("primer_r")

    layout     = config.get("layout")
    trim_type  = config.get("trim_type")

    with make_temp_dir(root_dir = CACHE) as tmp_dir:
        logger.info("Copying FASTQ files for pre-processing at %s..." % tmp_dir)
        copy(*files, dest = tmp_dir)

        prefix = get_random_str()
        logger.info("Using prefix %s..." % prefix)

        if layout == "single":
            fastq_file = osp.join(tmp_dir, "%s.file" % prefix)
            fastq_data = "\n".join(lmap(_get_fastq_file_line, files))
            write(fastq_file, fastq_data)

            config["fastq_file"] = fastq_file

            config["group"] = osp.join(tmp_dir, "%s.group" % prefix)

        if layout == "paired" and trim_type == "false":
            oligos_file = osp.join(tmp_dir, "primers.oligos")
            oligos_data = "primer %s %s" % (primer_f, primer_r)
            write(oligos_file, oligos_data)

            config["oligos"] = oligos_file

        template      = "mothur-filter"
        mothur_file   = osp.join(tmp_dir, template)
        logger.info("Building script %s for mothur..." % template)
        mothur_script = _render_template(template = template, inputdir = tmp_dir,
            prefix = prefix, processors = CONST["jobs"],
            qaverage = const.QUALITY_AVERAGE,
            maxambig = const.MAX_AMBIGUITY,
            maxhomop = const.MAX_HOMOPOLYMERS,
            **config
        )
        write(mothur_file, mothur_script)

        logger.info("Running mothur...")

        with ShellEnvironment(cwd = tmp_dir) as shell:
            shell("mothur %s" % mothur_file)

        choice = (".trim.contigs.trim.good.fasta", ".contigs.good.groups") \
            if layout == "paired" else (".trim.good.fasta", ".good.group") # group(s): are you f'king kiddin' me?

        makedirs(target_dir, exist_ok = True)
        
        copy(
            osp.join(tmp_dir, "%s%s" % (prefix, choice[0])),
            dest = osp.join(target_dir, "filtered.fasta")
        )

        copy(
            osp.join(tmp_dir, "%s%s" % (prefix, choice[1])),
            dest = osp.join(target_dir, "filtered.group")
        )

        copy(
            osp.join(tmp_dir, "%s%s" % (prefix, ".trim.contigs.trim.good.summary")),
            dest = osp.join(target_dir, "filtered.summary")
        )

        logger.info("Successfully completed.")

def install_silva(*args, **kwargs):
    path_silva_seed = osp.join(PATH["CACHE"], "silva.seed_v132.tgz")
    path_target = osp.join(PATH["CACHE"], "silva")

    if not osp.exists(path_silva_seed):
        logger.info("Downloading SILVA seed v132 database...")

        download_file(CONST["url_silva_seed_132"], path_silva_seed)
        extract_all(path_silva_seed, path_target)

    path_silva_gold_bacteria = osp.join(PATH["CACHE"], "silva.gold.bacteria.zip")

    if not osp.exists(path_silva_gold_bacteria):
        logger.info("Downloading SILVA for chimera...")

        download_file(CONST["url_silva_gold_bacteria"], path_silva_gold_bacteria)
        extract_all(path_silva_gold_bacteria, path_target)

    return path_target

def _merge_and_preprocess_files(data_dir, silva_path):
    filtered_dir = osp.join(data_dir, _DATA_DIR_NAME_FILTERED)

    filtered = get_files(filtered_dir, "*.fasta")
    groups   = get_files(filtered_dir, "*.group")

    with make_temp_dir(root_dir = CACHE) as tmp_dir:
        files = filtered + groups
        copy(*files, dest = tmp_dir)

        template    = "mothur-merge"
        mothur_file = osp.join(tmp_dir, template)

        logger.info("Building script %s for mothur..." % template)

        output_fasta  = osp.join(tmp_dir, "merged.fasta")
        output_group  = osp.join(tmp_dir, "merged.group")
    
        mothur_script = _render_template(
            template = template,
            input_fastas = filtered,
            input_groups = groups,
            output_fasta = output_fasta,
            output_group = output_group,
            silva_seed_path      = osp.join(silva_path, "silva.seed_v132.align"),

            silva_seed_pcr_align = osp.join(silva_path, "silva.seed_v132.pcr.align"),

            silva_gold_path = osp.join(silva_path, "silva.gold.bacteria.align")

        )
        write(mothur_file, mothur_script)

        with ShellEnvironment(cwd = tmp_dir) as shell:
            shell("mothur %s" % mothur_file)

        copy(
            output_fasta,
            output_group,
            dest = filtered_dir
        )

        logger.info("Successfully merged.")

def _filter_fastq(data_dir = None, check = False):
    data_dir = get_data_dir(data_dir)
    data     = get_csv_data(sample = check)

    filtered_dir = makedirs(osp.join(data_dir, _DATA_DIR_NAME_FILTERED), exist_ok = True)
    logger.info("Storing filtered FASTQ files at %s." % filtered_dir)

    mothur_configs = [ ]

    study_group = AutoDict(list)

    for d in data:
        study_id = d.pop("study_id")
        study_group[study_id].append(d)

    for layout, trim_type in itertools.product(("paired", "single"), ("true", "false")):
        for study_id, data in iteritems(study_group):
            if len(data):
                logger.info("Filtering FASTQ files for study %s of type (layout: %s, trimmed: %s)" % (study_id, layout, trim_type))

                sample = data[0]

                filtered = lfilter(lambda x: x["layout"] == layout and x["trimmed"] == trim_type, data)
                files    = []

                for d in filtered:
                    sra_id  = d["sra"]
                    sra_dir = osp.join(data_dir, sra_id)
                    fasta_files = get_files(sra_dir, "*.fastq")

                    files += fasta_files

                logger.info("FASTQ files found: %s" % files)

                tar_dir = osp.join(filtered_dir, study_id, layout,
                    "trimmed" if trim_type == "true" else "untrimmed")

                mothur_configs.append({
                    "files": files,
                    "target_dir": tar_dir,
                    # NOTE: This is under the assumption that each study has the same primer.
                    "primer_f": sample["primer_f"],
                    "primer_r": sample["primer_r"],

                    "layout": layout, "trim_type": trim_type,
                    
                    "min_length": sample["min_length"],
                    "max_length": sample["max_length"]
                })

    logger.info("Filtering files using mothur....")
    with parallel.no_daemon_pool(processes = CONST["jobs"]) as pool:
        pool.map(_mothur_filter_files, mothur_configs)

    logger.info("Installing SILVA...")
    path_silva = install_silva()


    logger.info("Merging files...")
    _merge_and_preprocess_files(data_dir = data_dir,
        silva_path = path_silva)
    
def preprocess_data(data_dir = None, check = False, *args, **kwargs):
    data_dir = get_data_dir(data_dir)

    logger.info("Filtering FASTQ files...")
    _filter_fastq(data_dir = data_dir, check = check, *args, **kwargs)