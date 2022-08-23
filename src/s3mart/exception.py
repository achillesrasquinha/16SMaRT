<<<<<<< HEAD
# imports - standard imports
import subprocess as sp

class S3martError(Exception):
    pass

class PopenError(S3martError, sp.CalledProcessError):
    pass

=======
class S3martError(Exception):
    pass

>>>>>>> template/master
class DependencyNotFoundError(ImportError):
    pass