import os.path as osp
import csv
from glob import glob
from functools import partial

from geomeat.config import PATH
from bpyutils.util.types  import lmap
from bpyutils.util.system import ShellEnvironment, makedirs, popen
from geomeat.const import N_JOBS
from bpyutils import parallel

def _fetch_sra_to_fastq(meta, output_dir):
    sra, layout = meta["sra"], meta["layout"]

    with ShellEnvironment(cwd = output_dir) as shell:
        shell("prefetch {sra}".format(sra = sra))
        shell("vdb-validate {dir}".format(dir = osp.join(output_dir, sra)))

        args = "--split-files" if layout == "paired" else "" 
        shell("fasterq-dump --threads {threads} --progress {args} {sra}".format(
            threads = N_JOBS, args = args, sra = sra))

def _fastq_quality_check(fastq_file, output_dir, fastqc_dir):
    with ShellEnvironment(cwd = output_dir) as shell:
        shell("fastqc {fastq_file} -o {out_dir}".format(out_dir = fastqc_dir,
            fastq_file = fastq_file))

def get_data(check = False, data_dir = None):
    path_data  = osp.join(PATH["DATA"], "sample.csv" if check else "data.csv")
    output_dir = osp.abspath(data_dir or osp.join(PATH["CACHE"], "data"))
    makedirs(output_dir, exist_ok = True)
    
    with open(path_data) as f:
        reader = csv.reader(f)
        next(reader, None)

        data = lmap(lambda x: dict(sra = x[0], layout = x[1]), reader)

        with parallel.no_daemon_pool(processes = N_JOBS) as pool:
            pool.map(
                partial(
                    _fetch_sra_to_fastq, 
                    **dict(output_dir = output_dir)
                )
            , data)

    fastq_files = glob("%s/*.fastq" % output_dir)

    fastqc_dir  = osp.join(output_dir, "fastqc")
    makedirs(fastqc_dir, exist_ok = True)

    with parallel.no_daemon_pool(processes = N_JOBS) as pool:
        pool.map(
            partial(
                _fastq_quality_check,
                **dict(output_dir = output_dir, fastqc_dir = fastqc_dir)
            )
        , fastq_files)
    
    popen("multiqc {fastqc_dir}".format(fastqc_dir = fastqc_dir), cwd = output_dir)