from bpyutils.const import CPU_COUNT
from bpyutils.util.environ import getenv

from s3mart import __name__ as NAME

_PREFIX = NAME.upper()

CONST = {
    "prefix": _PREFIX,

    "url_silva_seed": "https://mothur.s3.us-east-2.amazonaws.com/wiki/silva.seed_{version}.tgz",
    "url_silva_gold_bacteria": "https://mothur.s3.us-east-2.amazonaws.com/wiki/silva.gold.bacteria.zip"
}

DEFAULT = {
    "jobs":                 getenv("JOBS", CPU_COUNT, prefix = _PREFIX),
    "filter_chunks":        8,
    "primer_difference":    5,
    "quality_average":      35,
    "maximum_ambiguity":    0,
    "maximum_homopolymers": 8,
    "silva_version":        "132",
    "silva_seed_pcr_start": 6388,
    "silva_seed_pcr_end":   13861
}