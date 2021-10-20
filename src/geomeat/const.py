from bpyutils.const import CPU_COUNT
from bpyutils.util.environ import getenv

from geomeat import __name__ as NAME

_PREFIX = NAME.upper()

N_JOBS  = getenv("JOBS", CPU_COUNT, prefix = _PREFIX)
QUALITY_AVERAGE = 35