from rpy2.robjects.packages import importr

from s3mart.data.plots.util import save_plot, rarefy_pseq
from s3mart import settings

def plot(*args, **kwargs):
    pseq = importr("phyloseq")
    mothur_data = kwargs["mothur_data"]
    
    pseq_data   = pseq.import_mothur(
        mothur_shared_file  = mothur_data["shared"],
        # mothur_list_file    = mothur_data["list"],
        # mothur_tree_file    = mothur_data["tree"],
        mothur_constaxonomy_file = mothur_data["taxonomy"],
        # mothur_group_file   = mothur_data["group"],
        cutoff = settings.get("cutoff_level")
    )

    plot = pseq.plot_bar(pseq_data, fill = "Rank2")
    save_plot(plot, *args, **kwargs)
    
    pseq_data_rarefied = rarefy_pseq(pseq_data)
    plot = pseq.plot_bar(pseq_data_rarefied, fill = "Rank2")
    save_plot(plot, suffix = "rarefied", *args, **kwargs)