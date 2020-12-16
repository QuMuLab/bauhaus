import sys
import inspect
from nnf import Var

"""Utilities for bauhaus library."""


def ismethod(func) -> bool:
    """Checks if a function is a method.

    *Taken from multipledispatch

    Note that this has to work as the method is defined but before
    the class is defined. At this stage methods look like functions.

    Returns
    -------
    ismethod : bool
        True if it is a method belonging to a class and False if not.

    Reference
    ---------
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
    """Flattens an iterable.

    Returns object immediately if not a collections object.
    """
    if not isinstance(object, (list, tuple, set)):
        return object
    for item in object:
        if isinstance(item, (list, tuple, set)):
            yield from flatten(item)
        else:
            yield item


def classname(func) -> str:
    """Returns the class name of a given function.

    Necessary since there's no proper way to get the
    classname during constraint creation or using inspect
    because the bound method is added before classes are defined.

    Arguments
    ---------
    func : function
        Bounded method of a class.

    Returns
    -------
    name : str
        Name of the class a bounded function belongs to.

    """
    if hasattr(func, '__qualname__'):
        return func.__qualname__.split('.<locals>', 1)[0].rsplit('.', 1)[0]
    else:
        return None


def unpack_variables(T, propositions) -> list:
    """ Returns a list of all variable inputs for building a constraint

    Arguments
    ---------
    T : tuple
    propositions : defaultdict(weakref.WeakValueDictionary)

    Returns
    -------
    inputs : list
        List of inputs with only unqiue variables returned.

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
                    # apply method to object to get return values
                    ret = set(flatten([var(obj)]))
                    # check return values are valid inputs
                    res = unpack_variables(ret, propositions)
                    # add nnf.Var attribute of object
                    res.append(obj._var)
                    inputs.update(res)

        # if object, add its nnf.Var attribute
        elif hasattr(var, '_var'):
            inputs.add(var._var)

        # if nnf.Var object
        elif isinstance(var, Var):
            inputs.add(var)

        elif isinstance(var, (list, tuple, set)):
            inputs.update(unpack_variables(var, propositions))

        else:
            try:
                # convert to nnf.Var
                inputs.add(Var(var))
            except Exception as e:
                raise ValueError(f"Provided input {var} is not of an annotated class or method," 
                                 " instance of such as class or method, or of type nnf.Var."
                                 " Attempted conversion of {var} to nnf.Var also failed and"
                                f" yielded the following error message: {e}")
    return list(inputs)
