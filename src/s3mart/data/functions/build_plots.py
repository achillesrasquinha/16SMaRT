from bpyutils.util.imports import import_handler
from bpyutils import log

from s3mart import __name__ as NAME

logger = log.get_logger(name = NAME)

PLOTS = [
    "geomap"
]

def build_plots(data, *args, **kwargs):
    logger.info("Building Plots...")

    for plot in PLOTS:
        logger.info("Plotting %s..." % plot)
        plot_fn = import_handler("s3mart.data.plots.%s.plot" % plot)
        plot_fn(data)