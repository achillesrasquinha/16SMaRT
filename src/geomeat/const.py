from bpyutils.const import CPU_COUNT
from bpyutils.util.environ import getenv

from geomeat import __name__ as NAME

_PREFIX = NAME.upper()

QUALITY_AVERAGE     = 35
MAX_AMBIGUITY       = 0
MAX_HOMOPOLYMERS    = 8

CONST = {
    "prefix": _PREFIX,
    "jobs": getenv("JOBS", CPU_COUNT, prefix = _PREFIX),

    "url_silva_seed_132": "https://mothur.s3.us-east-2.amazonaws.com/wiki/silva.seed_v132.tgz",
    "url_silva_gold_bacteria": "https://mothur.s3.us-east-2.amazonaws.com/wiki/silva.gold.bacteria.zip"
}