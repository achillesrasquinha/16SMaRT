import os.path as osp

from jinja2 import Template

from bpyutils import log
from bpyutils.util.system  import read, extract_all
from bpyutils.util.request import download_file

from s3mart.config import PATH
from s3mart.const  import CONST
from s3mart import __name__ as NAME, settings

logger = log.get_logger(name = NAME)

def render_template(*args, **kwargs):
    script = kwargs["template"]

    template_path = osp.join(PATH["DATA"], "templates", script)
    template = Template(read(template_path))
    
    rendered = template.render(*args, **kwargs)

    return rendered

def install_silva():
    silva_version = str(settings.get("silva_version"))
    silva_version_str = "v%s" % silva_version.replace(".", "_")

    logger.info("Installing SILVA version v%s" % silva_version)

    path_silva_seed = osp.join(PATH["CACHE"], "silva.seed_%s.tgz" % silva_version_str)
    path_target     = osp.join(PATH["CACHE"], "silva")

    if not osp.exists(path_silva_seed):
        logger.info("Downloading SILVA seed v%s database..." % silva_version)

        download_file(CONST["url_silva_seed"].format(version = silva_version_str), path_silva_seed)
        extract_all(path_silva_seed, path_target)

    path_silva_gold_bacteria = osp.join(PATH["CACHE"], "silva.gold.bacteria.zip")

    if not osp.exists(path_silva_gold_bacteria):
        logger.info("Downloading SILVA for chimera...")

        download_file(CONST["url_silva_gold_bacteria"], path_silva_gold_bacteria)
        extract_all(path_silva_gold_bacteria, path_target)

    silva_paths = {
        "seed": osp.join(path_target, "silva.seed_%s.align" % silva_version_str),
        "gold": osp.join(path_target, "silva.gold.align"),
        "taxonomy": osp.join(path_target, "silva.seed_%s.tax" % silva_version_str)
    }

    logger.success("SILVA successfully downloaded at %s." % silva_paths)

    return silva_paths