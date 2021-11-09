import os.path as osp

from geomeat.__attr__ import __name__ as NAME
from geomeat.const import CONST

from bpyutils.config      import get_config_path
from bpyutils.util.system  import pardir
from bpyutils.util.environ import getenv

PATH = dict()

PATH["BASE"]  = pardir(__file__, 1)
PATH["DATA"]  = osp.join(PATH["BASE"], "data")
PATH["CACHE"] = getenv("PATH_CACHE", get_config_path(NAME), prefix = CONST["prefix"])