from rpy2.robjects.packages import importr

from s3mart import settings

def plot(*args, **kwargs):
    pseq = importr("phyloseq")
    mothur_data = kwargs["mothur_data"]
    
    pseq_data   = pseq.import_mothur(
        mothur_shared_file  = mothur_data["shared"],
        mothur_list_file    = mothur_data["list"],
        mothur_group_file   = mothur_data["taxonomy"],
        cutoff = settings.get("cutoff_level")
    )

    print(pseq_data)