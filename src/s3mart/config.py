<<<<<<< HEAD
import os.path as osp

from s3mart.__attr__ import __name__ as NAME
from s3mart.const import CONST

from bpyutils.config      import get_config_path
from bpyutils.util.system  import pardir
from bpyutils.util.environ import getenv
=======
from __future__ import absolute_import

import os.path as osp

from s3mart.__attr__ import __name__ as NAME

from bpyutils.config      import get_config_path
from bpyutils.util.system import pardir
>>>>>>> template/master

PATH = dict()

PATH["BASE"]  = pardir(__file__, 1)
PATH["DATA"]  = osp.join(PATH["BASE"], "data")
<<<<<<< HEAD
PATH["CACHE"] = getenv("PATH_CACHE", get_config_path(NAME), prefix = CONST["prefix"])
=======
PATH["CACHE"] = get_config_path(NAME)
>>>>>>> template/master
