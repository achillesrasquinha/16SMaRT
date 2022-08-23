# imports - compatibility imports
from __future__ import absolute_import

<<<<<<< HEAD
<<<<<<< HEAD
# imports - standard imports
import traceback

from s3mart.commands.util 	import cli_format
from bpyutils.util._dict        import merge_dict
from bpyutils.util.system   	import touch
from bpyutils.config			import environment
from bpyutils import log
from s3mart 	import cli
from bpyutils._compat		    import iteritems
from s3mart.__attr__      	import __name__
from s3mart.exception      import DependencyNotFoundError
=======
=======
>>>>>>> template/master
from s3mart.commands.util 	import cli_format
from bpyutils.util._dict        import merge_dict
from bpyutils.util.system   	import (touch)
from bpyutils.util.error        import pretty_print_error
from bpyutils.config			import environment
from bpyutils.exception         import DependencyNotFoundError
from bpyutils import log
from s3mart 	import cli
from bpyutils._compat		    import iteritems
from s3mart.__attr__ import __name__
<<<<<<< HEAD
>>>>>>> template/master
=======
>>>>>>> template/master

logger   = log.get_logger(level = log.DEBUG)

ARGUMENTS = dict(
    jobs						= 1,
    check		 				= False,
    interactive  				= False,
    yes			 				= False,
    no_cache		            = False,
    no_color 	 				= True,
    output						= None,
    ignore_error				= False,
    force						= False,
    verbose		 				= False
)

@cli.command
def command(**ARGUMENTS):
    try:
        return _command(**ARGUMENTS)
    except Exception as e:
        if not isinstance(e, DependencyNotFoundError):
            cli.echo()

<<<<<<< HEAD
<<<<<<< HEAD
            traceback_str = traceback.format_exc()
            cli.echo(traceback_str)
=======
            pretty_print_error(e)
>>>>>>> template/master
=======
            pretty_print_error(e)
>>>>>>> template/master

            cli.echo(cli_format("""\
An error occured while performing the above command. This could be an issue with
"s3mart". Kindly post an issue at https://github.com/achillesrasquinha/s3mart/issues""", cli.RED))
        else:
            raise e

def to_params(kwargs):
    class O(object):
        pass

    params = O()

    kwargs = merge_dict(ARGUMENTS, kwargs)

    for k, v in iteritems(kwargs):
        setattr(params, k, v)

    return params

<<<<<<< HEAD
<<<<<<< HEAD
def _command(**kwargs):
=======
def _command(*args, **kwargs):
>>>>>>> template/master
=======
def _command(*args, **kwargs):
>>>>>>> template/master
    a = to_params(kwargs)

    if not a.verbose:
        logger.setLevel(log.NOTSET)

    logger.info("Environment: %s" % environment())
    logger.info("Arguments Passed: %s" % locals())

    file_ = a.output

    if file_:
        logger.info("Writing to output file %s..." % file_)
        touch(file_)
    
    logger.info("Using %s jobs..." % a.jobs)