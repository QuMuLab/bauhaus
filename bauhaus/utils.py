import sys
import inspect

"""
Utilities for bauhaus library.

"""

def ismethod(func) -> bool:
    """ 
    *Taken from multipledispatch

    Is func a method?

    Note that this has to work as the method is defined but before 
    the class is defined. At this stage methods look like functions.

    Reference:
    https://github.com/mrocklin/multipledispatch/blob/master/multipledispatch/core.py#L74

    """
    if hasattr(inspect, "signature"):
        signature = inspect.signature(func)
        return signature.parameters.get('self', None) is not None
    else:
        if sys.version_info.major < 3:
            spec = inspect.getargspec(func)
        else:
            spec = inspect.getfullargspec(func)
        return spec and spec.args and spec.args[0] == 'self'


def unpack(L):
    """ TBD method for flattening tuple(args) during instantiation """
    pass