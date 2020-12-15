from nnf import NNF, And, Or
from itertools import product, combinations
from utils import ismethod, classname, flatten
from utils import unpack_variables as unpack
import warnings
from collections import defaultdict


class _ConstraintBuilder:
    """
    A _ConstraintBuilder object caches information for building
    an encoding's constraint. They're instantiated when a user decorates
    a class, method, or invokes the constraint class in bauhaus/core.py.
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
        instance_constraints : defaultdict(list)
            Stores per-instance constraints to be viewed by the
            user for debugging purposes.

    """

    def __init__(self,
                 constraint,
                 args=None,
                 func=None,
                 k=None,
                 left=None,
                 right=None):
        self._constraint = constraint
        self._vars = args
        self._func = func
        self._k = k
        self._left = left
        self._right = right
        self.instance_constraints = defaultdict(list)

    def __hash__(self):
        return hash((self._constraint,
                     self._vars,
                     self._func,
                     self._k,
                     self._left,
                     self._right))

    def __eq__(self, other) -> bool:
        if isinstance(other, _ConstraintBuilder):
            return self.__hash__() == other.__hash__()
        raise NotImplementedError

    def __repr__(self) -> str:
        k = f"k = {self._k}"
        variables = f" variables = {self._vars}"
        constraint_type = f"constraint.{self._constraint.__name__}:"
        left = f" left implication = {self._left}"
        right = f" right implication = {self._right}"

        if self._func:
            function = f"function = {self._func.__qualname__}"
            if self._k:
                return (f"{constraint_type}  {function}  {k}")
            if self._constraint is _ConstraintBuilder.implies_all:
                return (f"{constraint_type}  {function}  {left}  {right}")
            return (f"{constraint_type}  {function}")
        else:
            if self._k:
                return (f"{constraint_type}  {k}  {variables}")
            if self._constraint is _ConstraintBuilder.implies_all:
                return (f"{constraint_type}  {left}  {right}")
            return (f"{constraint_type}  {variables}")

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
            ensured in bauhaus/core.constraint._decorate. No positional 
            arguments are allowed to be passed based on the function
            definition of core/constraint.implies_all, so inputs
            will be empty for this case.

        Arguments:
            propositions : defaultdict(weakref.WeakValueDictionary)
            Stores instances in the form [classname] -> [instance_id: object]

        Returns:
            nnf.NNF: A built NNF constraint.

        """
        if self._constraint is _ConstraintBuilder.implies_all:
            left_vars = unpack(self._left, propositions) if self._left else []
            right_vars = unpack(self._right, propositions) if self._right else []
            if self._func:
                # retrieve dictionary of inputs
                inputs = self.get_implication_inputs(propositions) 
                if not any(inputs.values()) and not right_vars:
                    raise ValueError(f"The '{self}' cannot be built"
                                     " as it is decorating a class and"
                                     " the right implication variables are not"
                                     " provided. If it is decorating a method,"
                                     " ensure that the method's return is" 
                                     " valid for bauhaus or for the nnf library."
                                     " Check your decorator signature and set"
                                     " the 'right' keyword argument to such a value.")
            else:
                # inputs should be empty if not created from a decorator
                inputs = []
            return self._constraint(self, inputs, left_vars, right_vars)
        
        inputs = self.get_inputs(propositions)
        if not inputs:
            raise ValueError(inputs)
        if self._constraint is _ConstraintBuilder.at_most_k:
            return self._constraint(self, inputs, k=self._k)
        return self._constraint(self, inputs)

    def get_inputs(self, propositions) -> list:
        """Returns a list of inputs to be used for building the constraint.

        If the ConstraintBuilder was created for a decorated class or method,
        we check if the decorated class name (self._func) is a key in the
        Encoding.propositions and return its instances.
        
        If the ConstraintBuilder does not have the '_func' attribute,
        then it was invoked as a function call.
        We gather and validate its arguments (self._vars).

        Arguments:
            propositions : defaultdict(weakref.WeakValueDictionary)
            self : ConstraintBuilder

        Returns:
            List of nnf.Var inputs
        """
        inputs = []

        # Annotated class or its instance method
        if not self._func:
            return unpack(self._vars, propositions)
        else:
            ret = unpack([self._func], propositions)
            if not ret:
                raise ValueError(f"The {self} resulted in an empty {ret}")
            return ret

    def get_implication_inputs(self, propositions) -> dict:
        """ Returns a dictionary of values for an implication
            created with a decorator over a class or method.
            
            Arguments:
                    self : _ConstraintBuilder object
                    propositions : defaultdict(WeakValueDictionary)
            
            Returns:
                    Dictionary of key: left, value: right
        """
        if not self._func:
            raise TypeError()

        inputs = dict()

        if hasattr(self._func, '__qualname__'):
            if self._func.__qualname__ in propositions:
                cls = self._func.__qualname__
                for instance_id in propositions[cls]:
                    obj = propositions[cls][instance_id]
                    inputs[obj._var] = []

            elif classname(self._func) in propositions:
                cls = classname(self._func)
                for instance_id in propositions[cls]:
                    obj = propositions[cls][instance_id]
                    # return value of method applied to instance
                    ret = list(flatten([self._func(obj)]))
                    # validate values in ret
                    res = unpack(ret, propositions)
                    inputs[obj._var] = res

        return inputs

    """ Constraint methods

    Implementations of Naive SAT encodings.

    Reference:

    """

    def at_least_one(self, inputs: list) -> NNF:
        """At least one of the inputs are true.

        This is equivalent to a disjunction across all variables

        Arguments:
            inputs : list[nnf.Var]

        Returns:
            nnf.NNF: Or(inputs)
        """
        if not inputs:
            raise ValueError(f"Inputs are empty for {self}")

        return Or(inputs)

    def at_most_one(self, inputs: list) -> NNF:
        """At most one of the inputs are true.

        Arguments:
            inputs : list[nnf.Var]

        Returns:
            nnf.NNF: And(Or(~a, ~b)) for all a,b in input
        """
        if not inputs:
            raise ValueError(f"Inputs are empty for {self}")

        clauses = []
        for var in inputs:
            # negate variables that aren't the current var
            excludes_var = [~x for x in inputs if x != var]
            clause = list(map(lambda c: Or(c), product([~var], excludes_var)))
            clauses.extend(clause)
            self.instance_constraints[str(var)] = clause
        return And(clauses)

    def at_most_k(self, inputs: list, k: int) -> NNF:
        """ At most k variables can be true.

        Arguments:
            inputs : list[nnf.Var]
            k : int

        Returns:
            nnf.NNF:
        """
        if not 1 <= k <= len(inputs):
            raise ValueError(f"The provided k={k} is greater"
                             " than the number of propositional"
                            f" variables (i.e. {len(inputs)} variables)"
                            f" for {self}.")
        elif k == 1:
            return _ConstraintBuilder.at_most_one(inputs)
        if k >= len(inputs):
            warnings.warn(f"The provided k={k} for building the at most K"
                           " constraint is greater than or equal to"
                          f" the number of variables, which is {len(inputs)}."
                          f" We're setting k = {len(inputs) - 1} as a result.")
            k = len(inputs) - 1

        clauses = set() # avoid adding duplicate clauses
        inputs = list(map(lambda var: ~var, inputs))
        # combinations from choosing k from n inputs for 1 <= k <n
        chosen = list(combinations(inputs, k))
        for combo in chosen:
            combo = list(combo)
            excludes_combo = [x for x in inputs if x not in combo]
            for x in excludes_combo:
                clause = Or(combo + [x])
                clauses.add(clause)
                self.instance_constraints[tuple(combo)].append(clause)
        return And(clauses)

    def exactly_one(self, inputs: list) -> NNF:
        """
        Exactly one variable can be true of the input

        Arguments:
            inputs : list[nnf.Var]

        Returns:
            nnf.NNF: And(at_most_one, at_least_one)
        """
        at_most_one = _ConstraintBuilder.at_most_one(self, inputs)
        at_least_one = _ConstraintBuilder.at_least_one(self, inputs)

        if not(at_most_one and at_least_one):
            raise ValueError
        return And({at_most_one, at_least_one})

    def implies_all(self, inputs: dict, left: list, right: list) -> NNF:
        """All left variables imply all right variables.

        Arguments:
            inputs: dict
            left : list[nnf.Var]
            right: list[nnf.Var]

        Returns:
            nnf.NNF: And(Or(~left_i, right_j))

        """
        clauses = []
        
        if not inputs:
            if left and right:
                left_vars = list(map(lambda var: ~var, left))
                clauses = list(map(lambda clause: Or(clause),
                               product(left_vars, right)))
                return And(clauses)
        
        assert isinstance(inputs, dict)

        for key, value in inputs.items():
            left_vars = left + [key]
            right_vars = right + value
            negated_left = list(map(lambda var: ~var, left_vars))
            res = list(map(lambda clause: Or(clause),
                            product(negated_left, right_vars)))
            clauses.extend(res)
            self.instance_constraints[tuple(left_vars)].extend(res)
        return And(clauses)
