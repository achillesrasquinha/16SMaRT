<<<<<<< HEAD
from __future__ import absolute_import

=======

from __future__ import absolute_import


>>>>>>> template/master
try:
    import os

    if os.environ.get("S3MART_GEVENT_PATCH"):
        from gevent import monkey
        monkey.patch_all(threaded = False, select = False)
except ImportError:
    pass

# imports - module imports
from s3mart.__attr__ import (
    __name__,
    __version__,
    __build__,
<<<<<<< HEAD
    __description__,
    __author__
)
from s3mart.__main__    import main
from s3mart.config      import PATH
from s3mart.const       import DEFAULT

from bpyutils.cache       import Cache
from bpyutils.config      import Settings
=======

    __description__,

    __author__
)
from s3mart.config      import PATH
from s3mart.__main__    import main

from bpyutils.cache       import Cache
from bpyutils.config      import Settings
from bpyutils.util.jobs   import run_all as run_all_jobs, run_job

>>>>>>> template/master

cache = Cache(dirname = __name__)
cache.create()

<<<<<<< HEAD
settings = Settings(location = PATH["CACHE"], defaults = {
    "jobs":                     DEFAULT["jobs"],
    "trim_chunks":              DEFAULT["trim_chunks"],
    "primer_difference":        DEFAULT["primer_difference"],
    "quality_average":          DEFAULT["quality_average"],
    "maximum_ambiguity":        DEFAULT["maximum_ambiguity"],
    "maximum_homopolymers":     DEFAULT["maximum_homopolymers"],
    "classification_cutoff":    DEFAULT["classification_cutoff"],
    "filter_taxonomy":          DEFAULT["filter_taxonomy"],
    "taxonomy_level":           DEFAULT["taxonomy_level"],
    "cutoff_level":             DEFAULT["cutoff_level"],

    "silva_version":            DEFAULT["silva_version"],
    "silva_pcr_start":     DEFAULT["silva_pcr_start"],
    "silva_pcr_end":       DEFAULT["silva_pcr_end"],
    
    "seed":                     DEFAULT["seed"],

    "keep_temp_files":          DEFAULT["keep_temp_files"],
    
    "minimal_output":           DEFAULT["minimal_output"]
})
=======
settings = Settings()

>>>>>>> template/master

def get_version_str():
    version = "%s%s" % (__version__, " (%s)" % __build__ if __build__ else "")
    return version
