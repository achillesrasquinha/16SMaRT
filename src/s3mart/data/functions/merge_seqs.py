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

    logger.success("Found %s files." % len(trimmed))

    if trimmed: #  and groups
        logger.info("Merging %s filter files." % len(trimmed))

        output_fasta = osp.join(data_dir, "merged.fasta")
        output_group = osp.join(data_dir, "merged.group")
        output_unique = osp.join(data_dir, "merged.unique.fasta")

        if not any(osp.exists(f) for f in (output_fasta,)) or force:
            logger.info("Converting files...")

            fasta_f  = open(output_fasta,  "w")
            group_f  = open(output_group,  "w")
            unique_f = open(output_unique, "w")

            unique_hits = {}

            for trimmed_file in tqdm(trimmed, total = len(trimmed), desc = "Converting..."):
                trimmed_f = open(trimmed_file, "r")

                skip_next  = False
                current_id = None

                try:
                    for line in trimmed_f:
                        if not line.startswith("+"):
                            if not skip_next:
                                if line.startswith("@"):
                                    line = line[1:]
                                    current_id = line

                                    fasta_f.write(">%s" % line)

                                    splits = line.split(" ")

                                    id_  = " ".join(splits[0:2])

                                    sra  = id_.split(".")[0]
                                    line = id_ + "\t" + sra

                                    group_f.write(line)
                                    group_f.write("\n")
                                else:
                                    fasta_f.write(line)

                                    hash_ = hash(line)

                                    if hash_ not in unique_hits:
                                        unique_hits[hash_] = 1
                                        
                                        unique_f.write(">%s" % current_id)
                                        unique_f.write(line)
                                    else:
                                        unique_hits[hash_] += 1
                            else:
                                skip_next = False
                        else:
                            skip_next = True
                except Exception as e:
                    fasta_f.close()
                    trimmed_f.close()
                    group_f.close()
                    unique_f.close()

                    raise e

            logger.success("Group file written to: %s" % output_group)
    else:
        logger.warn("No files found to merge.")

    if success and minimal_output:
        trimmed_dir = osp.join(data_dir, _DATA_DIR_NAME_TRIMMED)
        remove(trimmed_dir, recursive = True)