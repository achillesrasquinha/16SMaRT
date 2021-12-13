import os, os.path as osp

from bpyutils.util.system  import makedirs
from bpyutils.util.imports import import_handler
from bpyutils import log

from s3mart import __name__ as NAME, settings

logger = log.get_logger(name = NAME)

PLOTS = [
    "world_map",
    "abundance_bar",
    "alpha_diversity",
    "beta_diversity",
    "phylo_tree"
]

def _import_and_plot(plot_name, *args, **kwargs):
    logger.info("Plotting %s..." % plot_name)
    target_dir = kwargs["target_dir"]

    plot_fn = import_handler("s3mart.data.plots.%s.plot" % plot_name)
    plot_fn(target_file = osp.join(target_dir, "%s.html") % plot_name, *args, **kwargs)

def build_plots(*args, **kwargs):
    target_dir = osp.abspath(kwargs.get("target_dir", os.getcwd()))
    makedirs(target_dir, exist_ok = True)

    logger.info("Building Plots to %s..." % target_dir)

    # with parallel.no_daemon_pool(processes = jobs) as pool:
    #     length    = len(PLOTS)
    #     function_ = build_fn(_import_and_plot, *args, **kwargs)

    #     list(tq.tqdm(pool.imap(function_, PLOTS), total = length))

    for plot_name in PLOTS:
        _import_and_plot(plot_name, *args, **kwargs)