import weakref
import logging
from nnf import Var, And, NNF
from functools import wraps
from collections import defaultdict
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
        if not self.constraints:
            pass
        if not self.propositions:
            pass

        theory = []

        for constraint in self.constraints:
            clause = constraint.build(self.propositions)
            if not clause:
                # raise Warning that constraint yielded []
                pass
            theory.append(clause)
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
    """How constraint class works.

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
            #warning: building constraint with weird k
            pass
        return constraint._decorate(encoding, cbuilder.at_most_k, args=args, k=k)

    def implies_all(encoding: Encoding, left=None, right=None):
        """Left proposition implies right proposition """
        # type check on left and right
        left = tuple(flatten([left])) if left else None
        right = tuple(flatten([right])) if right else None
        return constraint._decorate(encoding, cbuilder.implies_all, left=left, right=right)

####################################

e = Encoding()
a = Var('a')
b = Var('b')

class StrHash(object):
    def __hash__(self):
        return hash(str(self))

@proposition(e)
class Mark(StrHash):
    def __init__(self, i, j):
        self.i = i
        self.j = j
    def __repr__(self):
        return f'x_{self.i}_{self.j}'

@constraint.at_most_one(e)
@proposition(e)
class Row(StrHash):

    @constraint.implies_all(e)    # Says that r_i implies the conjunction of variables corresponding to the marks returned
    def row_is_marked(self):
        return self.marks

    def __init__(self, i, all_marks):
        self.i = i
        self.marks = [m for m in all_marks if m.i == self.i]
    def __repr__(self):
        return f'r_{self.i}'
    
@constraint.at_most_one(e)
@proposition(e)
class Col(StrHash):
    
    @constraint.implies_all(e)    # Says that r_i implies the conjunction of variables corresponding to the marks returned
    def col_is_marked(self):
        return self.marks
    
    def __init__(self, j, all_marks):
        self.j = j
        self.marks = [m for m in all_marks if m.j == self.j]
    def __repr__(self):
        return f'c_{self.j}'

def main():
    marks = [Mark(i,j) for i in range(1,4) for j in range(1,4)]
    rows = [Row(i, marks) for i in range(1,4)]
    cols = [Col(j, marks) for j in range(1,4)]
    constraint.at_least_one(e, [])
    constraint.implies_all(e, left=[], right=[])
    theory = e.compile()
    print(theory)

main()