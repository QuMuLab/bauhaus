from nnf import NNF, And, Or, Var
from itertools import chain, product, combinations
from utils import ismethod, unpack_variables, flatten, classname
from inspect import isclass


class _ConstraintBuilder:
    """
    Stores information necessary to build encoding constraint
    from constraint.method calls. Instances are stored in the
    list attribute 'constraints' in Encoding objects that are
    provided to the constraint.method

    Supports following SAT constraints:
    - at least one
    - at most one
    - at most k
    - implies all
    - exactly one

    Attributes:
        constraint (function)
        args (tuple)
        func (function)
        k (int)
        left (tuple)
        right (tuple)

    """

    def __init__(self, constraint, args, func=None, k=None, left=None, right=None):
        self._constraint = constraint
        self._vars = args
        self._func = func
        self._k = k
        self._left = left
        self._right = right

    def __hash__(self):
        return hash((self._constraint,
                     self._vars,
                     self._func,
                     self._k,
                     self._left, self._right))

    def __eq__(self, other) -> bool:
        if isinstance(other, _ConstraintBuilder):
            return self.__hash__() == other.__hash__()
        raise NotImplemented

    def __repr__(self) -> str:
        return f'constraint.{self._constraint}: variables:{self._vars}, function:{self._func}'
 
    def build(self, propositions) -> 'NNF':
        """Builds an SAT constraint from a ConstraintBuilder instance.

        Arguments:
            propositions: defaultdict(weakref.WeakValueDictionary)
        
        Returns:
            nnf.NNF: 

        """
        inputs = self.get_inputs(propositions)
        if self._constraint is _ConstraintBuilder.implies_all:
            left_vars, right_vars = [], []
            if self._left:
                left_vars = list(unpack_variables(self._left, propositions))
            if self._right:
                right_vars = list(unpack_variables(self._right, propositions))
            return self._constraint(inputs, left_vars, right_vars)
        elif not inputs:
            raise ValueError(inputs)
        return self._constraint(inputs)


    def get_inputs(self, propositions) -> list:
        """Returns a list of inputs to be used for building the constraint.
        
        If the ConstraintBuilder was created for a decorated class or method,
        then we check if the decorated class (self._func) is in the
        Encoding.propositions and return its instances.
        If the ConstraintBuilder does not have '_func', then it was invoked as 
        a function call. We gather its arguments (self._vars) and return.

        Arguments:
            propositions: defaultdict(weakref.WeakValueDictionary)
            self: ConstraintBuilder

        Returns:
            List of nnf.Var inputs, could be nested

        """
        inputs = []
        
        # Annotated class or its instance method
        if self._func:

            if hasattr(self._func, '__qualname__'):
                if self._func.__qualname__ in propositions:
                    cls = self._func.__qualname__
                    for instance_id in propositions[cls]:
                        obj = propositions[cls][instance_id]
                        inputs.append(obj._var)
                    return inputs
                # raise exception

                elif ismethod(self._func):
                    cls = classname(self._func)
                    if cls in propositions:
                        for instance_id in propositions[cls]:
                            obj = propositions[cls][instance_id]
                            res = [var._var for var in [*self._func(obj)]]
                            if self._constraint is _ConstraintBuilder.implies_all:
                                inputs.append({obj._var: res})
                            else:
                                res.append(obj._var)
                                inputs.extend(res)
                        return inputs
                # exception

        else:
            # Inputs from method call
            inputs = list(unpack_variables(self._vars, propositions))
            
        return inputs


    """ Constraint methods 

    Implementations of Naive SAT encodings.

    Reference:

    """

    def at_least_one(inputs: list) -> NNF:
        """At least one of the inputs are true.

        This is equivalent to a disjunction across all variables

        Arguments:
            inputs:

        Returns:
            nnf.NNF: Or(inputs)
        """
        if not inputs:
            raise ValueError

        return Or(inputs)

    def at_most_one(inputs: list) -> NNF:
        """At most one of the inputs are true.

        Arguments:
            inputs:

        Returns:
            nnf.NNF: And(Or(~a, ~b)) for all a,b in input 
        """
        if not inputs or type(inputs) is not list:
            raise ValueError("Inputs either empty or not correct type")

        inputs = list(map(lambda var: ~var, inputs))
        clauses = list(map(lambda c: Or(c), combinations(inputs, 2)))
        return And(clauses)

    def at_most_k(inputs: list, k: int) -> NNF:
        """ At most k variables can be true
        
        Arguments:
            inputs:
            k:

        Returns:
            nnf.NNF: 
        """
        if not 1 <= k <= len(inputs):
            raise ValueError("K is not within bounds")
        elif k == 1:
            return at_most_one(inputs)

        inputs = list(map(lambda var: ~var, inputs))
        clauses = list(map(lambda c: Or(c), combinations(inputs, k)))
        return And(clauses)

    def exactly_one(inputs: list) -> NNF:
        """ 
        Exactly one variable can be true of the input
        
        Arguments:
            inputs:

        Returns:
            nnf.NNF: And(at_most_one, at_least_one) 
        """
        at_most_one = at_most_one(inputs)
        at_least_one = at_least_one(inputs)
        
        if not(at_most_one and at_least_one):
            raise ValueError
        return And({at_most_one, at_least_one})
            
    def implies_all(inputs: list, left: list, right: list) -> NNF:
        """All left variables imply all right variables.
        
        Arguments:
            left:
            right:

        Returns:
            nnf.NNF: And(Or(~left_i, right_j))

        """
        clauses = []

        if inputs:
            for input in inputs:
                if isinstance(input, dict):
                    for key, value in input.items():
                        left_vars = left + [key]
                        right_vars = right + value
                        left_vars = list(map(lambda var: ~var, left_vars))
                        res = list(map(lambda clause: Or(clause), product(left_vars, right_vars)))
                        clauses.extend(res)

        elif left and right:
            left_vars = list(map(lambda var: ~var, left))
            clauses = list(map(lambda clause: Or(clause), product(left_vars, right)))

        return And(clauses)



