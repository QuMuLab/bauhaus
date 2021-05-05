from bauhaus.core import Encoding, constraint, proposition
from bauhaus.constraint_builder import _ConstraintBuilder as cbuilder
from nnf import Var
import pytest
"""
Unit tests for core functionalities and building constraints.

See reference:
https://github.com/mrocklin/multipledispatch/blob/master/multipledispatch/tests/test_core.py
"""

# Test Encoding class
t, s = Encoding(), Encoding()
class T(object): pass

@proposition(s)
class S(object): pass

def test_compile():
    # Cases for empty propositions or constraints
    with pytest.raises(ValueError):
        t.compile()
        s.compile()


# Test proposition decorator
e = Encoding()

@proposition(e)
class E(object): pass

def test_proposition():
    """ Test @proposition """
    objects = [E() for i in range(0,3)]
    assert e.propositions['E'] is not None
    assert len(e.propositions['E']) == 3


# Test multiple constraints on a class
# and decorator constraints
a = Encoding()

@constraint.at_least_one(a)
@constraint.at_most_k(a, 2)
@proposition(a)
class A(object):

    @constraint.implies_all(a)
    def foo(self):
        return self

@constraint.none_of(a)
@proposition(a)
class A2(object): pass

def test_storing_decorator_constraint():
    objects = [A() for i in range(0,3)]
    assert len(a.constraints) == 3
    for c in a.constraints:
        if c._constraint == cbuilder.implies_all:
            assert c._left == c._right == None
            assert c._func.__qualname__ == A.foo.__qualname__
        elif c._constraint == cbuilder.at_least_one:
            assert c._func.__qualname__ == A.__qualname__
            assert c._vars == None
        elif c._constraint == cbuilder.at_most_k:
            print(c._func)
            assert c._func.__qualname__ == A.__qualname__
            assert c._k == 2
            assert c._vars == None
        elif c._constraint == cbuilder.none_of:
            assert c._func.__qualname__ == A2.__qualname__
            assert c._vars == None
        else:
            print(c._constraint)
            raise Exception()


# Test adding constraints by function
b = Encoding()

@proposition(b)
class B(object): pass

def test_storing_function_constraint():
    # assert failures when creating,
    # add_method(e) with no arguments
    # add_implies_all(e) with no left or right
    # add_at_most_k with incorrect k
    test = Var('test')
    with pytest.raises(ValueError):
        constraint.add_at_least_one(b)
        constraint.add_at_most_k(b, 0)
        constraint.add_implies_all(b)
        constraint.add_implies_all(b, left=[], right=[test])
        constraint.add_none_of(b)
    assert len(b.constraints) == 0

    constraint.add_implies_all(b, left=test, right=test)
    assert len(b.constraints) == 1
    for c in b.constraints:
        assert c._constraint is cbuilder.implies_all
        assert c._left == c._right
        assert c._left == (test,)
