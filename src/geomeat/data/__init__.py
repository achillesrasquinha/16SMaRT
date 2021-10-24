import os.path as osp
import csv
import itertools

from jinja2 import Template

from geomeat.config  import PATH
from geomeat import const
from geomeat import __name__ as NAME

from bpyutils.util._dict   import dict_from_list, AutoDict
from bpyutils.util.types   import lmap, lfilter, auto_typecast, build_fn
from bpyutils.util.system  import (
    ShellEnvironment,
    makedirs,
    make_temp_dir, get_files, copy, write, read
)
from bpyutils.util.string  import get_random_str
from bpyutils.util.environ import getenv
from bpyutils._compat import iteritems
from bpyutils import parallel, log

logger  = log.get_logger(name = __name__)

_PREFIX = NAME.upper()

def get_data_dir(data_dir = None):
    data_dir = data_dir \
        or getenv("DATA_DIR", prefix = _PREFIX) \
        or osp.join(PATH["CACHE"], "data")

    makedirs(data_dir, exist_ok = True)

    return data_dir

def get_csv_data(sample = False):
    path_data = osp.join(PATH["DATA"], "sample.csv" if sample else "data.csv")
    data      = []
    
    with open(path_data) as f:
        reader = csv.reader(f)
        header = next(reader, None)

        data = lmap(lambda x: dict_from_list(header, lmap(auto_typecast, x)), reader)

    return data

def _fetch_sra_to_fastq(meta, output_dir):
    sra, layout = meta["sra"], meta["layout"]

    with ShellEnvironment(cwd = output_dir) as shell:
        sra_dir = osp.join(output_dir, sra)

        logger.info("Performing prefetch for SRA %s in directory %s..." % (sra, sra_dir))
        shell("prefetch {sra}".format(sra = sra))

        logger.info("Performing vdb-validate for SRA %s in directory %s..." % (sra, sra_dir))
        shell("vdb-validate {dir}".format(dir = sra_dir))

        logger.info("Downloading FASTA file for SRA %s..." % sra)
        args = "--split-files" if layout == "paired" else "" 
        shell("fasterq-dump {args} {sra}".format(
            threads = const.N_JOBS, args = args, sra = sra), cwd = sra_dir)

        logger.success("FASTA file for SRA %s successfully downloaded." % sra)

def get_data(data_dir = None, check = False, *args, **kwargs):
    data_dir = get_data_dir(data_dir)
    data     = get_csv_data(sample = check)

    logger.info("Loading data into directory: %s" % data_dir)

    logger.info("Fetching FASTA files...")

    with parallel.no_daemon_pool(processes = const.N_JOBS) as pool:
        function = build_fn(_fetch_sra_to_fastq, output_dir = data_dir)
        pool.map(function, data)

def _render_mothur_script(*args, **kwargs):
    template_path = osp.join(PATH["DATA"], "templates", "mothur-trim")
    template = Template(read(template_path))
    
    rendered = template.render(*args, **kwargs)

    return rendered

def _get_fastq_file_line(fname):
    prefix, _ = osp.splitext(fname)
    return "%s %s" % (osp.basename(prefix), fname)

def _mothur_trim_files(config):
    files      = config.pop("files")
    target_dir = config.pop("target_dir")

    primer_f   = config.pop("primer_f")
    primer_r   = config.pop("primer_r")

    layout     = config.get("layout")
    trim_type  = config.get("trim_type")

    makedirs(target_dir, exist_ok = True)

    with make_temp_dir() as tmp_dir:
        copy(*files, dest = tmp_dir)

        prefix = get_random_str()

        if layout == "paired" and trim_type == "false":
            oligos_file = osp.join(tmp_dir, "meta.oligos")
            oligos_data = "primer %s %s" % (primer_f, primer_r)
            write(oligos_file, oligos_data)

            config["oligos"] = oligos_file

        if layout == "single":
            fastq_file  = osp.join(tmp_dir, "%s.file" % prefix)
            fastq_data  = "\n".join(lmap(_get_fastq_file_line, files))
            write(fastq_file, fastq_data)

            config["fastq_file"] = fastq_file

            config["group"] = osp.join(tmp_dir, "%s.group" % prefix)

        mothur_file   = osp.join(tmp_dir, "source")
        mothur_script = _render_mothur_script(inputdir = tmp_dir,
            prefix = prefix, processors = const.N_JOBS,
            qaverage = const.QUALITY_AVERAGE,
            maxambig = const.MAX_AMBIGUITY,
            maxhomop = const.MAX_HOMOPOLYMERS,
            **config
        )
        write(mothur_file, mothur_script)
        
        with ShellEnvironment(cwd = tmp_dir) as shell:
            shell("mothur %s" % mothur_file)

        choice = (".trim.contigs.trim.good.fasta", ".contigs.good.groups") \
            if layout == "paired" else (".trim.good.fasta", ".good.group") # group(s): are you f'king kiddin' me?
        
        copy(
            osp.join(tmp_dir, "%s%s" % (prefix, choice[0])),
            dest = osp.join(target_dir, "output.fasta")
        )

        copy(
            osp.join(tmp_dir, "%s%s" % (prefix, choice[1])),
            dest = osp.join(target_dir, "output.group")
        )

def _trim_primers(check = False, data_dir = None, force = True):
    data_dir = get_data_dir(data_dir)
    data     = get_csv_data(sample = check)

    preprop_dir = osp.join(data_dir, "preprop")
    makedirs(preprop_dir, exist_ok = True)

    mothur_configs = [ ]

    study_group = AutoDict(list)

    for d in data:
        study_id = d.pop("study_id")
        study_group[study_id].append(d)

    for study_id, data in iteritems(study_group):
        files  = []

        sample = data[0] # TODO: Check if fails.

        for layout, trim_type in itertools.product(("paired", "single"), ("true", "false")):
            filtered = lfilter(lambda x: x["layout"] == layout and x["trimmed"] == trim_type, data)
            
            for d in filtered:
                sra_id  = d["sra"]
                sra_dir = osp.join(data_dir, sra_id)
                fasta_files = get_files(sra_dir, "*.fastq")

                files += fasta_files

            tar_dir = osp.join(preprop_dir, study_id)

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

    with parallel.no_daemon_pool(processes = const.N_JOBS) as pool:
        pool.map(_mothur_trim_files, mothur_configs)
    
def preprocess_data(data_dir = None, check = False, *args, **kwargs):
    data_dir = get_data_dir(data_dir)
    _trim_primers(data_dir = data_dir, check = check, *args, **kwargs)