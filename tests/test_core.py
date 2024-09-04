from bauhaus.core import CustomNNF, Encoding, constraint, proposition, And, Or
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
class T(object): 
    def _prop_name(self):
        return f"T"
    pass

@proposition(s)
class S(object): 
    def _prop_name(self):
        return f"S"
    pass

def test_compile():
    # Cases for empty propositions or constraints
    with pytest.raises(ValueError):
        t.compile()
        s.compile()


# Test proposition decorator
e = Encoding()

@proposition(e)
class E(object): 
    def __init__(self, val):
        self.val = val
    def _prop_name(self):
        return f"E.{self.val}"
    pass

def test_proposition():
    """ Test @proposition """
    objects = [E(i) for i in range(0,3)]
    assert e.propositions['E'] is not None
    assert len(e.propositions['E']) == 3


# Test multiple constraints on a class
# and decorator constraints
a = Encoding()

@constraint.at_least_one(a)
@constraint.at_most_k(a, 2)
@proposition(a)
class A(object):
    def __init__(self, val):
        self.val = val
    def _prop_name(self):
        return f"A.{self.val}"

    @constraint.implies_all(a)
    def foo(self):
        return self

@constraint.none_of(a)
@proposition(a)
class A2(object): 
    def __init__(self, val):
        self.val = val
    def _prop_name(self):
        return f"A2.{self.val}"
    pass

def test_storing_decorator_constraint():
    objects = [A(i) for i in range(0,3)]
    assert len(a.constraints) == 4
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
class B(object): 
    def __init__(self):
        pass
    def _prop_name(self):
        return f"B"
    pass

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


# Test adding raw constraints
c = Encoding()

@constraint.exactly_one(c)
@proposition(c)
class C: 
    def __init__(self, val):
        self.val = val
    def _prop_name(self):
        return f"C.{self.val}"
    pass

@proposition(c)
class D: 
    def __init__(self):
        pass
    def _prop_name(self):
        return f"D"
    pass

def test_raw_constraints():
    c1, c2, d1 = C(1), C(2), D()
    c.add_constraint(~c1 | (c2 & d1))
    T = c.compile()
    assert T.satisfiable()

def test_imp():
    c3, c4, d2 = C(3), C(4), D()
    c.add_constraint(c3 >> (c4 & d2))
    T1 = c.compile()
    assert T1.satisfiable()

def test_andor():
    c1, c2, d1 = C(5), C(6), D()
    c.add_constraint(And(~c1, (c2 & d1)))
    c.add_constraint(Or(c1 >> c2, d1))
    c.add_constraint(And(Or([c1, c2]), d1))
    c.add_constraint(Or(And({c1, c2}), d1))
    T = c.compile()
    assert T.satisfiable()

# Test forbidding raw constraints

d = Encoding()

with pytest.warns(UserWarning):
    @proposition(d)
    class F:
        def __init__(self):
            pass
        def _prop_name(self):
            return f"F"
        def __invert__(self):
            return -1

def test_failed_raw_constraints():
    x, y = F(), F()
    with pytest.raises(TypeError):
        d.add_constraint(x | y)

g = Encoding()
@proposition(g)
class H:
    def __init__(self, val):
        self.val = val
    def _prop_name(self):
        return f"H.{self.val}"
    
def test_duplicates():
    # want to ensure that warnings are raised whenever we send the
    # constraint.add_* functions literals instead of variables.
    h1 = H(1)
    h2 = H(2)
    h3 = H(3)
    h4 = H(4)

    with pytest.warns(UserWarning):
        constraint.add_at_most_one(g, h1, h2, h3 & h4);
        g.compile()

    with pytest.warns(UserWarning):
        constraint.add_at_most_k(g, 2, h1, h2, h3 & h4);
        g.compile()

    with pytest.warns(UserWarning):
        constraint.add_at_least_one(g, h1, h2, h3 & h4);
        g.compile()

    with pytest.warns(UserWarning):
        constraint.add_exactly_one(g, h1, h2, h3 & h4);
        g.compile()

    with pytest.warns(UserWarning):
        constraint.add_implies_all(g, left=h1, right=h3 & h4);
        g.compile()
       
    with pytest.warns(UserWarning):
        constraint.add_none_of(g, h1, h2, h3 & h4);
        g.compile()
