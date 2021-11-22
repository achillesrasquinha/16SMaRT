import os.path as osp
import itertools

import tqdm as tq

from s3mart.config  import PATH
from s3mart import settings, __name__ as NAME

from bpyutils.util.ml      import get_data_dir
from bpyutils.util.array   import chunkify, group_by
from bpyutils.util._dict   import dict_from_list
from bpyutils.util.types   import lmap, lfilter, build_fn
from bpyutils.util.system  import (
    ShellEnvironment,
    makedirs,
    make_temp_dir, get_files, copy, write
)
from bpyutils.util.string    import get_random_str
from bpyutils.exception      import PopenError
from bpyutils._compat import itervalues, iteritems
from bpyutils import parallel, log

from s3mart.data.util import build_mothur_script

logger = log.get_logger(name = NAME)

CACHE  = PATH["CACHE"]

_DATA_DIR_NAME_TRIMMED = "trimmed"

def _mothur_trim_files(config, data_dir = None, *args, **kwargs):
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
        lmap(lambda x: osp.join(target_dir, "trimmed.%s" % x), target_types)
    )

    if not all(osp.exists(x) for x in itervalues(target_path)):
        with make_temp_dir(root_dir = CACHE) as tmp_dir:
            logger.info("[group %s] Copying FASTQ files %s for pre-processing at %s." % (group, files, tmp_dir))
            copy(*files, dest = tmp_dir)

            prefix = get_random_str()
            logger.info("[group %s] Using prefix for mothur: %s" % (group, prefix))

            logger.info("[group %s] Setting up directory %s for preprocessing" % (group, tmp_dir))

            # if layout == "single":
            #     fastq_file = osp.join(tmp_dir, "%s.file" % prefix)
            #     fastq_data = "\n".join(lmap(_get_fastq_file_line, files))
            #     write(fastq_file, fastq_data)

            #     config["fastq_file"] = fastq_file
            #     config["group"]      = osp.join(tmp_dir, "%s.group" % prefix)

            if trim_type == "false":
                oligos_file = osp.join(tmp_dir, "primers.oligos")
                oligos_data = "primer %s %s %s" % (primer_f, primer_r, group)
                write(oligos_file, oligos_data)

                config["oligos"] = oligos_file

            mothur_file = osp.join(tmp_dir, "script")
            build_mothur_script(
                template = "mothur/trim",
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

def trim_seqs(data_dir = None, data = [], *args, **kwargs):
    data_dir = get_data_dir(NAME, data_dir = data_dir)
    jobs     = kwargs.get("jobs", settings.get("jobs"))

    trimmed_dir = makedirs(osp.join(data_dir, _DATA_DIR_NAME_TRIMMED), exist_ok = True)
    logger.info("Storing trimmed FASTQ files at %s." % trimmed_dir)

    mothur_configs = [ ]

    study_group    = group_by(data, "group")

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

    if mothur_configs:
        logger.info("Filtering files using mothur using %s jobs...." % jobs)

        trim_chunks = settings.get("trim_chunks")

        for chunk in chunkify(mothur_configs, trim_chunks):
            with parallel.no_daemon_pool(processes = jobs) as pool:
                length    = len(mothur_configs)
                function_ = build_fn(_mothur_trim_files, *args, **kwargs)
                results   = pool.imap(function_, chunk)

                list(tq.tqdm(results, total = length))