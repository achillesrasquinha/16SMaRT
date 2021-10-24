import os, os.path as osp
import csv
from functools import partial
import gzip
import itertools
from re import template

from jinja2 import Template

from geomeat.config  import PATH
from geomeat import const
from geomeat import __name__ as NAME

from bpyutils.util._dict   import dict_from_list, AutoDict
from bpyutils.util.types   import lmap, lfilter, auto_typecast
from bpyutils.util.system  import (
    ShellEnvironment,
    makedirs,
    popen, make_temp_dir, get_files, copy, write, read
)
from bpyutils.util.string  import get_random_str
from bpyutils.util.environ import getenv
from bpyutils._compat import iteritems
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

        data = lmap(lambda x: dict_from_list(header, lmap(auto_typecast, x)), reader)

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
            threads = const.N_JOBS, args = args, sra = sra), cwd = sra_dir)

        if gunzip:
            fastqs = lfilter(osp.isfile, map(lambda x: osp.join(sra_dir, x), os.listdir(sra_dir)))
            meta   = lmap(lambda x: dict(
                input_path  = x,
                output_path = "%s.gz" % x
            ), fastqs)
            
            with parallel.pool(processes = const.N_JOBS) as pool:
                pool.map(_gzip_file, meta)

def _fastq_quality_check(fastq_file, output_dir, fastqc_dir):
    with ShellEnvironment(cwd = output_dir) as shell:
        shell("fastqc -q --threads {threads} {fastq_file} -o {out_dir}".format(
            threads = const.N_JOBS, out_dir = fastqc_dir, fastq_file = fastq_file))

def get_data(data_dir = None, check = False, *args, **kwargs):
    data_dir =  get_data_dir(data_dir)
    data     = get_csv_data(sample = check)

    logger.info("Loading data into directory: %s" % data_dir)

    with parallel.no_daemon_pool(processes = const.N_JOBS) as pool:
        pool.map(
            partial(
                _fetch_sra_to_fastq, 
                **dict(output_dir = data_dir, gunzip = False)
            )
        , data)

    fastq_files = get_files(data_dir, "*.fastq")
    
    fastqc_dir  = osp.join(data_dir, "fastqc")
    makedirs(fastqc_dir, exist_ok = True)

    with parallel.no_daemon_pool(processes = const.N_JOBS) as pool:
        pool.map(
            partial(
                _fastq_quality_check,
                **dict(output_dir = data_dir, fastqc_dir = fastqc_dir)
            )
        , fastq_files)
    
    popen("multiqc {fastqc_dir}".format(fastqc_dir = fastqc_dir), cwd = data_dir)

def _render_mothur_script(*args, **kwargs):
    template_path = osp.join(PATH["DATA"], "templates", "mothur-trim")
    template = Template(read(template_path))
    
    rendered = template.render(*args, **kwargs)

    print(rendered)

    return rendered

def _get_fastq_file_line(fname):
    prefix, _ = osp.splitext(fname)
    return "%s %s" % (osp.basename(prefix), fname)

def _mothur_trim_files(config):
    files      = config.pop("files")
    target_dir = config.pop("target_dir")

    primer_f   = config.pop("primer_f")
    primer_r   = config.pop("primer_r")

    layout     = config.get("layout")
    trim_type  = config.get("trim_type")

    makedirs(target_dir, exist_ok = True)

    with make_temp_dir() as tmp_dir:
        copy(*files, dest = tmp_dir)

        prefix = get_random_str()

        if layout == "paired" and trim_type == "false":
            oligos_file = osp.join(tmp_dir, "meta.oligos")
            oligos_data = "primer %s %s" % (primer_f, primer_r)
            write(oligos_file, oligos_data)

            config["oligos"] = oligos_file

        if layout == "single":
            fastq_file  = osp.join(tmp_dir, "%s.file" % prefix)
            fastq_data  = "\n".join(lmap(_get_fastq_file_line, files))
            write(fastq_file, fastq_data)

            config["fastq_file"] = fastq_file

            config["group"] = osp.join(tmp_dir, "%s.group" % prefix)

        mothur_file   = osp.join(tmp_dir, "source")
        mothur_script = _render_mothur_script(inputdir = tmp_dir,
            prefix = prefix, processors = const.N_JOBS,
            qaverage = const.QUALITY_AVERAGE,
            maxambig = const.MAX_AMBIGUITY,
            maxhomop = const.MAX_HOMOPOLYMERS,
            **config
        )
        write(mothur_file, mothur_script)
        
        with ShellEnvironment(cwd = tmp_dir) as shell:
            shell("mothur %s" % mothur_file)

        choice = (".trim.contigs.trim.good.fasta", ".contigs.good.groups") \
            if layout == "paired" else (".trim.good.fasta", ".good.group") # group(s): are you f'king kiddin' me?
        
        copy(
            osp.join(tmp_dir, "%s%s" % (prefix, choice[0])),
            dest = osp.join(target_dir, "output.fasta")
        )

        copy(
            osp.join(tmp_dir, "%s%s" % (prefix, choice[1])),
            dest = osp.join(target_dir, "output.group")
        )

def _trim_primers(check = False, data_dir = None, force = True):
    data_dir = get_data_dir(data_dir)
    data     = get_csv_data(sample = check)

    preprop_dir = osp.join(data_dir, "preprop")
    makedirs(preprop_dir, exist_ok = True)

    mothur_configs = [ ]

    study_group = AutoDict(list)

    for d in data:
        study_id = d.pop("study_id")
        study_group[study_id].append(d)

    for study_id, data in iteritems(study_group):
        files  = []

        sample = data[0] # TODO: Check if fails.

        for layout, trim_type in itertools.product(("paired", "single"), ("true", "false")):
            filtered = lfilter(lambda x: x["layout"] == layout and x["trimmed"] == trim_type, data)
            
            for d in filtered:
                sra_id  = d["sra"]
                sra_dir = osp.join(data_dir, sra_id)
                fasta_files = get_files(sra_dir, "*.fastq")

                files += fasta_files

            tar_dir = osp.join(preprop_dir, study_id)

            mothur_configs.append({
                "files": files,
                "target_dir": tar_dir,
                # NOTE: This is under the assumption that each study has the same primer.
                "primer_f": sample["primer_f"],
                "primer_r": sample["primer_r"],
                "layout": layout, "trim_type": trim_type,
                "min_length": sample["min_length"],
                "max_length": sample["max_length"]
            })

    with parallel.no_daemon_pool(processes = const.N_JOBS) as pool:
        pool.map(_mothur_trim_files, mothur_configs)
    
def preprocess_data(data_dir = None, check = False, *args, **kwargs):
    data_dir = get_data_dir(data_dir)
    _trim_primers(data_dir = data_dir, check = check, *args, **kwargs)