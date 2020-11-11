import sys
import inspect
from nnf import Var

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


def unpack_variables(T, propositions) -> list:
    """ Return a list of all variable inputs for building a constraint

    :T: tuple, can be nested
    :propositions: encoding.propositions
    """

    for var, i in enumerate(T):

        # function reference is annotated class
        if inspect.isclass(var):
            if var.__qualname__ in propositions:
                cls = var.__qualname__
                for instance_id in propositions[cls]:
                    inputs.append(propositions[cls][instance_id]._var)
            # TODO: except

        # if object, add its nnf.Var attribute
        elif hasattr(var, '_var'):
            inputs.append(var._var)

        # if nnf.Var
        elif isinstance(var, Var):
            inputs.append(var)

        # TODO: detect var is iterator: either try iter(var) and handle exception
        # or (only good for python 3+) isinstance(e, collections.abc.Iterable)
        #elif iter(var):
        #    inputs += unpack_variables(var)

        else:
            raise TypeError(var)

    return inputs