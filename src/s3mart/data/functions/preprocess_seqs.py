import os.path as osp

from s3mart.config  import PATH
from s3mart import settings, __name__ as NAME

from bpyutils.util.array   import sequencify
from bpyutils.util.ml      import get_data_dir
from bpyutils.util.system  import (
    ShellEnvironment, makedirs,
    make_temp_dir, copy, move,
    makedirs
)
from bpyutils import log

from s3mart.data.util import build_mothur_script
from s3mart.data.util  import install_silva

logger = log.get_logger(name = NAME)

CACHE  = PATH["CACHE"]

def preprocess_seqs(data_dir = None, **kwargs):
    logger.info("Installing SILVA...")
    silva_paths = install_silva()

    logger.success("SILVA successfully downloaded at %s." % silva_paths)

    logger.info("Pre-processing FASTA + Group files...")

    data_dir = get_data_dir(NAME, data_dir)
    jobs     = kwargs.get("jobs", settings.get("jobs"))

    merged_fasta = osp.join(data_dir, "merged.fasta")
    
    merged_group = osp.join(data_dir, "merged.group")

    silva_seed = kwargs.get("silva_seed", silva_paths["seed"])
    silva_gold = kwargs.get("silva_gold", silva_paths["gold"])
    silva_seed_tax = kwargs.get("silva_seed_tax", silva_paths["taxonomy"])

    cutoff_level   = settings.get("cutoff_level")

    files = (merged_fasta, merged_group, silva_seed, silva_gold, silva_seed_tax)
    target_files = [{
        "source": "merged.unique.good.unique.precluster.pick.pick.phylip.tre",
        "target": osp.join(data_dir, "output.tre")
    }, {
        "source": "merged.unique.good.unique.precluster.pick.pick.opti_mcc.%s.cons.taxonomy" % cutoff_level,
        "target": osp.join(data_dir, "output.taxonomy"),
    }, {
        "source": "merged.unique.good.unique.precluster.pick.count_table",
        "target": osp.join(data_dir, "output.count_table")
    }, {
        "source": "merged.unique.good.unique.precluster.pick.pick.opti_mcc.list",
        "target": osp.join(data_dir, "output.list")
    }, {
        "source": "merged.unique.good.unique.precluster.pick.pick.opti_mcc.shared",
        "target": osp.join(data_dir, "output.shared")
    }]

    logger.info("Preprocessing sequences...")

    # with make_temp_dir(root_dir = CACHE) as tmp_dir:
    # tmp_dir = make_temp_dir(root_dir = CACHE)
    # print(tmp_dir)
    tmp_dir = "/work/s3mart"
    makedirs(tmp_dir, exist_ok = True)

    copy(*files, dest = tmp_dir)

    silva_seed_splitext = osp.splitext(osp.basename(silva_seed))

    filter_taxonomy = settings.get("filter_taxonomy")
    if not isinstance(filter_taxonomy, (list, tuple)):
        filter_taxonomy = eval(filter_taxonomy)
        filter_taxonomy = sequencify(filter_taxonomy)
        
    mothur_file = osp.join(tmp_dir, "script")
    build_mothur_script(
        template = "mothur/preprocess",
        output   = mothur_file,
        merged_fasta = osp.join(tmp_dir, osp.basename(merged_fasta)),
        merged_group = osp.join(tmp_dir, osp.basename(merged_group)),

        silva_seed       = osp.join(tmp_dir, osp.basename(silva_seed)),
        silva_seed_start = settings.get("silva_pcr_start"),
        silva_seed_end   = settings.get("silva_pcr_end"),

        silva_pcr   = osp.join(tmp_dir, "%s.pcr%s" % (silva_seed_splitext[0], silva_seed_splitext[1])),
        
        silva_seed_tax   = osp.join(tmp_dir, osp.basename(silva_seed_tax)),
        silva_gold       = osp.join(tmp_dir, osp.basename(silva_gold)),

        maxhomop              = settings.get("maximum_homopolymers"),
        classification_cutoff = settings.get("classification_cutoff"),
        filter_taxonomy       = filter_taxonomy,
        taxonomy_level        = settings.get("taxonomy_level"),
        cutoff_level          = settings.get("cutoff_level"),

        processors            = jobs
    )

    with ShellEnvironment(cwd = tmp_dir) as shell:
        code = shell("mothur %s" % mothur_file)

        if not code:
            makedirs(data_dir, exist_ok = True)

            for tar_file in target_files:
                source = osp.join(tmp_dir, tar_file["source"])
                target = tar_file["target"]

                move(source, dest = target)

            logger.success("Successfully preprocessed files.")
        else:
            logger.error("Error merging files.")