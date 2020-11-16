import sys
import inspect
import functools
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


def flatten(object):
    for item in object:
        if isinstance(item, (list, tuple, set)):
            yield from flatten(item)
        else:
            yield item


def unpack_variables(T: tuple, propositions) -> set:
    """ Return a list of all variable inputs for building a constraint

    :T: tuple, can be nested
    :param propositions: defaultdict(weakref.WeakValueDictionary)
    """
    inputs = set()

    for var in T:

        # function reference is annotated class or bound method
        if hasattr(var, '__qualname__'):
            if var.__qualname__ in propositions:
                cls = var.__qualname__
                for instance_id in propositions[cls]:
                    inputs.add(propositions[cls][instance_id]._var)
            elif var.__qualname__.split('.<locals>', 1)[0].rsplit('.', 1)[0] in propositions:
                cls = var.__qualname__.split('.<locals>', 1)[0].rsplit('.', 1)[0]
                for instance_id in propositions[cls]:
                    obj = propositions[cls][instance_id]
                    # TODO: is following expected behaviour if someone adds a bound method to a constraint?
                    inputs.add(tuple(var(obj)))
                return inputs

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

    return inputs