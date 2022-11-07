from bpyutils.util.array   import sequencify
from bpyutils.util.imports import import_handler

# imports - module imports
from s3mart.cli.parser import get_args
from s3mart import cli

def cli_format(string, type_):
    args = get_args(as_dict = False)
    
    if hasattr(args, "no_color") and not args.no_color:
        string = cli.format(string, type_)

    return string