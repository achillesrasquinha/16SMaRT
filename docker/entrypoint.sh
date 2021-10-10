#!/bin/bash --login

set -euo pipefail

set +euo pipefail
conda activate $CONDA_ENV

set -euo pipefail

if [ "${1:0:1}" = "-" ]; then
    set -- geomeat "$@"
fi

exec "$@"