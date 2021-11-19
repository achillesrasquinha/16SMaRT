import os.path as osp
import csv
import itertools

import tqdm as tq

from geomeat.config  import PATH
from geomeat import settings, __name__ as NAME
from geomeat.data.util import install_silva

from bpyutils.util.ml      import get_data_dir
from bpyutils.util.array   import chunkify
from bpyutils.util._dict   import dict_from_list, AutoDict
from bpyutils.util.types   import lmap, lfilter, auto_typecast, build_fn
from bpyutils.util.system  import (
    ShellEnvironment,
    makedirs,
    make_temp_dir, get_files, copy, write, move
)
from bpyutils.util.string    import get_random_str
from bpyutils.exception      import PopenError
from bpyutils._compat import itervalues, iteritems
from bpyutils import parallel, log

from geomeat.data.util import render_template

logger = log.get_logger(name = NAME)

CACHE  = PATH["CACHE"]

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

    jobs     = kwargs.get("jobs", settings.get("jobs"))
    data_dir = get_data_dir(NAME, data_dir)

    with ShellEnvironment(cwd = data_dir) as shell:
        sra_dir = osp.join(data_dir, sra)

        logger.info("Checking if SRA %s is prefetched..." % sra)
        path_sra = osp.join(sra_dir, "%s.sra" % sra)

        if not osp.exists(path_sra):
            logger.info("Performing prefetch for SRA %s in directory %s." % (sra, sra_dir))
            code = shell("prefetch -O {output_dir} {sra}".format(output_dir = sra_dir, sra = sra))

            if not code:
                logger.success("Successfully prefeteched SRA %s." % sra)

                logger.info("Validating SRA %s..." % sra)
                logger.info("Performing vdb-validate for SRA %s in directory %s." % (sra, sra_dir))
                code = shell("vdb-validate {dir}".format(dir = sra_dir))

                if not code:
                    logger.success("Successfully validated SRA %s." % sra)
                else:
                    logger.error("Unable to validate SRA %s." % sra)
                    return
            else:
                logger.error("Unable to prefetech SRA %s." % sra)
                return
        else:
            logger.warn("SRA %s already prefeteched." % sra)

        logger.info("Checking if FASTQ files for SRA %s has been downloaded..." % sra)
        fastq_files = get_files(sra_dir, "*.fastq")
        
        if not fastq_files:
            logger.info("Downloading FASTQ file(s) for SRA %s..." % sra)
            args = "--split-files" if layout == "paired" else "" 
            code = shell("fasterq-dump --threads {threads} {args} {sra}".format(
                threads = jobs, args = args, sra = sra), cwd = sra_dir)

            if not code:
                logger.success("Successfully downloaded FASTQ file(s) for SRA %s." % sra)
            else:
                logger.error("Unable to download FASTQ file(s) for SRA %s." % sra)
        else:
            logger.warn("FASTQ file(s) for SRA %s already exist." % sra)

def get_data(data_dir = None, check = False, *args, **kwargs):
    jobs = kwargs.get("jobs", settings.get("jobs"))

    data_dir = get_data_dir(NAME, data_dir)
    logger.info("Created data directory at %s." % data_dir)

    data = get_csv_data(sample = check)

    logger.info("Fetching FASTQ files...")
    with parallel.no_daemon_pool(processes = jobs) as pool:
        length   = len(data)

        function = build_fn(get_fastq, data_dir = data_dir,
            raise_err = False, *args, **kwargs)
        results  = pool.imap(function, data)

        list(tq.tqdm(results, total = length))

def _get_fastq_file_line(fname):
    prefix, _ = osp.splitext(fname)
    prefix    = osp.basename(prefix)

    return "%s %s" % (prefix, fname)

def _build_mothur_script(*args, **kwargs):
    template = kwargs.get("template")
    output   = kwargs.pop("output")

    logger.info("Building script %s for mothur with args: %s" % (template, kwargs))

    mothur_script = render_template(*args, **kwargs)
    write(output, mothur_script)

