import os, os.path as osp
import csv
import itertools

import tqdm as tq

from s3mart.config  import PATH
from s3mart import settings, __name__ as NAME
from s3mart.data.util import install_silva

from bpyutils.util._csv    import read as read_csv
from bpyutils.util.ml      import get_data_dir
from bpyutils.util.array   import chunkify
from bpyutils.util._dict   import dict_from_list, AutoDict
from bpyutils.util.types   import lmap, lfilter, build_fn
from bpyutils.util.system  import (
    ShellEnvironment,
    makedirs,
    make_temp_dir, get_files, copy, write, move
)
from bpyutils.util.string    import get_random_str
from bpyutils.exception      import PopenError
from bpyutils._compat import itervalues, iteritems
from bpyutils import parallel, log

from s3mart.data.functions.get_fastq import get_fastq
from s3mart.data.util import render_template

logger = log.get_logger(name = NAME)

CACHE  = PATH["CACHE"]

_DATA_DIR_NAME_FILTERED = "filtered"

def get_data(input = None, data_dir = None, *args, **kwargs):
    if input:
        input = osp.abspath(input)

        if osp.isdir(input):
            data_dir = input
    else:
        input = osp.join(PATH["DATA"], "sample.csv")

    data = []

    if osp.isfile(input):
        data = read_csv(input)

    data_dir = get_data_dir(NAME, data_dir)
    jobs     = kwargs.get("jobs", settings.get("jobs"))

    logger.info("Data directory at %s." % data_dir)

    if data:
        logger.info("Fetching FASTQ files...")
        with parallel.no_daemon_pool(progress = True, processes = jobs) as pool:
            length   = len(data)

            function = build_fn(get_fastq, data_dir = data_dir, *args, **kwargs)
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
    print(mothur_script)
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

    group      = config.pop("group")

    target_types = ("fasta", "group", "summary")
    target_path  = dict_from_list(
        target_types,
        lmap(lambda x: osp.join(target_dir, "filtered.%s" % x), target_types)
    )

    if not all(osp.exists(x) for x in itervalues(target_path)):
        with make_temp_dir(root_dir = CACHE) as tmp_dir:
            logger.info("[group %s] Copying FASTQ files %s for pre-processing at %s." % (group, files, tmp_dir))
            copy(*files, dest = tmp_dir)

            prefix = get_random_str()
            logger.info("[group %s] Using prefix for mothur: %s" % (group, prefix))

            logger.info("[group %s] Setting up directory %s for preprocessing" % (group, tmp_dir))

            if layout == "single":
                fastq_file = osp.join(tmp_dir, "%s.file" % prefix)
                fastq_data = "\n".join(lmap(_get_fastq_file_line, files))
                write(fastq_file, fastq_data)

                config["fastq_file"] = fastq_file
                config["group"]      = osp.join(tmp_dir, "%s.group" % prefix)

            if trim_type == "false":
                oligos_file = osp.join(tmp_dir, "primers.oligos")
                oligos_data = "primer %s %s %s" % (primer_f, primer_r, group)
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

            logger.info("[group %s] Running mothur..." % group)

            try:
                with ShellEnvironment(cwd = tmp_dir) as shell:
                    code = shell("mothur %s" % mothur_file)

                    if not code:
                        logger.success("[group %s] mothur ran successfully." % group)

                        logger.info("[group %s] Attempting to copy filtered files." % group)

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

                        logger.info("[group %s] Successfully copied filtered files at %s." % (group, target_dir))
            except PopenError as e:
                logger.error("[group %s] Unable to filter files. Error: %s" % (group, e))
    else:
        logger.warn("[group %s] Filtered files already exists." % group)

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
        group = d.pop("group")
        study_group[group].append(d)

    logger.info("Building configs for mothur...")

    for layout, trim_type in itertools.product(("paired", "single"), ("true", "false")):
        for group, data in iteritems(study_group):
            if len(data):
                filtered = lfilter(lambda x: x["layout"] == layout and x["trimmed"] == trim_type, data)
                files    = []

                for d in filtered:
                    sra_id  = d["sra"]
                    sra_dir = osp.join(data_dir, sra_id)
                    fasta_files = get_files(sra_dir, "*.fastq")

                    files += fasta_files

                if files:
                    logger.info("Filtering FASTQ files for group %s of type (layout: %s, trimmed: %s)" % (group, layout, trim_type))

                    sample  = data[0]

                    tar_dir = osp.join(filtered_dir, group, layout,
                        "trimmed" if trim_type == "true" else "untrimmed")

                    mothur_configs.append({
                        "files": files,
                        "target_dir": tar_dir,

                        "group": group,

                        # NOTE: This is under the assumption that each group has the same primer.
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

def fastqc_check(file_, output_dir = None, threads = None):
    output_dir = output_dir or os.cwd()
    threads    = threads or settings.get("jobs")

    with ShellEnvironment(cwd = output_dir) as shell:
        shell("fastqc -q --threads {threads} {fastq_file} -o {out_dir}".format(
            threads = threads, out_dir = output_dir, fastq_file = file_))

def check_quality(data_dir = None, multiqc = False, *args, **kwargs):    
    data_dir = get_data_dir(NAME, data_dir)

    jobs  = kwargs.get("jobs", settings.get("jobs"))     
    
    logger.info("Checking quality of FASTQ files...")

    files = get_files(data_dir, "*.fastq")

    fastqc_dir = osp.join(data_dir, "fastqc")
    makedirs(fastqc_dir, exist_ok = True)

    with parallel.no_daemon_pool(processes = jobs) as pool:
        length   = len(files)

        function = build_fn(fastqc_check, output_dir = fastqc_dir, threads = jobs)
        results  = pool.imap(function, files)

        list(tq.tqdm(results, total = length))

    

def preprocess_data(data_dir = None, check = False, *args, **kwargs):
    data_dir = get_data_dir(NAME, data_dir)

    fastqc   = kwargs.get("fastqc",  False)
    multiqc  = kwargs.get("multiqc", False)

    if fastqc:
        check_quality(data_dir = data_dir, multiqc = multiqc)

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
        silva_seed_tax = silva_paths["taxonomy"], *args, **kwargs
    )

def check_data(data_dir = None):
    pass