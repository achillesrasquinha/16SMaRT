import os, os.path as osp
import itertools

import tqdm as tq

from s3mart.config  import PATH
from s3mart import settings, __name__ as NAME

from bpyutils.util.ml      import get_data_dir
from bpyutils.util.array   import chunkify
from bpyutils.util._dict   import dict_from_list
from bpyutils.util.types   import lmap, lfilter, build_fn
from bpyutils.util.system  import (
    ShellEnvironment,
    makedirs,
    make_temp_dir, get_files, copy, write,
    remove,
    read
)
from bpyutils.util.string    import get_random_str
from bpyutils.exception      import PopenError
from bpyutils._compat import itervalues, iteritems
from bpyutils import parallel, log

from s3mart.data.functions.get_input_data import get_input_data

logger = log.get_logger(name = NAME)

CACHE  = PATH["CACHE"]

_DATA_DIR_NAME_TRIMMED = "trimmed"
_FILENAME_TRIMMED      = "trimmed"

def _get_fastq_file_line(fname):
    prefix    = osp.basename(fname)
    prefix, _ = osp.splitext(prefix)

    return "%s %s" % (prefix, fname)

def _mothur_trim_files(config, data_dir = None, **kwargs):
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

    root_tmp_dir = kwargs.get("root_tmp_dir", CACHE)

    success    = False

    minimal_output = kwargs.get("minimal_output", settings.get("minimal_output"))

    target_types = ("fasta", "group", "summary")
    target_path  = dict_from_list(
        target_types,
        lmap(lambda x: osp.join(target_dir, "%s.%s" % (_FILENAME_TRIMMED, x)), target_types)
    )

    if not all(osp.exists(x) for x in itervalues(target_path)):
        with make_temp_dir(root_dir = root_tmp_dir) as tmp_dir:
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
                config["group"] = osp.join(tmp_dir, "%s.group" % prefix)

            if layout == "paired":
                pass
                # config["forward_fastq"] = osp.join(tmp_dir, "%s_1.fastq" % prefix)
                # config["reverse_fastq"] = osp.join(tmp_dir, "%s_2.fastq" % prefix)

            # if trim_type == "false":
            #     primers_fasta_file = osp.join(tmp_dir, "primers.fasta")
            #     primers_fasta_data = ">forward_primer\n%s\n>reverse_primer\n%s" % (primer_f, primer_r)
            #     write(primers_fasta_file, primers_fasta_data)

            #     print(read(primers_fasta_file))

            #     config["primers_fasta_file"] = primers_fasta_file

            # mothur_file = osp.join(tmp_dir, "script")
            
            # build_mothur_script(
            #     template = "mothur/trim",
            #     output   = mothur_file,
            #     inputdir = tmp_dir, prefix = prefix, processors = jobs,
            #     qaverage = settings.get("quality_average"),
            #     maxambig = settings.get("maximum_ambiguity"),
            #     maxhomop = settings.get("maximum_homopolymers"),
            #     pdiffs   = settings.get("primer_difference"),
            #     proccessors = jobs,
            #     **config
            # )

            logger.info("[group %s] Running fastp..." % group)

            try:
                with ShellEnvironment(cwd = tmp_dir) as shell:
                    if layout == "single":
                        config_single = read(fastq_file)
                        config_single = config_single.split("\n")
                        
                        config_single = lmap(lambda x: x.split(" "), config_single)
                        
                        for cfg in config_single:
                            fasta_file = cfg[1]
                            fasta_dir  = osp.dirname(fasta_file)
                            fasta_name = osp.basename(fasta_file)
                            sra_name   = osp.splitext(fasta_name)[0]

                            shell("fastp -i {fasta_file} -e {quality_average} -yY {maxhomop} -n {maxambig} -o {trimmed} -w {jobs}".format(
                                fasta_file = fasta_file,

                                quality_average = settings.get("quality_average"),
                                maxhomop = settings.get("maximum_homopolymers"),
                                maxambig = settings.get("maximum_ambiguity"),

                                trimmed = osp.join(fasta_dir, "%s.trimmed.fastq" % sra_name),
                                jobs = min(jobs, 16)
                            ))

                    if layout == "paired":
                        for file in files:
                            file_dir  = osp.dirname(file)
                            file_name = osp.basename(file)

                            sra_name  = osp.splitext(file_name)[0]
                            sra_name  = sra_name.split("_")[0]

                            if "1.fastq" in file_name:
                                forward = file
                                reverse = osp.join(file_dir, "%s_2.fastq" % sra_name)

                                shell("fastp -i {forward} -I {reverse} -e {quality_average} -n {maxambig} -yY {maxhomop} -m --merged_out {trimmed} -w {jobs}".format(
                                    forward = forward, 
                                    reverse = reverse,

                                    quality_average = settings.get("quality_average"),
                                    maxhomop = settings.get("maximum_homopolymers"),
                                    maxambig = settings.get("maximum_ambiguity"),

                                    trimmed = osp.join(file_dir, "%s.trimmed.fastq" % sra_name),
                                    jobs = min(jobs, 16)
                                ))

                        logger.info("[group %s] Successfully copied filtered files at %s." % (group, target_dir))
                
                        success = True
            except PopenError as e:
                logger.error("[group %s] Unable to filter files. Error: %s" % (group, e))
    else:
        logger.warn("[group %s] Filtered files already exists." % group)

    if success and minimal_output:
        remove(*files)

