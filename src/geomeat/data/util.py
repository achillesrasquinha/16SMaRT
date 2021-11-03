import os.path as osp

from bpyutils import log

from geomeat.config import PATH
from geomeat import __name__ as NAME

logger = log.get_logger(name = NAME)

def install_silva():
    path_silva_seed = osp.join(PATH["CACHE"], "silva.seed_v132.tgz")
    path_target     = osp.join(PATH["CACHE"], "silva")

    if not osp.exists(path_silva_seed):
        logger.info("Downloading SILVA seed v132 database...")

        download_file(CONST["url_silva_seed_132"], path_silva_seed)
        extract_all(path_silva_seed, path_target)

    path_silva_gold_bacteria = osp.join(PATH["CACHE"], "silva.gold.bacteria.zip")

    if not osp.exists(path_silva_gold_bacteria):
        logger.info("Downloading SILVA for chimera...")

        download_file(CONST["url_silva_gold_bacteria"], path_silva_gold_bacteria)
        extract_all(path_silva_gold_bacteria, path_target)

    return path_target