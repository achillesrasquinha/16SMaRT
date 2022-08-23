# imports - module imports
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
from bpyutils.cli.util      import *
from s3mart.cli.parser     import get_args
from bpyutils.util._dict    import merge_dict
from bpyutils.util.types    import get_function_arguments
=======
=======
>>>>>>> template/master
=======
>>>>>>> template/master
from bpyutils.cli.util     import *
from s3mart.cli.parser import get_args
from bpyutils.util._dict   import merge_dict
from bpyutils.util.types   import get_function_arguments
<<<<<<< HEAD
<<<<<<< HEAD
>>>>>>> template/master
=======
>>>>>>> template/master
=======
>>>>>>> template/master


def command(fn):
    args    = get_args()
    
    params  = get_function_arguments(fn)

    params  = merge_dict(params, args)
    
    def wrapper(*args, **kwargs):
        return fn(**params)

    return wrapper