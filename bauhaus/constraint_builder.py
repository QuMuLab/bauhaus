from nnf import NNF, And, Or
from itertools import product, combinations
from utils import ismethod, classname
from utils import unpack as unpack


class _ConstraintBuilder:
    """
    A _ConstraintBuilder object caches information for building
    an encoding's constraint. They're created when a user decorates
    a class or method or invokes the constraint class in core.
    Instances are stored in the attribute 'constraints' in Encoding
    objects.

    Supports following SAT constraints:
    - at least one
    - at most one
    - at most k
    - implies all
    - exactly one

    Attributes:
        constraint : function
            Reference to the function for building an SAT encoding
            constraint in _ConstraintBuilder
        args : tuple
            User-given arguments from a function invocation.
        func : function
            Decorated class or bound method. Default = None.
        k : int
            Integer for constraint "At most K". Default = None.
        left : tuple
            Used for constraint "implies all". Default = None.
            User-given arguments for the left side.
        right : tuple
            Used for constraint "implies all". Default = None.
            User-given arguments for the right side.

    """

    def __init__(self, constraint, args, func=None,
                 k=None, left=None, right=None):
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
        raise NotImplementedError

    def __repr__(self) -> str:
        return f'constraint.{self._constraint}: variables:{self._vars}, function:{self._func}'

    def build(self, propositions) -> 'NNF':
        """Builds an SAT constraint from a ConstraintBuilder instance.

        Note:
        There is unique handling for the implies all constraint
        where a user could have the following cases,
        1) implies_all used as a class or bound method:
            For this case, we can have inputs (list of dictionaries)
            and left or right attributes, which must be validated
            by utils/unpack_variables. We set left and right as
            empty lists to make it simple for merging the propositions
            in _ConstraintBuilder.implies_all

        2) implies_all used as a function invocation:
            If called as a function, the user must provide both
            a left and right side of the implication. This is
            ensured in core/constraint._decorate. No arguments
            are allowed to be passed based on the function
            definition of core/constraint.implies_all, so inputs
            will be empty.

        Arguments:
            propositions : defaultdict(weakref.WeakValueDictionary)
            Stores instances in the form [classname] -> [instance_id: object]

        Returns:
            nnf.NNF: A built NNF constraint.

        """
        inputs = self.get_inputs(propositions)
        if self._constraint is _ConstraintBuilder.implies_all:
            left_vars = unpack(self._left, propositions) if self._left else []
            right_vars = unpack(self._right, propositions) if self._right else []
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
            propositions : defaultdict(weakref.WeakValueDictionary)
            self : ConstraintBuilder

        Returns:
            List of nnf.Var inputs

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
            # Inputs from function invocation
            inputs = unpack(self._vars, propositions)

        return inputs

    """ Constraint methods

    Implementations of Naive SAT encodings.

    Reference:

    """

    def at_least_one(inputs: list) -> NNF:
        """At least one of the inputs are true.

        This is equivalent to a disjunction across all variables

        Arguments:
            inputs : list[nnf.Var]

        Returns:
            nnf.NNF: Or(inputs)
        """
        if not inputs:
            raise ValueError

        return Or(inputs)

    def at_most_one(inputs: list) -> NNF:
        """At most one of the inputs are true.

        Arguments:
            inputs : list[nnf.Var]

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
            inputs : list[nnf.Var]
            k : int

        Returns:
            nnf.NNF:
        """
        if not 1 <= k <= len(inputs):
            raise ValueError("K is not within bounds")
        elif k == 1:
            return _ConstraintBuilder.at_most_one(inputs)

        inputs = list(map(lambda var: ~var, inputs))
        clauses = list(map(lambda c: Or(c), combinations(inputs, k)))
        return And(clauses)

    def exactly_one(inputs: list) -> NNF:
        """
        Exactly one variable can be true of the input

        Arguments:
            inputs : list[nnf.Var]

        Returns:
            nnf.NNF: And(at_most_one, at_least_one)
        """
        at_most_one = _ConstraintBuilder.at_most_one(inputs)
        at_least_one = _ConstraintBuilder.at_least_one(inputs)

        if not(at_most_one and at_least_one):
            raise ValueError
        return And({at_most_one, at_least_one})

    def implies_all(inputs: list, left: list, right: list) -> NNF:
        """All left variables imply all right variables.

        Arguments:
            inputs: list[dict]
            left : list[nnf.Var]
            right: list[nnf.Var]

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
                        res = list(map(lambda clause: Or(clause),
                                       product(left_vars, right_vars)))
                        clauses.extend(res)

        elif left and right:
            left_vars = list(map(lambda var: ~var, left))
            clauses = list(map(lambda clause: Or(clause),
                               product(left_vars, right)))

        return And(clauses)
