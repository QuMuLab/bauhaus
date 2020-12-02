import weakref
import logging
from nnf import Var, And, NNF
from functools import wraps
from collections import defaultdict
import warnings
from constraint_builder import _ConstraintBuilder as cbuilder
from utils import flatten


__all__ = (
    "Encoding", 
    "proposition", 
    "constraint"
    )


class Encoding:
    """
    Examples

    Attributes

    """

    def __init__(self):
        """
        Creates an Encoding object. This will store propositions
        and constraints that you can compile into a theory.

        Attributes:

            propositions (defaultdict(weakref.WeakValueDictionary)):
                       Stores decorated classes/functions pointing to
                       their associated instances.These are later used
                       to build the theory's constraints.

            constraints (set): A set of unique _ConstraintBuilder objects
                      that hold relevant information to build an NNF constraint.
                      They are added to the Encoding object whenever the
                      constraint decorator is used or when it is called
                      as a function.
        """
        self.propositions = defaultdict(weakref.WeakValueDictionary) 
        self.constraints = set()


    def __repr__(self) -> str:
        return f'Encoding: propositions:{self.propositions}, constraints:{self.constraints}'


    def compile(self) -> NNF:
        """ Convert constraints into an NNF theory """
        if not self.constraints or self.propositions:
            warnings.warn(f"Constraints or propositions in {self} are empty."
                         "Compiling this is not advisable.")

        theory = []

        for constraint in self.constraints:
            clause = constraint.build(self.propositions)
            if clause:
                theory.append(clause)
            else:
                warnings.warn(f"{constraint} was not built and"
                             "will not be added to the theory.")
        return And(theory)

    
    def to_CNF(theory: NNF, naive=False) -> NNF:
        """ Convert theory to CNF """
        from nnf import to_CNF as cnf
        return theory.cnf(naive=naive)


def proposition(encoding: Encoding, *args):
    ''' Create a propositional variable from the decorated
    class or function and add to encoding.proposition
    Return original object instance or nnf.Var(obj)

    Examples:

    Arguments:
        encoding:
        *args:

    Returns:
        Returns the function it decorated

    '''
    if args:
        if isinstance(args, object):
            return Var(args)
        else:
            raise TypeError(args)
        
    def wrapper(cls):
        @wraps(cls)
        def wrapped(*args, **kwargs):
            ret = cls(*args, **kwargs)
            ret._var = Var(ret)
            class_name = ret.__class__.__qualname__
            encoding.propositions[class_name][id(ret)] = ret
            return ret
        return wrapped
    return wrapper


class constraint:
    """Creates constraints on the fly when used as a decorator
    or as a function invocation.

    The constraint class works by directing all function
    calls from constraint methods to the classmethod _decorate,
    which is the decorator that caches the user-given information
    into a _ConstraintBuilder object.

    Examples:
        Decorator for class or instance method:
            @constraint.method(e)
            @proposition
            class A:
                
                @constraint.method(e)
                def do_something(self):
                    pass

        Constraint creation by function call:
            constraint.method(e, *args)

    """
    @classmethod
    def _decorate(cls,
                  encoding: Encoding,
                  constraint_type,
                  args=None,
                  k=None,
                  left=None,
                  right=None):
        """
        Create _ConstraintBuilder objects from constraint.method
        function calls

        Arguments:
            constraint (function):
                Reference to the function for building an SAT encoding
                constraint in _ConstraintBuilder
            args (tuple):
                User-given arguments from a function invocation.
                Default = None.
            func (function):
                Decorated class or bound method. Default = None.
            k (int):
                Used for constraint "At most K".
            left (tuple):
                Used for constraint "implies all".
                User-given arguments for the left side.
            right (tuple):
                Used for constraint "implies all".
                User-given arguments for the right side.

        Returns:
            Function call: Returns None
            Wrapper: Returns the function it decorated

        """
        #function call
        args = tuple(flatten(args)) if args else None
        if (args or (left and right)):
            constraint = cbuilder(constraint_type,
                                  args,
                                  k=k,
                                  left=left,
                                  right=right)
            encoding.constraints.add(constraint)
            return

        # decorator call
        def wrapper(func):
            constraint = cbuilder(constraint_type,
                                  args,
                                  func=func,
                                  k=k,
                                  left=left,
                                  right=right)
            encoding.constraints.add(constraint)

            @wraps(func)
            def wrapped(*args, **kwargs):
                ret = func(*args, **kwargs)
                return ret
            return wrapped
        return wrapper


    def at_least_one(encoding: Encoding, *args):
        """At least one of the propositional variables are True. """
        return constraint._decorate(encoding, cbuilder.at_least_one, args=args)

    def at_most_one(encoding: Encoding, *args):
        """At most one of the propositional variables are True. """
        return constraint._decorate(encoding, cbuilder.at_most_one, args=args)

    def exactly_one(encoding: Encoding, *args):
        """ Exactly one of the propositional variables are True. """
        return constraint._decorate(encoding, cbuilder.exactly_one, args=args)

    def at_most_k(encoding: Encoding, *args, k: int):
        """At most K of the propositional variables are True. """
        if not isinstance(k, int):
            raise TypeError(k)
        if k < 1:
            raise ValueError(k)
        if k == 1:
            warnings.warn("Warning: This will result in at most one constraint,"
                          "but we'll proceed anyway.")
        return constraint._decorate(encoding, cbuilder.at_most_k, args=args, k=k)

    def implies_all(encoding: Encoding, left=None, right=None):
        """Left proposition(s) implies right proposition(s) """
        left = tuple(flatten([left])) if left else None
        right = tuple(flatten([right])) if right else None
        return constraint._decorate(encoding, cbuilder.implies_all, left=left, right=right)