def trim_seqs_fastp(data_dir = None, data = [], *args, **kwargs):
    input = kwargs.pop("input", None)

    data_dir, data_input = get_input_data(input = input, data_dir = data_dir, *args, **kwargs)

    if not data:
        data = data_input

    jobs = kwargs.get("jobs", settings.get("jobs"))

    trimmed_dir = makedirs(osp.join(data_dir, _DATA_DIR_NAME_TRIMMED), exist_ok = True)
    logger.info("Storing trimmed FASTQ files at %s." % trimmed_dir)

    mothur_configs = []
    
    for group, values in iteritems(data):
        for i, _ in enumerate(values):
            values[i]["group"] = group
        data[group] = values

    study_group = data

    logger.info("Found %s groups." % len(study_group))
    logger.info("Building configs for fastp...")

    for layout, trim_type in itertools.product(("paired", "single"), ("true", "false")):
        for group, data in iteritems(study_group):
            if len(data):
                filtered = lfilter(lambda x: x["layout"] == layout and x["trimmed"] == trim_type, data)
                files = []
                
                for d in filtered:
                    sra_id  = d["sra"]
                    sra_dir = osp.join(data_dir, sra_id)

                    logger.info("Searching FASTQ files in directory %s..." % sra_dir)

                    fasta_files = get_files(sra_dir, "*.fastq")
                    fasta_files_map = dict_from_list(fasta_files)
                    
                    for fasta_file in fasta_files:
                        trimmed = osp.join(sra_dir, "%s.trimmed.fastq" % sra_id)
                        if trimmed not in fasta_files_map:
                            files.append(fasta_file)
                        else:
                            logger.warn("SRA %s already trimmed." % sra_id)

                if files:
                    logger.info("Filtering FASTQ files for group %s of type (layout: %s, trimmed: %s)" % (group, layout, trim_type))

                    sample  = data[0]

                    tar_dir = osp.join(trimmed_dir, group, layout,
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
                else:
                    logger.warn("No FASTQ files found for group %s of type (layout: %s, trimmed: %s)" % (group, layout, trim_type))
            else:
                logger.warn("No FASTQ files found for group %s" % group)

    if mothur_configs:
        logger.info("Filtering files using mothur using %s jobs...." % jobs)

        trim_chunks = settings.get("trim_chunks")

        for chunk in chunkify(mothur_configs, trim_chunks):
            with parallel.no_daemon_pool(processes = jobs) as pool:
                length    = len(mothur_configs)
                function_ = build_fn(_mothur_trim_files, *args, **kwargs)
                results   = pool.imap(function_, chunk)

                list(tq.tqdm(results, total = length))