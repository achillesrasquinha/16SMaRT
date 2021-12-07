import tqdm as tq

from bpyutils.util.types   import build_fn
from bpyutils.util.imports import import_handler
from bpyutils import log, parallel

from s3mart import __name__ as NAME, settings

logger = log.get_logger(name = NAME)

PLOTS = [
    "geomap"
]

def _import_and_plot(plot_name, *args, **kwargs):
    logger.info("Plotting %s..." % plot_name)

    plot_fn = import_handler("s3mart.data.plots.%s.plot" % plot_name)
    plot_fn(*args, **kwargs)

def build_plots(*args, **kwargs):
    jobs = kwargs.get("jobs", settings.get("jobs"))

    logger.info("Building Plots...")

    

    with parallel.no_daemon_pool(processes = jobs) as pool:
        length    = len(PLOTS)
        function_ = build_fn(_import_and_plot, *args, **kwargs)

        list(tq.tqdm(pool.imap(function_, PLOTS), total = length))
