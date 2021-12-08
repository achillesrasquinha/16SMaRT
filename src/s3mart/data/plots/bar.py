from rpy2.robjects.packages import importr

def plot(*args, **kwargs):
    pseq = importr("phyloseq")
    mothur_data = kwargs["mothur_data"]

    pseq_data   = pseq.import_mothur(
        # mothur_shared_file = mothur_data["shared"],
        mothur_list_file   = mothur_data["list"],
        mothur_tree_file   = mothur_data["tree"],
        mothur_constaxonomy_file = mothur_data["taxanomy"]
    )

    print(pseq_data)

    # pseq.plot_bar(pseq_data)