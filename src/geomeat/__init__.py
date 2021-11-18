from __future__ import absolute_import

try:
    import os

    if os.environ.get("GEOMEAT_GEVENT_PATCH"):
        from gevent import monkey
        monkey.patch_all(threaded = False, select = False)
except ImportError:
    pass

# imports - module imports
from geomeat.__attr__ import (
    __name__,
    __version__,
    __build__,
    __description__,
    __author__
)
from geomeat.__main__    import main
from geomeat.config      import PATH
from geomeat.const       import DEFAULT

from bpyutils.cache       import Cache
from bpyutils.config      import Settings

cache = Cache(dirname = __name__)
cache.create()

settings = Settings(location = PATH["CACHE"], defaults = {
    "jobs":                 DEFAULT["jobs"],
    "filter_chunks":        DEFAULT["filter_chunks"],
    "primer_difference":    DEFAULT["primer_difference"],
    "quality_average":      DEFAULT["quality_average"],
    "maximum_ambiguity":    DEFAULT["maximum_ambiguity"],
    "maximum_homopolymers": DEFAULT["maximum_homopolymers"],
    "silva_version":        DEFAULT["silva_version"],
    "silva_seed_pcr_start": DEFAULT["silva_seed_pcr_start"],
    "silva_seed_pcr_end":   DEFAULT["silva_seed_pcr_end"]
})

def get_version_str():
    version = "%s%s" % (__version__, " (%s)" % __build__ if __build__ else "")
    return version
