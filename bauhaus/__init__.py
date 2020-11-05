__version__ = "0.0.1"

from nnf import Var, And, Or, NNF
from functools import wraps, update_wrapper
import weakref
from collections import defaultdict


__all__ = (
    "Encoding", 
    "proposition", 
    "constraint"
    )


class Encoding:

    def __init__(self):
        """
        Store objects of annotated classes in propositions.
        Store _ConstraintBuilder objects in constraints to build
        when user calls encoding.compile()
        :propositions: type {class_name: {instances}}
        :constraints: [constraint_type(vars),..., constraint_type(vars)]
        """
        self.propositions = defaultdict(weakref.WeakValueDictionary) 
        self.constraints = set()


    def __repr__(self):
        """ """
        return str(self)


    def compile(self):
        """ Convert constraints into an NNF theory """
        theory = []

        for constraint in self.constraints:
            theory.append(constraint.build(self))
        return And(theory)

    
    def to_CNF(self, naive=False):
        """ Convert theory to CNF """
        from nnf import to_CNF as cnf
        return self.theory.cnf(naive=naive)


def proposition(encoding: Encoding, literal=None):
    ''' 
    Create a propositional variable from the decorated object
    and add to encoding.proposition
    Return original object instance or nnf.Var(string)
    '''
    if literal:
        if isinstance(literal, str):
            return Var(literal)
        else:
            raise TypeError(literal)
        
    def wrapper(cls):
        @wraps(cls)
        def wrapped(*args, **kwargs):
            ret = cls(*args, **kwargs)
            ret._var = Var(ret)
            class_name = ret.__class__.__name__
            encoding.propositions[class_name][id(ret)] = ret
            return ret
        return wrapped
    return wrapper


class _ConstraintBuilder:


    def __init__(self, constraint, *args, func=None):
        self._constraint = constraint
        self._variables = tuple(args)
        self._func = func

    def __hash__(self):
        return hash((self._constraint, self._variables, self._func))

    def __eq__(self, other):
        if isinstance(other, _ConstraintBuilder):
            return self.__hash__() == other.__hash__()
        raise NotImplemented

    def __str__(self):
        return f'constraint:{self._constraint}, variables:{self._variables}, function:{self._func}'
    

    def build(self, encoding: Encoding) -> NNF:
        """ 
        Builds a constraint from a _ConstraintBuilder object and its
        associated Encoding
        """
        inputs = self.get_inputs(encoding)
        return self._constraint(inputs)

    def get_inputs(self, encoding) -> [Var[]]:
        from inspect import isclass, ismethod

        inputs = []
        
        # Annotated a class or its instance method
        if self._func is not None:
            if self._func.__name__ in encoding.propositions:
                class_name = self._func.__name__
                for instance in encoding.propositions[class_name]:
                    obj = encoding.propositions[class_name][instance]
                    inputs.append(obj._var)
                return inputs
            elif ismethod(self._func) and self._func.__class__ in encoding.propositions:
                class_name = self._func.__class__
                for instance in encoding.propositions[class_name]:
                    obj = encoding.propositions[class_name][instance]
                    inputs.append({obj._var, self._func(obj)})
                return inputs
            else:
                # TODO: specify exception
                raise Exception("Class or instance method should be decorated.")

        # Constraint from method call
        for i, arg in enumerate(self._variables):
            # if reference is annotated class
            if arg[i].__name__ in encoding.propositions:
                for instance in encoding.propositions[arg[i].__name__]:
                    inputs.append(encoding.propositions[arg[i].__name__][instance]._var)
            # if object, add its nnf.Var attribute
            elif hasattr(arg[i], '_var'):
                inputs.append(arg._var)
            # if nnf.Var
            elif isinstance(arg[i], Var):
                inputs.append(arg)
            else:
                raise TypeError(arg)

        return inputs
    
    """ Constraint methods """

    def at_least_one(input: [Var[]]) -> NNF:
        """ Disjunction across all variables """
        return Or(input)

    def at_most_one(input: [Var[]]) -> NNF:
        """ And(Or(~a, ~b)) for all a,b in input """
        pass

    def exactly_one(input: [Var[]]) -> NNF:
        """ 
        Exactly one variable can be true of the input 
        And(at_most_one, at_least_one) 

        """
        pass

    def at_most_k(input: [Var[]], k=1) -> NNF:
        """ At most k variables can be true """
        pass

    def implies_all(self, left: Var, right: [Var[]]) -> NNF:
        """ And(Or(~left, right)) """
        pass


class constraint:
    """
    Decorator for class or instance method:
        @constraint.method(e)
        @proposition
        class A:
            
            @constraint.method(e)
            def do_something(self):
                pass

    Constraint creation by function call:
        constraint.method(e, *args)
    
    TODO: Add handling for instance methods
    relevant SO: https://stackoverflow.com/questions/42670667/using-classes-as-method-decorators?noredirect=1&lq=1

    """
    @classmethod
    def _decorate(encoding, constraint_type, args=None, k=None):
        """ Create _ConstraintBuilder objects from constraint method calls """
        # method call
        if args:
            constraint = _ConstraintBuilder(constraint_type, args)
            encoding.constraints.add(constraint)
            return constraint

        # decorator call
        def wrapper(func):
            @wraps(func)
            def wrapped(*args, **kwargs):
                ret = func(*args, **kwargs)
                constraint = _ConstraintBuilder(constraint_type, func=func)
                encoding.constraints.add(constraint)
                return ret
            return wrapped
        return wrapper

    def at_least_one(encoding, *args):
        return constraint._decorate(encoding, _ConstraintBuilder.at_least_one, args)

    def at_most_one(encoding, *args):
        return constraint._decorate(encoding, _ConstraintBuilder.at_most_one, args)

    def exactly_one(encoding, *args):
        return constraint._decorate(encoding, _ConstraintBuilder.exactly_one, args)

    def at_most_k(encoding, *args, k=1):
         return constraint._decorate(encoding, _ConstraintBuilder.at_most_k, args, k=k)

    def implies_all(encoding, *args):
         return constraint._decorate(encoding, _ConstraintBuilder.implies_all, args)
