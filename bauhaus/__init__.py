__version__ = "0.0.1"

import weakref
from nnf import Var, And, Or, NNF
from functools import wraps
from collections import defaultdict
from constraint_builder import _ConstraintBuilder as cbuilder


__all__ = (
    "Encoding", 
    "proposition", 
    "constraint"
    )


class Encoding:

    def __init__(self):
        """
        Store objects of annotated classes in propositions.
        Store _ConstraintBuilder objects in constraints attribute for
        when user calls encoding.compile()

        :propositions: type {class_name: {instances}}
        :constraints: [constraint_type(vars),..., constraint_type(vars)]
        """
        self.propositions = defaultdict(weakref.WeakValueDictionary) 
        self.constraints = set() 


    def __repr__(self):
        return str(self)


    def compile(self):
        """ Convert constraints into an NNF theory """
        theory = []

        for constraint in self.constraints:
            theory.append(constraint.build(self.propositions))
        return And(theory)

    
    def to_CNF(self, naive=False):
        """ Convert theory to CNF """
        from nnf import to_CNF as cnf
        return self.theory.cnf(naive=naive)


def proposition(encoding: Encoding, *arg):
    ''' 
    Create a propositional variable from the decorated object
    and add to encoding.proposition
    Return original object instance or nnf.Var(obj)
    '''
    if arg:
        if isinstance(arg, object):
            return Var(arg)
        else:
            raise TypeError(arg)
        
    def wrapper(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            ret = func(*args, **kwargs)
            ret._var = Var(ret)
            class_name = ret.__class__.__name__
            encoding.propositions[class_name][id(ret)] = ret
            return ret
        return wrapped
    return wrapper


class constraint:
    """
    TODO: docstrings
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
    def _decorate(cls, encoding, constraint_type, args=None, k=None):
        """ Create _ConstraintBuilder objects from constraint.method function calls """

        # function call
        if args:
            constraint = cbuilder(constraint_type, args, k=k)
            encoding.constraints.add(constraint)
            return

        # decorator call
        def wrapper(func):

            # before proposition decorator kicks in
            # this is when methods are defined but classes aren't, so we can
            # decorate instance methods and classes
            constraint = cbuilder(constraint_type, args, func=func, cls=func.__wrapped__, k=k)
            encoding.constraints.add(constraint)

            @wraps(func)
            def wrapped(*args, **kwargs):
                ret = func(*args, **kwargs) # equiv to proposition(fn(*args, **kwargs))
                return ret
            return wrapped
        return wrapper


    def at_least_one(encoding, *args):
        return constraint._decorate(encoding, cbuilder.at_least_one, args)

    def at_most_one(encoding, *args):
        return constraint._decorate(encoding, cbuilder.at_most_one, args)

    def exactly_one(encoding, *args):
        return constraint._decorate(encoding, cbuilder.exactly_one, args)

    def at_most_k(encoding, *args, k=1):
         return constraint._decorate(encoding, cbuilder.at_most_k, args, k=k)

    def implies_all(encoding, *args):
         return constraint._decorate(encoding, cbuilder.implies_all, args)

####################################

e = Encoding()

class StrHash(object):
    def __hash__(self):
        return hash(str(self))

@proposition(e)
class Mark(StrHash):
    def __init__(self, i, j):
        self.i = i
        self.j = j
    def __str__(self):
        return f'x_{self.i}_{self.j}'

@constraint.at_most_one(e)
@proposition(e)
class Row(StrHash):

    @proposition(e)    # Says that r_i implies the conjunction of variables corresponding to the marks returned
    def row_is_marked(self):
        return self.marks

    def __init__(self, i, all_marks):
        self.i = i
        self.marks = [m for m in all_marks if m.i == self.i]
    def __str__(self):
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
    def __str__(self):
        return f'c_{self.j}'

def main():
    constraint.at_least_one(e, Row, Col, (Row, Col))
    marks = [Mark(i,j) for i in range(1,4) for j in range(1,4)]
    rows = [Row(i, marks) for i in range(1,4)]
    cols = [Col(j, marks) for j in range(1,4)]
    theory = e.compile()

main()