def _mothur_filter_files(config, data_dir = None, *args, **kwargs):
    logger.info("Using config %s to filter files." % config)

    jobs       = kwargs.get("jobs", settings.get("jobs"))
    data_dir   = get_data_dir(NAME, data_dir)

    files      = config.pop("files")
    target_dir = config.pop("target_dir")

    primer_f   = config.pop("primer_f")
    primer_r   = config.pop("primer_r")

    layout     = config.get("layout")
    trim_type  = config.get("trim_type")

    sra_id     = config.pop("sra_id")
    study_id   = config.pop("study_id")

    target_types = ("fasta", "group", "summary")
    target_path  = dict_from_list(
        target_types,
        lmap(lambda x: osp.join(target_dir, "filtered.%s" % x), target_types)
    )

    if not all(osp.exists(x) for x in itervalues(target_path)):
        with make_temp_dir(root_dir = CACHE) as tmp_dir:
            logger.info("[SRA %s] Copying FASTQ files %s for pre-processing at %s." % (sra_id, files, tmp_dir))
            copy(*files, dest = tmp_dir)

            prefix = get_random_str()
            logger.info("[SRA %s] Using prefix for mothur: %s" % (sra_id, prefix))

            logger.info("[SRA %s] Setting up directory %s for preprocessing" % (sra_id, tmp_dir))

            if layout == "single":
                fastq_file = osp.join(tmp_dir, "%s.file" % prefix)
                fastq_data = "\n".join(lmap(_get_fastq_file_line, files))
                write(fastq_file, fastq_data)

                config["fastq_file"] = fastq_file
                config["group"]      = osp.join(tmp_dir, "%s.group" % prefix)

            if trim_type == "false":
                oligos_file = osp.join(tmp_dir, "primers.oligos")
                oligos_data = "primer %s %s %s" % (primer_f, primer_r, study_id)
                write(oligos_file, oligos_data)

                config["oligos"] = oligos_file

            mothur_file = osp.join(tmp_dir, "script")
            _build_mothur_script(
                template = "mothur/filter",
                output   = mothur_file,
                inputdir = tmp_dir, prefix = prefix, processors = jobs,
                qaverage = settings.get("quality_average"),
                maxambig = settings.get("maximum_ambiguity"),
                maxhomop = settings.get("maximum_homopolymers"),
                pdiffs   = settings.get("primer_difference"),
                **config
            )

            logger.info("[SRA %s] Running mothur..." % sra_id)

            try:
                with ShellEnvironment(cwd = tmp_dir) as shell:
                    code = shell("mothur %s" % mothur_file)

                    if not code:
                        logger.success("[SRA %s] mothur ran successfully." % sra_id)

                        logger.info("[SRA %s] Attempting to copy filtered files." % sra_id)

                        choice = (
                            ".trim.contigs.trim.good.fasta",
                            ".contigs.good.groups",
                            ".trim.contigs.trim.good.summary"
                        ) if layout == "paired" else (
                            ".trim.good.fasta",
                            ".good.group",
                            ".trim.good.summary"
                        )
                            # group(s): are you f'king kiddin' me?

                        makedirs(target_dir, exist_ok = True)
                
                        copy(
                            osp.join(tmp_dir, "%s%s" % (prefix, choice[0])),
                            dest = target_path["fasta"]
                        )

                        copy(
                            osp.join(tmp_dir, "%s%s" % (prefix, choice[1])),
                            dest = target_path["group"]
                        )

                        copy(
                            osp.join(tmp_dir, "%s%s" % (prefix, choice[2])),
                            dest = target_path["summary"]
                        )

                        logger.info("[SRA %s] Successfully copied filtered files at %s." % (sra_id, target_dir))
            except PopenError as e:
                logger.error("[SRA %s] Unable to filter files. Error: %s" % (sra_id, e))
    else:
        logger.warn("[SRA %s] Filtered files already exists." % sra_id)

def merge_fastq(data_dir = None):
    data_dir = get_data_dir(NAME, data_dir = data_dir)

    logger.info("Finding files in directory: %s" % data_dir)
    
    filtered = get_files(data_dir, "filtered.fasta")
    groups   = get_files(data_dir, "filtered.group")

    if filtered and groups:
        logger.info("Merging %s filter and %s group files." % (len(filtered), len(groups)))

        output_fasta = osp.join(data_dir, "merged.fasta")
        output_group = osp.join(data_dir, "merged.group")

        with make_temp_dir(root_dir = CACHE) as tmp_dir:
            mothur_file = osp.join(tmp_dir, "script")
            _build_mothur_script(
                template     = "mothur/merge", 
                output       = mothur_file,
                input_fastas = filtered,
                input_groups = groups,
                output_fasta = output_fasta,
                output_group = output_group
            )

            with ShellEnvironment(cwd = tmp_dir) as shell:
                code = shell("mothur %s" % mothur_file)

                if not code:
                    # HACK: weird hack around failure of mothur detecting output for merge.files
                    merged_fasta = get_files(data_dir, "merged.fasta")
                    merged_group = get_files(data_dir, "merged.group")

                    move(*merged_fasta, dest = output_fasta)
                    move(*merged_group, dest = output_group)

                    logger.success("Successfully merged.")
                else:
                    logger.error("Error merging files.")
    else:
        logger.warn("No files found to merge.")

