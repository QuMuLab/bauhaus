import weakref
from collections.abc import Iterable
# add try import
import nnf
from functools import wraps
from collections import defaultdict
import warnings
from .constraint_builder import _ConstraintBuilder as cbuilder
from .utils import flatten, ismethod, classname
from .errors import *


class Encoding:
    """
    An Encoding object stores the propositions and constraints
    you create on the fly with ``@proposition`` and ``@constraint``
    decorators and functions.

    When you're ready, you can compile your constraints into
    a logical theory in conjunctive or negation normal form
    to submit to a SAT solver.

    If you're interested in debugging your theory or learning
    about its origin story from each propositional object to
    the final theory, call the ``introspect()`` function on your
    encoding.

    """

    def __init__(self):
        """
        Creates an Encoding object. This will store propositions
        and constraints that you can compile into a theory.

        Attributes
        ----------
        propositions : defaultdict(weakref.WeakValueDictionary)
            Stores decorated classes/functions pointing to
            their associated instances.These are later used
            to build the theory's constraints.

        constraints : set
            A set of unique _ConstraintBuilder objects
            that hold relevant information to build an NNF
            constraint.
            They are added to the Encoding object whenever the
            constraint decorator is used or when it is called
            as a function.
        debug_constraints : dictionary
            Maps ConstraintBuilder objects to their compiled
            constraints for debugging purposes.

        """
        self.propositions = defaultdict(weakref.WeakValueDictionary)
        self.constraints = set()
        self.debug_constraints = dict()
        self._custom_constraints = set()

    def __repr__(self) -> str:
        return (f"Encoding: \n"
                f"  propositions::{self.propositions.keys()} \n"
                f"  constraints::{self.constraints}")

    def clear_propositions(self):
        """ Clears the propositional variables of an Encoding object """
        self.propositions = defaultdict(weakref.WeakValueDictionary)

    def clear_constraints(self):
        """ Clears the constraints of an Encoding object """
        self.constraints = set()

    def clear_debug_constraints(self):
        """Clear debug_constraints attribute in Encoding"""
        self.debug_constraints = dict()

    def add_constraint(self, constraint: nnf.NNF):
        """Add an NNF constraint to the encoding.

        Arguments
        ---------
        cons : NNF
            Constraint to be added.
        """
        if self._custom_constraints is not None:
            raise CustomConstraintOperatorOverloadError(constraint)
        self._custom_constraints.add(constraint)

    def disable_custom_constraints(self):
        """Disable the functionality for using custom_constraints"""
        self._custom_constraints = None

    def compile(self, CNF=True) -> 'nnf.NNF':
        """ Convert constraints into a theory in
        conjunctive normal form, or if specified,
        the simpler negation-normal form.

        Arguments
        ---------
        CNF : bool
            Default is True. Converts a theory to CNF.

        Returns
        -------
        theory : NNF
            Conjunctive or Negation normal form of constraints.

        """
        if not self.constraints and not self._custom_constraints:
            raise EmptyConstraintsError(self)

        if not self.propositions.values():
            raise EmptyPropositionalVariablesError(self)

        theory = []
        self.clear_debug_constraints()

        # custom constraints
        for constraint in self._custom_constraints:
            clause = constraint.compile()
            theory.append(clause)
            self.debug_constraints[constraint] = clause

        # builder constraints
        for constraint in self.constraints:
            clause = constraint.build(self.propositions)
            if CNF:
                clause = clause.to_CNF()
            if clause:
                theory.append(clause)
                try:
                    self.debug_constraints[constraint] = clause
                except Exception as e:
                    raise(e)
            else:
                warnings.warn(f"The {constraint} was not built and"
                            "will not be added to the theory.")
        return nnf.And(theory)

    def introspect(self):
        """Observing the origin of a theory from each
        propositional object to the final constraint.

        Details
        -------
        The mapping is structured like so,

        Encoding.debug_constraints : dictionary

            key -> ConstraintBuilder object

            value -> Clause built in Encoding.compile()

        Each ConstraintBuilder object has the attribute
        instance_constraints : defaultdict with,

            key -> Object (from annotated class or method)

            value -> List of constraint clauses created per object

        This allows you to view the constraints created
        for annotated classes or methods and the per-instance
        object constraints, along with the final (succinct)
        constraint.

        """
        if not self.debug_constraints:
            warnings.warn("Your theory has not been compiled yet,"
                          "so we cannot provide a representation of it."
                          "Try running compile() on your encoding.")
            return self.debug_constraints

        print('\n\t{Encoding Introspection}\n')

        for constraint, clause in self.debug_constraints.items():
            print(f"{constraint}: \n")
            # Check based on original constraint type
            if 'instance_constraints' in dir(constraint):
                if constraint.instance_constraints:
                    for instance, values in constraint.instance_constraints.items():
                            print(f"{instance} =>")
                            for v in values:
                                self.pprint(v)
                            print("\n")
                print(f"Final {constraint._constraint.__name__}: ", end='')
                self.pprint(clause)
            # Otherwise, it must be coming from a custom constraint
            else:
                print('Custom constraint added:')
                self.pprint(clause)
                print()

        print()

    def pprint(self, formula):
        """Pretty print an NNF formula

        Arguments
        ---------
        formula : NNF
            Formula to be displayed.
        """

        def _process(f):
            if isinstance(f, nnf.Var):
                return {True: '', False: '¬'}[f.true] + str(f.name)
            elif isinstance(f, nnf.And):
                return '(' + ' ∧ '.join([_process(i) for i in f]) + ')'
            elif isinstance(f, nnf.Or):
                return '(' + ' ∨ '.join([_process(i) for i in f]) + ')'
            else:
                raise TypeError("Can only pprint an NNF object. Given %s" % type(f))

        print(_process(formula))


