import sys
import inspect
import functools
from nnf import Var

"""
Utilities for bauhaus library.

"""

def ismethod(func) -> bool:
    """Checks if a function is a method.

    *Taken from multipledispatch

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


def flatten(object):
    """ 
    Flattens an iterable.

    """
    # refactor case where object is not iterable/collection
    if not isinstance(object, (list, tuple, set)):
        return object
    for item in object:
        if isinstance(item, (list, tuple, set)):
            yield from flatten(item)
        else:
            yield item

def classname(func) -> str:
    """ Returns the class name of a given function.
    
    Necessary since there's no proper way to get the
    classname during constraint creation or using inspect
    because the bound method is added before classes are defined.

    Arguments:
        func: Bounded method of a class.

    Returns:
        name (str): Name of the class a bounded function belongs to.

    """
    if hasattr(func, '__qualname__'):
        return func.__qualname__.split('.<locals>', 1)[0].rsplit('.', 1)[0]
    else:
        return None


def unpack_variables(T: tuple, propositions) -> list:
    """ Returns a set of all variable inputs for building a constraint
    
    Arguments:
        T (tuple):
        propositions:

    Returns:
        Set of inputs, which ensures that only unqiue variables are
        returned.

    """
    inputs = set()

    for var in T:

        if hasattr(var, '__qualname__'):
            if var.__qualname__ in propositions:
                cls = var.__qualname__
                for instance_id in propositions[cls]:
                    inputs.add(propositions[cls][instance_id]._var)

            elif classname(var) in propositions:
                cls = classname(var)
                for instance_id in propositions[cls]:
                    obj = propositions[cls][instance_id]
                    ret = set(flatten(var(obj)))
                    ret.add(obj)
                    inputs.update(ret)

        # if object, add its nnf.Var attribute
        elif hasattr(var, '_var'):
            inputs.add(var._var)

        # if nnf.Var object
        elif isinstance(var, Var):
            inputs.add(var)

        elif isinstance(var, tuple):
            inputs.update(unpack_variables(var, propositions))

        else:
            raise TypeError(var)

    return list(inputs)