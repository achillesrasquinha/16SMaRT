# imports - standard imports
import subprocess as sp

class GeomeatError(Exception):
    pass

class PopenError(GeomeatError, sp.CalledProcessError):
    pass

class DependencyNotFoundError(ImportError):
    pass