class CustomNNF:
    """
    CustomNNF is a thin wrapper around the python-nnf class hierarchy
    that allows us to create arbitrary constraints with the bauhaus-
    modified classes/objects, and then have these placed in the
    theory when .compile() is called on the encoding.

    The CustomNNF class shouldn't be used directly, but rather will
    be implicitly created if/when custom constraints are created and
    added to an encoding.

    The CustomNNF::compile() method converts the nested CustomNNF
    object into a pure python-nnf one.

    Attributes
    ----------
    typ: the type of NNF element [var|and|or|not]
    args: list of arguments for the NNF element
    """

    def __init__(self, typ, args):
        self.typ = typ
        self.args = args

    def __and__(self, other):
        if not isinstance(other, CustomNNF):
            other = CustomNNF('var', [other._var])
        return CustomNNF('and', [self, other])
    def __or__(self, other):
        if not isinstance(other, CustomNNF):
            other = CustomNNF('var', [other._var])
        return CustomNNF('or', [self, other])
    def __invert__(self):
        return CustomNNF('not', [self])
    def __rshift__(self, other):
        if not isinstance(other, CustomNNF):
            other = CustomNNF('var', [other._var])
        return CustomNNF('imp', [self, other])

    def compile(self):
        if self.typ == 'var':
            return self.args[0]
        elif self.typ == 'and':
            return nnf.And(map(lambda x: x.compile(), self.args))
        elif self.typ == 'or':
            return nnf.Or(map(lambda x: x.compile(), self.args))
        elif self.typ == 'not':
            return self.args[0].compile().negate()
        elif self.typ == 'imp':
            return self.args[0].compile().negate() | self.args[1].compile()


def _flatten_and_build_andor(args, andor):
    all_args = []
    for arg in args:
        if isinstance(arg, Iterable):
            all_args.extend(list(arg))
        else:
            all_args.append(arg)
    return CustomNNF(andor, all_args)

def And(*args):
    return _flatten_and_build_andor(args, 'and')

def Or(*args):
    return _flatten_and_build_andor(args, 'or')


