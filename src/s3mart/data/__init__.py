import os.path as osp

<<<<<<< HEAD
<<<<<<< HEAD
import tqdm as tq

from s3mart.config  import PATH
from s3mart import settings, __name__ as NAME

from bpyutils.util._csv    import read as read_csv
from bpyutils.util.ml      import get_data_dir
from bpyutils.util.types   import build_fn
from bpyutils.util.string  import check_url, safe_decode
from bpyutils.util.system  import write, read, makedirs, get_files, remove
from bpyutils import parallel, log, request as req
from bpyutils._compat import iteritems

from s3mart.data.functions import (
    get_fastq,
    check_quality,
    trim_seqs,
    merge_seqs,
    preprocess_seqs,
    build_plots,
    patch_tree_file
)
from s3mart.data.util  import install_silva

logger = log.get_logger(name = NAME)

CACHE  = PATH["CACHE"]

def get_input_data(input = None, data_dir = None, *args, **kwargs):
    data_dir = get_data_dir(NAME, data_dir)

    if input:
        if check_url(input, raise_err = False):
            response = req.get(input)
            response.raise_for_status()

            content  = response.content

            input    = osp.join(data_dir, "input.csv")
            write(input, safe_decode(content))
        
        input = osp.abspath(input)

        if osp.isdir(input):
            data_dir = input
    else:
        input = osp.join(PATH["DATA"], "sample.csv")

    data = []

    if osp.isfile(input):
        data = read_csv(input)

    return data_dir, data

def get_data(input = None, data_dir = None, *args, **kwargs):
    data_dir, data = get_input_data(input = input, data_dir = data_dir, *args, **kwargs)

    data_dir = get_data_dir(NAME, data_dir)
    jobs     = kwargs.get("jobs", settings.get("jobs"))

    fastqc   = kwargs.get("fastqc", True)

    logger.info("Data directory at %s." % data_dir)

    if data:
        logger.info("Fetching FASTQ files...")
        with parallel.no_daemon_pool(processes = jobs) as pool:
            length   = len(data)

            function = build_fn(get_fastq, data_dir = data_dir, fastqc = fastqc, *args, **kwargs)
            results  = pool.imap(function, data)

            list(tq.tqdm(results, total = length))

def preprocess_data(input = None, data_dir = None, *args, **kwargs):
    data_dir, data = get_input_data(input = input, data_dir = data_dir, *args, **kwargs)
    data_dir = get_data_dir(NAME, data_dir)

    minimal_output = kwargs.get("minimal_output", settings.get("minimal_output"))

    # fastqc   = kwargs.get("fastqc",  True)
    multiqc  = kwargs.get("multiqc", True)

    if multiqc:
        check_quality(data_dir = data_dir, fastqc = False, multiqc = multiqc, *args, **kwargs)

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
=======
=======
>>>>>>> template/master
from s3mart.config import PATH
from s3mart import __name__ as NAME

from bpyutils.util.environ import getenv
from bpyutils.util.system  import makedirs

_PREFIX = NAME.upper()

def get_data_dir(data_dir = None):
    data_dir = data_dir \
        or getenv("DATA_DIR", prefix = _PREFIX) \
        or osp.join(PATH["CACHE"], "data")

    makedirs(data_dir, exist_ok = True)

    return data_dir

def get_data(data_dir = None, check = False, *args, **kwargs):
    data_dir = get_data_dir(data_dir)
    # do something ...

def preprocess_data(data_dir = None, check = False, *args, **kwargs):
    data_dir = get_data_dir(data_dir)
<<<<<<< HEAD
    # do something ...
>>>>>>> template/master
=======
    # do something ...
>>>>>>> template/master
