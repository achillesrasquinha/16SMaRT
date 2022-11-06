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

    logger.info("Finding files in directory: %s" % data_dir)
    
    trimmed = get_files(data_dir, "*%s.fastq" % _FILENAME_TRIMMED)
    groups  = get_files(data_dir, "%s.group" % _FILENAME_TRIMMED)

    logger.success("Found %s files." % len(trimmed))

    if trimmed: #  and groups
        logger.info("Merging %s filter and %s group files." % (len(trimmed), len(groups)))

        output_fastq = osp.join(data_dir, "merged.fastq")
        output_fasta = osp.join(data_dir, "merged.fasta")
        output_group = osp.join(data_dir, "merged.group")

        if not any(osp.exists(f) for f in (output_fasta,)) or force:
            with make_temp_dir(root_dir = CACHE) as tmp_dir:
                # mothur_file = osp.join(tmp_dir, "script")
                # build_mothur_script(
                #     template     = "mothur/merge", 
                #     output       = mothur_file,
                #     input_fastas = trimmed,
                #     input_groups = groups,
                #     output_fasta = output_fasta,
                #     # output_group = output_group
                # )

                with ShellEnvironment(cwd = tmp_dir) as shell:
                    # code = shell("mothur %s" % mothur_file)
                    for f in tqdm(trimmed, total = len(trimmed), desc = "Merging..."):
                        code = shell("cat %s >> %s" % (f, output_fastq))

                    logger.info("Converting fastq to fasta...")
                    code = shell("sed -n '1~2s/^@/>/p;2~4p' %s > %s" % (output_fastq, output_fasta))

                    logger.info("Writing group file...")

                    with open(output_group, "w") as group_f:
                        with open(output_fasta, "r") as fasta_f:
                            for line in tqdm(fasta_f, total = word_count(output_fasta), desc = "Writing group file..."):
                                if line.startswith(">"):
                                    splits = line.split(" ")
                                    splits = lfilter(lambda x: "length=" not in x, splits)

                                    id_  = " ".join(splits)

                                    id_  = id_[1:]
                                    sra  = id_.split(".")[0]
                                    line = id_ + "\t" + sra

                                    group_f.write(line)
                                    group_f.write("\n")

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