def proposition(encoding: Encoding):
    """Create a propositional variable from the decorated
    class or function.

    Adds propositional variable to Encoding.

    Return original object instance.

    Arguments
    ---------
    encoding : Encoding
        Given encoding object.

    Returns
    -------
    The decorated function : function

    Examples
    --------

    Each instance of class A is added to propositions
    in the given Encoding object::

        e = Encoding()
        @proposition(e)
        class A(object):
            pass
        >> e.propositions = {'A': {id: object}}

    """
    def wrapper(cls):

        if ('__and__' in dir(cls)) or ('__or__' in dir(cls)) or ('__invert__' in dir(cls)) or ('__rshift__' in dir(cls)):
            encoding.disable_custom_constraints()
            warnings.warn("Warning: Disabling the use of Encoding::add_constraint because of pre-existing operator overloading.")

        else:
            # To allow for custom constraints over @proposition-enabled objects,
            #  we inject the functionality to use &, |, ~ and >> on instances of
            #  that class. These will ultimately result in CustomNNF objects
            #  being created.
            def _process(o):
                if isinstance(o, CustomNNF):
                    return o
                else:
                    return CustomNNF('var', [o._var])

            def _and(left, right):
                return _process(left) & _process(right)

            def _or(left, right):
                return _process(left) | _process(right)

            def _neg(c):
                return ~ _process(c)

            def _imp(left, right):
                return _process(left) >> _process(right)

            def compile(s):
                return s._var

            cls.__and__ = _and
            cls.__or__ = _or
            cls.__invert__ = _neg
            cls.__rshift__ = _imp
            cls.compile = compile


        @wraps(cls)
        def wrapped(*args, **kwargs):
            ret = cls(*args, **kwargs)
            ret._var = nnf.Var(ret)
            class_name = ret.__class__.__qualname__
            encoding.propositions[class_name][id(ret)] = ret
            return ret
        return wrapped
    return wrapper