def filter_fastq(data_dir = None, check = False, *args, **kwargs):
    jobs = kwargs.get("jobs", settings.get("jobs"))    

    data_dir = get_data_dir(NAME, data_dir = data_dir)

    data = get_csv_data(sample = check)

    filtered_dir = makedirs(osp.join(data_dir, _DATA_DIR_NAME_FILTERED), exist_ok = True)
    logger.info("Storing filtered FASTQ files at %s." % filtered_dir)

    mothur_configs = [ ]

    study_group    = AutoDict(list)

    for d in data:
        study_id = d.pop("study_id")
        study_group[study_id].append(d)

    logger.info("Building configs for mothur...")

    for layout, trim_type in itertools.product(("paired", "single"), ("true", "false")):
        for study_id, data in iteritems(study_group):
            if len(data):
                filtered = lfilter(lambda x: x["layout"] == layout and x["trimmed"] == trim_type, data)
                files    = []

                for d in filtered:
                    sra_id  = d["sra"]
                    sra_dir = osp.join(data_dir, sra_id)
                    fasta_files = get_files(sra_dir, "*.fastq")

                    files += fasta_files

                if files:
                    logger.info("Filtering FASTQ files for study %s of type (layout: %s, trimmed: %s)" % (study_id, layout, trim_type))

                    sample  = data[0]

                    tar_dir = osp.join(filtered_dir, study_id, layout,
                        "trimmed" if trim_type == "true" else "untrimmed")

                    mothur_configs.append({
                        "files": files,
                        "target_dir": tar_dir,

                        "study_id": study_id,

                        # NOTE: This is under the assumption that each study has the same primer.
                        "primer_f": sample["primer_f"],
                        "primer_r": sample["primer_r"],

                        "layout": layout, "trim_type": trim_type,
                        
                        "min_length": sample["min_length"],
                        "max_length": sample["max_length"]
                    })

    if mothur_configs:
        logger.info("Filtering files using mothur using %s jobs...." % jobs)

        filter_chunks = settings.get("filter_chunks")

        for chunk in chunkify(mothur_configs, filter_chunks):
            with parallel.no_daemon_pool(processes = jobs) as pool:
                length    = len(mothur_configs)
                function_ = build_fn(_mothur_filter_files, *args, **kwargs)
                results   = pool.imap(function_, chunk)

                list(tq.tqdm(results, total = length))

def preprocess_fasta(data_dir = None, *args, **kwargs):
    data_dir = get_data_dir(NAME, data_dir)
    
    jobs     = kwargs.get("jobs", settings.get("jobs"))

    merged_fasta = osp.join(data_dir, "merged.fasta")
    merged_group = osp.join(data_dir, "merged.group")

    silva_seed = kwargs["silva_seed"]
    silva_gold = kwargs["silva_gold"]
    silva_seed_tax = kwargs["silva_seed_tax"]

    files = (merged_fasta, merged_group, silva_seed, silva_gold)

    with make_temp_dir(root_dir = CACHE) as tmp_dir:
        copy(*files, dest = tmp_dir)

        silva_seed_splitext = osp.splitext(osp.basename(silva_seed))

        mothur_file = osp.join(tmp_dir, "script")
        _build_mothur_script(
            template = "mothur/preprocess",
            output   = mothur_file,
            merged_fasta = osp.join(tmp_dir, osp.basename(merged_fasta)),
            merged_group = osp.join(tmp_dir, osp.basename(merged_group)),

            silva_seed       = osp.join(tmp_dir, osp.basename(silva_seed)),
            silva_seed_start = settings.get("silva_seed_pcr_start"),
            silva_seed_end   = settings.get("silva_seed_pcr_end"),

            silva_seed_pcr   = osp.join(tmp_dir, "%s.pcr%s" % (silva_seed_splitext[0], silva_seed_splitext[1])),
            
            silva_seed_tax   = osp.join(tmp_dir, osp.basename(silva_seed_tax)),
            silva_gold       = osp.join(tmp_dir, osp.basename(silva_gold)),

            maxhomop         = settings.get("maximum_homopolymers"),

            processors       = jobs
        )

        with ShellEnvironment(cwd = tmp_dir) as shell:
            code = shell("mothur %s" % mothur_file)

            if not code:
                pass
            else:
                logger.error("Error merging files.")

def preprocess_data(data_dir = None, check = False, *args, **kwargs):
    data_dir = get_data_dir(NAME, data_dir)

    logger.info("Attempting to filter FASTQ files...")
    filter_fastq(data_dir = data_dir, check = check, *args, **kwargs)

    logger.info("Merging FASTQs...")
    merge_fastq(data_dir = data_dir)

    logger.info("Installing SILVA...")
    silva_paths = install_silva()

    logger.success("SILVA successfully downloaded at %s." % silva_paths)
    
    logger.info("Pre-processing FASTA + Group files...")
    preprocess_fasta(data_dir = data_dir,
        silva_seed = silva_paths["seed"], silva_gold = silva_paths["gold"],
        silva_seed_tax = silva_paths["taxonomy"]
    )

def check_data(data_dir = None):
    pass