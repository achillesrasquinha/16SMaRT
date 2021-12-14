import os.path as osp

from rpy2.robjects.packages import importr
import rpy2.robjects as ro

from s3mart import settings

R = ro.r

def save_plot(plot, *args, **kwargs):
    target_file = kwargs.pop("target_file")
    suffix      = kwargs.get("suffix", None)
    plot_kwargs = kwargs.get("plot_kwargs", {})
    
    if suffix:
        dirname     = osp.dirname(target_file)
        basename    = osp.basename(target_file)
        prefix, ext = osp.splitext(basename)

        target_file = osp.join(dirname, "%s-%s%s" % (prefix, suffix, ext))
    
    # R.ggsave(target_file, **plot_kwargs)

    ggplotly    = importr("plotly")
    htmlwidgets = importr("htmlwidgets")
    
    plot        = ggplotly.ggplotly(plot)

    htmlwidgets.saveWidget(plot, file = target_file, libdir = "libs")

def rarefy_pseq(pseq_data):
    phyloseq  = importr("phyloseq")
    resampled = phyloseq.rarefy_even_depth(pseq_data, rngseed = settings.get("seed"))

    return resampled