class constraint:
    """Creates constraints on the fly when
    used as a decorator or as a function invocation.

    The constraint class directs all function
    invokations of constraint methods to the
    classmethod ``_constraint_by_function``.

    ``@constraint.method`` calls are directed
    to classmethod ``_decorate``.

    In both cases, a ``_ConstraintBuilder`` object
    is created to store the given information.

    Supports the following SAT constraints:
        - At least one
        - At most one
        - Exactly one
        - At most K
        - Implies all

    Examples
    --------
    Decorator for class or method::

        @constraint.at_most_one(e)
        @proposition
        class A:

            @constraint.implies_all(e)
            def do_something(self):
                pass

    Constraint creation by function call
        ``constraint.add_at_least_one(e, *args)``

    """
    def _is_valid_grouby(decorated_class, parameter):
        """ Validates if a groupby can be performed prior to
        storing constraint information.

        We cannot check if the given parameter is an attribute at the
        stage when classes look like functions, so this check
        is completed when compiling an Encoding object in
        bauhaus/constraint_builder.py

        Arguments
        ---------
        decorated_class : function
            Decorated class.
        parameter : function or string
            Can be either a function or attribute to
            partition class objects.

        Returns
        -------
        True if a valid groupby, and raises an Exception if not.

        """
        clsname = classname(decorated_class)
        if ismethod(decorated_class):
            raise GroupbyOnMethodError(decorated_class.__qualname__, clsname)
        if not (isinstance(parameter, str) or callable(parameter)):
            value_type = type(parameter).__name__
            raise GroupbyWithIncorrectTypeError(parameter, value_type, clsname)
        return True


    @classmethod
    def _constraint_by_function(cls,
                               encoding: Encoding,
                               constraint_type,
                               args=None,
                               k=None,
                               left=None,
                               right=None):

        """
        `Private Method`:
        Create ``_ConstraintBuilder`` objects from
        constraint.add_method function calls

        Arguments
        ---------
        encoding : Encoding object
        constraint_type : function
            Reference to the function for building an SAT encoding
            constraint in ``_ConstraintBuilder``
        args : tuple
            Tuple of user-given arguments.
        k : int
            Used for constraint "At most K".
        left : tuple
            Used for constraint "implies all".
            User-given arguments for the left implication.
        right : tuple
            Used for constraint "implies all".
            User-given arguments for the right implication.

        Returns
        -------
        None

        """
        if constraint_type is cbuilder.implies_all:
            constraint = cbuilder(constraint_type, left=left, right=right)
            encoding.constraints.add(constraint)
            return
        elif args:
            args = tuple(flatten(args))
            constraint = cbuilder(constraint_type, args=args, k=k)
            encoding.constraints.add(constraint)
            return
        else:
            raise ConstraintCreationError(constraint_type.__name__, args, left, right)

    @classmethod
    def _decorate(cls,
                  encoding: Encoding,
                  constraint_type,
                  k=None,
                  left=None,
                  right=None,
                  groupby=None):
        """
        `Private Method`:
        Create _ConstraintBuilder objects from constraint.method
        function calls

        Arguments
        ---------
        constraint : function
            Reference to the function for building an SAT encoding
            constraint in _ConstraintBuilder
        func : function
            Decorated class or bound method. Default = None.
        k : int
            Used for constraint "At most K".
        left : tuple
            Used for constraint "implies all".
            User-given arguments for the left implication.
        right : tuple
            Used for constraint "implies all".
            User-given arguments for the right implication.
        groupby : str or func
            Used to group instances of a class for the constraints.

        Returns
        -------
        Wrapper: Returns the function it decorated

        """
        def wrapper(func):

            if groupby:
                assert cls._is_valid_grouby(func, groupby)

            constraint = cbuilder(constraint_type,
                                  func=func,
                                  k=k,
                                  left=left,
                                  right=right,
                                  groupby=groupby)
            encoding.constraints.add(constraint)

            @wraps(func)
            def wrapped(*args, **kwargs):
                ret = func(*args, **kwargs)
                return ret
            return wrapped
        return wrapper

    def at_least_one(encoding: Encoding, **kwargs):
        """At least one of the propositional variables are True.

        Constraint is added with the @constraint decorator.

        Arguments
        ---------
        encoding : Encoding
            Given encoding.

        Example
        -------
        ``@constraint.at_least_one(encoding)``

        """
        return constraint._decorate(encoding, cbuilder.at_least_one, **kwargs)

    def at_most_one(encoding: Encoding, **kwargs):
        """At most one of the propositional variables are True.

        Constraint is added with the @constraint decorator.

        Arguments
        ---------
        encoding : Encoding
            Given encoding.

        Example
        -------

        ``@constraint.at_most_one(encoding)``

        """
        return constraint._decorate(encoding, cbuilder.at_most_one, **kwargs)

    def exactly_one(encoding: Encoding, **kwargs):
        """ Exactly one of the propositional variables are True.

        Constraint is added with the @constraint decorator.

        Arguments
        ---------
        encoding : Encoding
            Given encoding.

        Example
        -------

        ``@constraint.exactly_one(encoding)``

        """
        return constraint._decorate(encoding, cbuilder.exactly_one, **kwargs)

    def at_most_k(encoding: Encoding, k: int, **kwargs):
        """At most K of the propositional variables are True

        Constraint is added with the @constraint decorator.

        Arguments
        ---------
        encoding : Encoding
            Given encoding.
        k : int
            The number of variables that are true at one time.
            Must be less than the number of total variables for
            the constraint.

        Example
        -------

        ``@constraint.at_most_k(encoding, k)``

        """
        if not isinstance(k, int):
            raise TypeError(f"The provided k={k} is not an integer.")
        if k < 1:
            raise ValueError(f"The provided k={k} is less than 1.")
        if k == 1:
            warnings.warn(f"Warning: The provided k={k} will"
                           " result in an 'at most one' constraint,"
                           " but we'll proceed anyway.")
        return constraint._decorate(encoding,
                                    cbuilder.at_most_k,
                                    k=k, **kwargs)

    def implies_all(encoding: Encoding, left=None, right=None, **kwargs):
        """Left proposition(s) implies right proposition(s)

        Constraint is added with the @constraint decorator.

        Arguments
        ---------
        encoding : Encoding
            Given encoding.
        left : list
            Propositional variables for the left side of an
            implication.
        right : list
            Propositional variables for the right side of an
            implication.

        Example
        -------
        Above a class, each instance will be on the left
        side of an implication. You need to define a right
        side of the implication if you are decorating a class.::

            @constraint.implies_all(encoding, right=[Obj])
            @proposition(e)
            class A(Object):
                pass

        Above a method in a class, each instance will be on
        the left side of an implication. The return value(s)
        will be the right side of the implication. You can
        provide additional variables for either the left or
        right side.::

            @proposition(e)
            class A(object):

                def __init__(self, data):
                    self.data = data

                @constraint.implies_all(encoding)
                def foo(self):
                    return self.data

        """
        left = tuple(flatten([left])) if left else None
        right = tuple(flatten([right])) if right else None
        return constraint._decorate(encoding,
                                    cbuilder.implies_all,
                                    left=left, right=right, **kwargs)



    def none_of(encoding: Encoding, **kwargs):
        """None of the propositional variables are True.

        Constraint is added with the @constraint decorator.

        Arguments
        ---------
        encoding : Encoding
            Given encoding.

        Example
        -------
        ``@constraint.none_of(encoding)``

        """
        return constraint._decorate(encoding, cbuilder.none_of, **kwargs)

    # Creating constraints from function invokations
    # Constraint creation for these are directed to
    # constraint._constraint_by_function.

    def add_at_least_one(encoding: Encoding, *args):
        """At least one of the propositional variables are True

        Constraint is added directly with this function.

        Arguments
        ---------
        encoding : Encoding
            Given encoding.

        Example
        -------
        ``@constraint.add_at_least_one(encoding, [Obj, Class, Class.method])``

        """
        return constraint._constraint_by_function(encoding,
                                                 cbuilder.at_least_one,
                                                 args=args)

    def add_at_most_one(encoding: Encoding, *args):
        """At most one of the propositional variables are True

        Constraint is added directly with this function.

        Arguments
        ---------
        encoding : Encoding
            Given encoding.

        Example
        -------
        ``@constraint.add_at_most_one(encoding, [Obj, Class, Class.method])``

        """
        return constraint._constraint_by_function(encoding,
                                                 cbuilder.at_most_one,
                                                 args=args)

    def add_exactly_one(encoding: Encoding, *args):
        """ Exactly one of the propositional variables are True

        Constraint is added directly with this function.

        Arguments
        ---------
        encoding : Encoding
            Given encoding.

        Example
        -------
        ``@constraint.add_exactly_one(encoding, [Obj, Class, Class.method])``

        """
        return constraint._constraint_by_function(encoding,
                                                 cbuilder.exactly_one,
                                                 args=args)

    def add_at_most_k(encoding: Encoding, k: int, *args):
        """At most K of the propositional variables are True

        Constraint is added directly with this function.

        Arguments
        ---------
        encoding : Encoding
            Given encoding.
        k : int
            The number of variables that are true at one time.
            Must be less than the number of total variables for
            the constraint.

        Example
        -------
        ``@constraint.add_at_most_k(encoding, k, [Obj, Class, Class.method])``

        """
        if not isinstance(k, int):
            raise TypeError(f"The provided k={k} is not an integer.")
        if k < 1:
            raise ValueError(f"The provided k={k} is less than 1.")
        if k == 1:
            warnings.warn(f"Warning: The provided k={k} will"
                           " result in an 'at most one' constraint,"
                           " but we'll proceed anyway.")
        return constraint._constraint_by_function(encoding,
                                                 cbuilder.at_most_k,
                                                 args=args, k=k)

    def add_implies_all(encoding: Encoding, left, right):
        """Left proposition(s) implies right proposition(s)

        Constraint is added directly by calling this function.

        Arguments
        ---------
        encoding : Encoding
            Given encoding.
        left : list
            Propositional variables for the left side of an
            implication.
        right : list
            Propositional variables for the right side of an
            implication.

        Example
        -------
        ``constraint.add_implies_all(encoding, left=[Obj, 'hello'], right=['goodbye'])``

        """
        if not (left and right):
            raise ImplicationConstraintCreationError(left, right)
        left = tuple(flatten([left]))
        right = tuple(flatten([right]))
        return constraint._constraint_by_function(encoding,
                                                 cbuilder.implies_all,
                                                 left=left, right=right)

    def add_none_of(encoding: Encoding, *args):
        """None of the propositional variables are True

        Constraint is added directly with this function.

        Arguments
        ---------
        encoding : Encoding
            Given encoding.

        Example
        -------
        ``@constraint.add_none_of(encoding, [Obj, Class, Class.method])``

        """
        return constraint._constraint_by_function(encoding,
                                                 cbuilder.none_of,
                                                 args=args)
