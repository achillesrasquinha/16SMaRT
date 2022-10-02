import os.path as osp
import json

import tqdm as tq

from s3mart.config  import PATH
from s3mart import settings, __name__ as NAME

from bpyutils.util._dict   import autodict
from bpyutils.util._csv    import read as read_csv
from bpyutils.util.array   import group_by
from bpyutils.util.ml      import get_data_dir
from bpyutils.util.types   import build_fn
from bpyutils.util.string  import check_url, safe_decode
from bpyutils.util.system  import write, read, makedirs, get_files, remove
from bpyutils import parallel, log, request as req
from bpyutils._compat import iteritems, itervalues

from s3mart.data.functions import (
    get_input_data,
    get_fastq,
    check_quality,
    trim_seqs,
    merge_seqs,
    preprocess_seqs,
    build_plots,
    patch_tree_file,
    trim_seqs_fastp
)
from s3mart.data.util  import install_silva

logger = log.get_logger(name = NAME)

CACHE  = PATH["CACHE"]

def get_fastq_group(group, data_dir = None, *args, **kwargs):
    jobs = kwargs.get("jobs", settings.get("jobs"))
    fastqc = kwargs.pop("fastqc", True)

    with parallel.no_daemon_pool(processes = jobs) as pool:
        length = len(group)

        function = build_fn(get_fastq, data_dir = data_dir, fastqc = fastqc, *args, **kwargs)
        results  = pool.imap(function, group)

        list(tq.tqdm(results, total = length))

def check_data(input = None, data_dir = None, *args, **kwargs):
    data_dir, groups = get_input_data(input = input, data_dir = data_dir, *args, **kwargs)

    data_dir = get_data_dir(NAME, data_dir)

    logger.info("Attempting to check data integrity...")

    stats = autodict()

    global_total_sra = 0
    global_total_sra_available = 0

    n_groups = len(groups)

    for group, data in tq.tqdm(iteritems(groups), total = n_groups, desc = "Checking data integrity"):
        n_sra_success = 0
        total_sra = len(data)

        for d in data:
            sra_id = d["sra"]

            path_sra_fastq = osp.join(data_dir, sra_id)
            files = [file for file in get_files(path_sra_fastq, "*.fastq") \
                if "trimmed" not in file]

            if not files:
                logger.warning("No FASTQ files found for SRA ID: %s" % sra_id)
                stats["sra"][sra_id]["fastq"] = {
                    "status": "missing"
                }
            else:
                stats["sra"][sra_id]["fastq"] = {
                    "status": "available"
                }

                success = True

                if d["layout"] == "paired":
                    if len(files) != 2:
                        logger.warning("Invalid number of FASTQ files found for SRA ID: %s" % sra_id)
                        stats["sra"][sra_id]["fastq"] = {
                            "status": "invalid"
                        }
                        
                        success = False

                trimmed = False

                if any(["trimmed" in file for file in get_files(path_sra_fastq, "*.fastq")]):
                    trimmed = True

                if success:
                    stats["sra"][sra_id]["fastq"]["files"] = [{
                        "path": path,
                        "size": osp.getsize(path),
                        "trimmed": trimmed
                    } for path in files]
                    n_sra_success += 1

        stats["group"][group]["sra"] = {
            "total": total_sra,
            "available": n_sra_success
        }

        global_total_sra += total_sra
        global_total_sra_available += n_sra_success

    stats["global"] = {
        "sra": global_total_sra,
        "available": global_total_sra_available
    }

    write(osp.join(data_dir, "stats.json"), json.dumps(stats), force = True)

def get_data(input = None, data_dir = None, *args, **kwargs):
    data_dir, groups = get_input_data(input = input, data_dir = data_dir, *args, **kwargs)

    data_dir = get_data_dir(NAME, data_dir)
    jobs     = kwargs.get("jobs", settings.get("jobs"))

    logger.info("Data directory at %s." % data_dir)

    if groups:
        logger.info("Fetching FASTQ files...")
        with parallel.no_daemon_pool(processes = jobs) as pool:
            function = build_fn(get_fastq_group, data_dir = data_dir, *args, **kwargs)
            list(pool.imap(function, itervalues(groups)))

def preprocess_data(input = None, data_dir = None, *args, **kwargs):
    data_dir, data = get_input_data(input = input, data_dir = data_dir, *args, **kwargs)
    data_dir = get_data_dir(NAME, data_dir)

    minimal_output = kwargs.get("minimal_output", settings.get("minimal_output"))

    fastqc  = kwargs.get("fastqc",  True)
    multiqc = fastqc and kwargs.get("multiqc", True)

    if multiqc:
        check_quality(data_dir = data_dir, multiqc = multiqc, *args, **kwargs)
    else:
        logger.warning("MultiQC is disabled. Skipping quality check.")

    logger.info("Attempting to trim FASTQ files...")
    trim_seqs(data_dir = data_dir, data = data, *args, **kwargs)

    logger.info("Merging FASTQs...")
    merge_seqs(data_dir = data_dir)

    logger.info("Installing SILVA...")
    silva_paths = install_silva()

    logger.success("SILVA successfully downloaded at %s." % silva_paths)

    logger.info("Pre-processing FASTA + Group files...")
    preprocess_seqs(data_dir = data_dir,
        silva_seed = silva_paths["seed"], silva_gold = silva_paths["gold"],
        silva_seed_tax = silva_paths["taxonomy"], *args, **kwargs
    )

    if minimal_output:
        files = get_files(data_dir, "merged.*")
        remove(*files)

    logger.info("Render Plots...")
    render_plots(input = input, data_dir = data_dir, *args, **kwargs)

def render_plots(input = None, data_dir = None, *args, **kwargs):
    data_dir, data = get_input_data(input = input, data_dir = data_dir, *args, **kwargs)
    plot_dir  = osp.join(data_dir, "plots")
    makedirs(plot_dir, exist_ok = True)

    tree_file = osp.join(data_dir, "output.tre")
    list_file = osp.join(data_dir, "output.list")
    target_tree_file = osp.join(data_dir, "patched.tre")

    patch_tree_file(tree_file, list_file, target_tree_file)

    mothur_data    = {
        "tree":     target_tree_file,
        "list":     list_file,
        "shared":   osp.join(data_dir, "output.shared"),
        "taxonomy": osp.join(data_dir, "output.taxonomy"),
    }

    build_plots(data = data, mothur_data = mothur_data, target_dir = plot_dir)