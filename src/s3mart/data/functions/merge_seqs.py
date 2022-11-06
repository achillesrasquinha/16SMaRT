import os.path as osp

from tqdm import tqdm

from s3mart.config  import PATH
from s3mart import __name__ as NAME

from bpyutils.util.ml      import get_data_dir
from bpyutils.util.system  import (
    ShellEnvironment,
    make_temp_dir, get_files, move,
    remove,
    wc as word_count
)
from bpyutils.util.types import lfilter
from bpyutils import log

from s3mart.data.functions.trim_seqs import _FILENAME_TRIMMED, _DATA_DIR_NAME_TRIMMED
from s3mart.data.util import build_mothur_script
from s3mart import settings

logger = log.get_logger(name = NAME)

CACHE  = PATH["CACHE"]

def merge_seqs(data_dir = None, force = False, **kwargs):
    minimal_output = kwargs.get("minimal_output", settings.get("minimal_output"))

    success  = False

    data_dir = get_data_dir(NAME, data_dir = data_dir)

    skip_fasta = kwargs.get("skip_fasta", False)
    skip_fastq = kwargs.get("skip_fastq", False)

    if not skip_fasta:
        logger.info("Finding files in directory: %s" % data_dir)
        
        trimmed = get_files(data_dir, "*%s.fastq" % _FILENAME_TRIMMED)

        logger.success("Found %s files." % len(trimmed))
    else:
        trimmed = []

    if trimmed or skip_fasta or skip_fastq: #  and groups
        logger.info("Merging %s filter files." % len(trimmed))

        output_fastq = osp.join(data_dir, "merged.fastq")
        output_fasta = osp.join(data_dir, "merged.fasta")
        output_group = osp.join(data_dir, "merged.group")

        if not any(osp.exists(f) for f in (output_fasta,)) or force:
            with make_temp_dir(root_dir = CACHE) as tmp_dir:
                with ShellEnvironment(cwd = tmp_dir) as shell:
                    if not skip_fasta:
                        for f in tqdm(trimmed, total = len(trimmed), desc = "Merging..."):
                            code = shell("cat %s >> %s" % (f, output_fastq))
                    else:
                        logger.info("Skipping fasta file.")
                            
                    if not skip_fastq:
                        logger.info("Converting fastq to fasta...")
                        code = shell("sed -n '1~2s/^@/>/p;2~4p' %s | pv > %s" % (output_fastq, output_fasta))
                    else:
                        logger.info("Skipping fastq file.")

                    logger.info("Writing group file...")

                    with tqdm(total = osp.getsize(output_fasta), desc = "Writing group file...") as pbar:
                        with open(output_group, "w") as group_f:
                            with open(output_fasta, "r") as fasta_f:
                                for line in fasta_f:
                                    if line.startswith(">"):
                                        splits = line.split(" ")
                                        splits = lfilter(lambda x: "length=" not in x, splits)

                                        id_  = " ".join(splits)

                                        id_  = id_[1:]
                                        sra  = id_.split(".")[0]
                                        line = id_ + "\t" + sra

                                        group_f.write(line)
                                        group_f.write("\n")

                                    pbar.update(len(line))

                    logger.success("Group file written to: %s" % output_group)

                    if not code:
                    #     # HACK: weird hack around failure of mothur detecting output for merge.files
                        # merged_fasta = get_files(data_dir, "merged.fasta")
                        # merged_group = get_files(data_dir, "merged.group")

                        # move(*merged_fasta, dest = output_fasta)
                        # move(*merged_group, dest = output_group)

                        logger.success("Successfully merged.")

                        success = True
                    else:
                        logger.error("Error merging files.")
    else:
        logger.warn("No files found to merge.")

    if success and minimal_output:
        trimmed_dir = osp.join(data_dir, _DATA_DIR_NAME_TRIMMED)
        remove(trimmed_dir, recursive = True)