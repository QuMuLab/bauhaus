__version__ = "0.0.1"

from nnf import Var, And, Or, NNF
from functools import wraps, update_wrapper
import weakref
from collections import defaultdict


class Encoding:

    def __init__(self):
        """
        :propositions: type {class_name: {instances}}
        :theory: [constraint_type(vars),..., constraint_type(vars)]
        """
        self.propositions = defaultdict(weakref.WeakValueDictionary)
        self.constraints = [] # WIP constraints we incrementally add to build at .compile()
        self.theory = [] # WIP stores final NNF


    def __repr__(self):
        """ """
        pass


    def compile(self):
        """ """
        pass

    
    def to_CNF(self, naive=False):
        """ Convert theory to CNF """
        from nnf import to_CNF as cnf
        return self.theory.cnf(naive=naive)


def proposition(encoding, literal=None):
    ''' 
    Create a propositional variable from the decorated object
    and add to encoding.proposition
    Return original object instance or nnf.Var(string)
    '''
    if literal and isinstance(literal, str):
        return Var(literal)
        
    def wrapper(cls):
        @wraps(cls)
        def wrapped(*args, **kwargs):
            ret = cls(*args, **kwargs)
            ret.var = Var(ret)
            class_name = ret.__class__.__name__
            if class_name not in encoding.propositions:
                encoding.propositions[class_name] = [ret]
            else:
                encoding.propositions[class_name].append(ret)
            return ret
        return wrapped
    return wrapper


class constraint:
    """
    Constraint of a class or in a class:
    Each constraint is associated with the instance of the class.
    We need to keep track of,
    - the encoding object
    - class 
    - if class function passed to decorator, then classfunc and class name

    Constraint creation not by decorator:
    constraint.method(encoding, *args)
    which is relatively straightforward

    """

    def at_least_one(encoding):
        ''' A disjunction across all variables'''
        def wrapper(func):
            @wraps(func)
            def wrapped(*args, **kwargs):
                ret = func(*args, **kwargs)
                print("in @at least one")
                # add to encoding.theory
                return ret
            return wrapped
        return wrapper

    def at_most_one(encoding):
        def wrapper(func):
            @wraps(func)
            def wrapped(*args, **kwargs):
                ret = func(*args, **kwargs)
                print("in @at most one")
                # add to encoding.theory
                return ret
            return wrapped
        return wrapper

    def exactly_one(encoding):
        #And(at_most_one, at_least_one)
        def wrapper(func):
            @wraps(func)
            def wrapped(*args, **kwargs):
                ret = func(*args, **kwargs)
                print("in @ exactly one")
                # add to encoding.theory
                return ret
            return wrapped
        return wrapper

    def at_most_k(encoding, k=1):
        def wrapper(func):
            @wraps(func)
            def wrapped(*args, **kwargs):
                ret = func(*args, **kwargs)
                print("in @at most k")
                # add to encoding.theory
                return ret
            return wrapped
        return wrapper

    def implies_all(encoding):
        def wrapper(func):
            @wraps(func)
            def wrapped(*args, **kwargs):
                ret = func(*args, **kwargs)
                print("in @implies all")
                # add to encoding.theory
                return ret
            return wrapped
        return wrapper