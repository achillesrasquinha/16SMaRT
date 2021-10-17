import os, os.path as osp
import csv
from functools import partial
import gzip
from posixpath import basename
import shutil

from geomeat.config  import PATH
from geomeat.const   import N_JOBS
from geomeat._compat import iteritems
from geomeat import __name__ as NAME

from bpyutils.util._dict   import dict_from_list, AutoDict, merge_dict
from bpyutils.util.types   import lmap, lfilter
from bpyutils.util.system  import ShellEnvironment, makedirs, popen, make_temp_dir, get_files
from bpyutils.util.environ import getenv
from bpyutils import parallel, log

logger  = log.get_logger(name = __name__)

_PREFIX = NAME.upper()

def get_data_dir(data_dir = None):
    data_dir = data_dir \
        or getenv("DATA_DIR", prefix = _PREFIX) \
        or osp.join(PATH["CACHE"], "data")

    makedirs(data_dir, exist_ok = True)

    return data_dir

def get_csv_data(sample = False):
    path_data = osp.join(PATH["DATA"], "sample.csv" if sample else "data.csv")
    data      = []
    
    with open(path_data) as f:
        reader = csv.reader(f)
        header = next(reader, None)

        data = lmap(lambda x: dict_from_list(header, x), reader)

    return data

def _gzip_file(meta):
    input_path, output_path = meta["input_path"], meta["output_path"]

    with open(input_path) as f_in:
        with gzip.open(output_path, "wb") as f_out:
            f_out.writelines(f_in)

def _fetch_sra_to_fastq(meta, output_dir, gunzip = True):
    sra, layout = meta["sra"], meta["layout"]

    with ShellEnvironment(cwd = output_dir) as shell:
        sra_dir = osp.join(output_dir, sra)
        shell("prefetch -O {out_dir} {sra}".format(out_dir = sra_dir, sra = sra))
        # shell("vdb-validate {dir}".format(dir = sra_dir))

        args = "--split-files" if layout == "paired" else "" 
        shell("fasterq-dump {args} {sra}".format(
            threads = N_JOBS, args = args, sra = sra), cwd = sra_dir)

        if gunzip:
            fastqs = lfilter(osp.isfile, map(lambda x: osp.join(sra_dir, x), os.listdir(sra_dir)))
            meta   = lmap(lambda x: dict(
                input_path  = x,
                output_path = "%s.gz" % x
            ), fastqs)
            
            with parallel.pool(processes = N_JOBS) as pool:
                pool.map(_gzip_file, meta)

def _fastq_quality_check(fastq_file, output_dir, fastqc_dir):
    with ShellEnvironment(cwd = output_dir) as shell:
        shell("fastqc -q --threads {threads} {fastq_file} -o {out_dir}".format(
            threads = N_JOBS, out_dir = fastqc_dir, fastq_file = fastq_file))

def get_data(data_dir = None, check = False, *args, **kwargs):
    data_dir =  get_data_dir(data_dir)
    data     = get_csv_data(sample = check)

    logger.info("Loading data into directory: %s" % data_dir)

    with parallel.no_daemon_pool(processes = N_JOBS) as pool:
        pool.map(
            partial(
                _fetch_sra_to_fastq, 
                **dict(output_dir = data_dir, gunzip = False)
            )
        , data)

    fastq_files = get_files(data_dir, "*.fastq")
    
    fastqc_dir  = osp.join(data_dir, "fastqc")
    makedirs(fastqc_dir, exist_ok = True)

    with parallel.no_daemon_pool(processes = N_JOBS) as pool:
        pool.map(
            partial(
                _fastq_quality_check,
                **dict(output_dir = data_dir, fastqc_dir = fastqc_dir)
            )
        , fastq_files)
    
    popen("multiqc {fastqc_dir}".format(fastqc_dir = fastqc_dir), cwd = data_dir)

def _fastq_to_qza(input_path, output_path, sample_data_type):
    with ShellEnvironment() as shell:
        shell("qiime tools import \
                --type 'SampleData[{sample_data_type}]' \
                --input-path  {input_path} \
                --output-path {output_path} \
                --input-format 'CasavaOneEightSingleLanePerSampleDirFmt'".format(
            input_path  = input_path,
            output_path = output_path,
            sample_data_type = sample_data_type
        ))

def _get_qime_compat_format(basename):
    if "_2" in basename:
        format_ = "_S001_L001_R2_001"
    else:
        format_ = "_S001_L001_R1_001"
    return format_

def _convert_to_qza(check = False, data_dir = None, force = False):
    data_dir    =  get_data_dir(data_dir)
    study_group = AutoDict(list)
    extension   = ".fastq.gz"

    data = get_csv_data(sample = check)

    for d in data:
        study_id = d.pop("study_id")
        study_group[study_id].append(d)

    for study_id, data in iteritems(study_group):
        for d in data:
            sra_id  = d["sra"]
            sra_dir = osp.join(data_dir, sra_id)
            sources = get_files(sra_dir, "*%s" % extension)

            output_path = osp.join(sra_dir, "%s.qza" % sra_id)

            with make_temp_dir() as tmp_dir:
                for source in sources:
                    basename = osp.basename(source)
                    format_  = _get_qime_compat_format(basename)

                    target_name = "%s%s%s" % (sra_id, format_, extension)

                    target   = osp.join(tmp_dir, target_name)

                    shutil.copy2(source, target)

                sample_data_type = "PairedEndSequencesWithQuality" if d["layout"] == "paired" else "SequencesWithQuality"

                if not osp.exists(output_path) or force:
                    _fastq_to_qza(tmp_dir, output_path, sample_data_type)

def _qiime_trim_qza(kwargs):
    with ShellEnvironment() as shell:
        shell("qiime cutadapt trim-paired \
                --i-demultiplexed-sequences {input_path} \
                --p-cores {jobs} \
                --p-front-f {primer_f} \
                --p-front-r {primer_r} \
                --p-no-indels \
                --o-trimmed-sequences {output_path}".format(**merge_dict(kwargs, dict(jobs = N_JOBS))))

        input_path  = kwargs["output_path"]
        basename, _ = osp.splitext(input_path)
        output_path = "%s.qzv" % basename

        shell("qiime demux summarize \
                --i-data {input_path} \
                --o-visualization {output_path}".format(
            input_path  = input_path,
            output_path = output_path
        ))

def _trim_primers(check = False, data_dir = None, force = True):
    data_dir = get_data_dir(data_dir)
    data     = get_csv_data(sample = check)

    qza_config = []

    for d in data:
        if d["layout"] == "paired":
            sra_id   = d["sra"]
            sra_dir  = osp.join(data_dir, sra_id)
            qza_file = get_files(sra_dir, "*.qza")[0]

            output_path = "%s_trimmed%s" % osp.splitext(qza_file)
            
            qza_config.append(dict(
                input_path  = qza_file,
                primer_f    = d["primer_f"],
                primer_r    = d["primer_r"],
                output_path = output_path
            ))

    with parallel.pool(processes = N_JOBS) as pool:
        pool.map(_qiime_trim_qza, qza_config)
    
def preprocess_data(data_dir = None, check = False, *args, **kwargs):
    data_dir = get_data_dir(data_dir)
    # _convert_to_qza(*args, **kwargs)
    # _trim_primers(*args, **kwargs)
    pass
