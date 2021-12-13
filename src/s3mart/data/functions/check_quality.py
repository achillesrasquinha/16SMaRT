import os, os.path as osp

from s3mart import settings, __name__ as NAME

from bpyutils.util.ml      import get_data_dir
from bpyutils.util.system  import (
    ShellEnvironment, popen,
    makedirs,
    get_files,
    remove
)
from bpyutils import log

logger = log.get_logger(name = NAME)

def fastqc_check(file_, output_dir = None, threads = None):
    output_dir = output_dir or os.cwd()
    threads    = threads or settings.get("jobs")

    basename   = osp.basename(file_)
    prefix, _  = osp.splitext(basename)

    if not get_files(output_dir, "%s_fastqc.*" % prefix):
        with ShellEnvironment(cwd = output_dir) as shell:
            shell("fastqc -q --threads {threads} {fastq_file} -o {out_dir}".format(
                threads = threads, out_dir = output_dir, fastq_file = file_))
    else:
        logger.warn("FASTQC for file %s already exists." % file_)

def check_quality(data_dir = None, multiqc = False, **kwargs):    
    data_dir = get_data_dir(NAME, data_dir)
    # jobs     = kwargs.get("jobs", settings.get("jobs"))

    minimal_output = kwargs.get("minimal_output", settings.get("minimal_output"))
    
    logger.info("Checking quality of FASTQ files...")

    # files    = get_files(data_dir, "*.fastq")

    fastqc_dir = osp.join(data_dir, "fastqc")
    makedirs(fastqc_dir, exist_ok = True)

    # with parallel.no_daemon_pool(processes = jobs) as pool:
    #     length   = len(files)

    #     function = build_fn(fastqc_check, output_dir = fastqc_dir, threads = jobs)
    #     results  = pool.imap(function, files)

    #     list(tq.tqdm(results, total = length))

    if multiqc:
        logger.info("Running MultiQC...")

        popen("multiqc {fastqc_dir}".format(fastqc_dir = fastqc_dir), cwd = data_dir)

    if minimal_output:
        remove(fastqc_dir, recursive = True)