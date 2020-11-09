from nnf import NNF, And, Or, Var
from utils import ismethod

class _ConstraintBuilder:
    """
    Stores information necessary to build encoding constraint
    from class constraint calls. 

    Builds constraint for a given Encoding object.

    Supports following SAT constraints:
    - at least one
    - at most one
    - at most k
    - implies all
    - exactly one

    """

    #TODO: add __slots__?

    def __init__(self, constraint, *args, func=None, cls = None, k=None):
        self._constraint = constraint
        self._variables = tuple(args) #TODO: unpack args here before get_inputs?
        self._func = func
        self._cls = cls #TODO: see if we need to define this here
        self._k = k


    def __hash__(self):
        return hash((self._constraint, self._variables, self._func, self._cls, self._k))


    # ensures no duplicate constraints are created
    # TODO: would this be a problem with multiple encodings?
    def __eq__(self, other):
        if isinstance(other, _ConstraintBuilder):
            return self.__hash__() == other.__hash__()
        raise NotImplemented


    def __str__(self):
        return f'constraint:{self._constraint}, variables:{self._variables}, function:{self._func}'


    def build(self, propositions) -> NNF:
        """ 
        Builds a constraint from a _ConstraintBuilder object and its
        associated Encoding
        """
        inputs = self.get_inputs(propositions)
        return self._constraint(inputs)


    def get_inputs(self, propositions):
        """ Returns a list of inputs from a Constraint Builder object
        and the Encoding it is stored in """

        inputs = []
        
        # Annotated class or its instance method
        if self._func:
            if self._func.__qualname__ in propositions:
                self._cls = self._func.__qualname__

                for instance_id in propositions[self._cls]:
                    obj = propositions[self._cls][instance_id]
                    inputs.append(obj._var)
                return inputs

            if ismethod(self._func):
                # TODO: get class name from self._func 
                self._cls = self._func.__qualname__.split(".")[-2] # really wack but just checking

                for instance_id in propositions[self._cls]:
                    obj = propositions[self._cls][instance_id]
                    # TODO: figure out how we need to store variables from
                    # decorated instance methods. Currently doing dict(key: obj, val: func(obj))
                    # this is handy for implies_all, and if not, 
                    # we can simply combine obj._var + keys._var
                    inputs.append({obj: [self._func(obj)]})
                return inputs

            else:
                # TODO: specify exception
                raise Exception("Class or instance method should be decorated.")

        # Constraint from method call
        # TODO: add handling for iterables
        # TODO: unpacking for args, currently only getting first element
        # TODO: look into better storing for self._variables = *args
        for i, arg in enumerate(self._variables):

            # if reference is annotated class
            if arg[i].__name__ in propositions:
                cls = arg[i].__qualname__
                for instance_id in propositions[cls]:
                    inputs.append(propositions[cls][instance_id]._var)

            # if object, add its nnf.Var attribute
            elif hasattr(arg[i], '_var'):
                inputs.append(arg._var)

            # if nnf.Var
            elif isinstance(arg[i], Var):
                inputs.append(arg)

            elif iter(arg):
                inputs += get_inputs

            else:
                raise TypeError(arg)

        return inputs


    """ Constraint methods 
    
    #TODO: a biggie, but can leave till later

    """

    def at_least_one(input) -> NNF:
        """ Disjunction across all variables """
        return Or(input)

    def at_most_one(input) -> NNF:
        """ And(Or(~a, ~b)) for all a,b in input 
        use functools.product(input)
        """
        pass

    def exactly_one(input) -> NNF:
        """ 
        Exactly one variable can be true of the input 
        And(at_most_one, at_least_one) 
        """
        pass

    def at_most_k(input, k=1) -> NNF:
        """ At most k variables can be true """
        pass

    def implies_all(input) -> NNF:
        """ And(Or(~left, right)) """
        pass

