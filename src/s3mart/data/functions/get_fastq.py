import os.path as osp
from s3mart import settings, __name__ as NAME

from s3mart.data.functions.check_quality import fastqc_check

from bpyutils.util.ml      import get_data_dir
from bpyutils.util.types   import build_fn
from bpyutils.util.system  import (
    ShellEnvironment,
    get_files,
    makedirs,
    remove
)
from bpyutils import log, parallel

logger = log.get_logger(name = NAME)

def get_fastq(meta, data_dir = None, *args, **kwargs):
    sra, layout = meta["sra"], meta["layout"]

    jobs        = kwargs.get("jobs", settings.get("jobs"))
    data_dir    = get_data_dir(NAME, data_dir)

    minimal_output = kwargs.get("minimal_output", settings.get("minimal_output"))
    
    fastqc      = kwargs.get("fastqc", True)

    fastqc_dir = osp.join(data_dir, "fastqc")
    makedirs(fastqc_dir, exist_ok = True)

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
            code = shell("parallel-fastq-dump --threads {threads} {args} {sra}".format(
                threads = jobs, args = args, sra = sra), cwd = sra_dir)

            if not code:
                logger.success("Successfully downloaded FASTQ file(s) for SRA %s." % sra)
            else:
                logger.error("Unable to download FASTQ file(s) for SRA %s." % sra)
        else:
            logger.warn("FASTQ file(s) for SRA %s already exist." % sra)

        fastq_files = get_files(sra_dir, "*.fastq")

        if fastqc:
            logger.info("Checking quality of FASTQ files...")

            with parallel.pool(processes = jobs) as pool:
                function_ = build_fn(fastqc_check, output_dir = fastqc_dir, threads = jobs)
                list(pool.imap(function_, fastq_files))

        if minimal_output:
            remove(path_sra)