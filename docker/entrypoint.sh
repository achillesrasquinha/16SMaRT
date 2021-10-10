#!/bin/bash --login

set -euo pipefail

if [ "${1:0:1}" = "-" ]; then
    set -- geomeat "$@"
fi

exec "$@"