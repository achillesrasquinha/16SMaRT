import rpy2.robjects as ro
from rpy2.robjects.packages import importr

from bpyutils import log, parallel

from s3mart.data.plots.util import save_plot
from s3mart import settings

from s3mart import __name__ as NAME

logger = log.get_logger(name = NAME)

R = ro.r

def plot(*args, **kwargs):
    mothur_data = kwargs["mothur_data"]

    base    = importr("base")
    treeio  = importr("treeio")
    ggt     = importr("ggtree")

    logger.info("Loading tree...")

    tree_data = treeio.read_newick(mothur_data["tree"])

    logger.info("Rendering tree...")

    plot = ggt.ggtree(tree_data)
    save_plot(plot, *args, **kwargs)