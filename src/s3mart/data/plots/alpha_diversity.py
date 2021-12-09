from rpy2.robjects.lib import ggplot2 as gg
from rpy2.robjects.packages import importr

from bpyutils.util.array import sequencify

from s3mart.data.plots.util import save_plot, normalize_pseq
from s3mart import settings

def plot(*args, **kwargs):
    target_file = kwargs["target_file"]
    mothur_data = kwargs["mothur_data"]

    pseq = importr("phyloseq")
    
    pseq_data   = pseq.import_mothur(
        mothur_shared_file  = mothur_data["shared"],
        mothur_list_file    = mothur_data["list"],
        # mothur_tree_file    = mothur_data["tree"],
        mothur_constaxonomy_file = mothur_data["taxonomy"],
        # mothur_group_file   = mothur_data["group"],
        cutoff = settings.get("cutoff_level")
    )

    pseq_data_resampled = normalize_pseq(pseq_data)
    
    plot_kwargs = { "width": 10, "height": 8 }

    kwargs["plot_kwargs"] = plot_kwargs
    
    ggplot = pseq.plot_richness(pseq_data)
    save_plot(ggplot, *args, **kwargs)

    ggplot = pseq.plot_richness(pseq_data_resampled)
    save_plot(ggplot, suffix = "resampled", *args, **kwargs)