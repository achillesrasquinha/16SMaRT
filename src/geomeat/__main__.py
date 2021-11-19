
from __future__ import absolute_import


import sys

from   s3mart.commands import command as main

if __name__ == "__main__":
    code = main()
    sys.exit(code)
