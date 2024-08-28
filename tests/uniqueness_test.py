from bauhaus import Encoding, proposition, constraint
import pytest
    
def test_constraint_construction_1():
    
    e = Encoding()

    @proposition(e)
    class V(object):
        def _prop_name(self):
            return f"V.{self.val}"

    x = V('x')
    y = V('y')
    z = V('z')
    e.add_constraint(x | y)
    e.add_constraint(x | z)

    const1 = e._custom_constraints.pop()
    const2 = e._custom_constraints.pop()

    #assert that Var(V.x) is the same in both constraints
    assert [x.args for x in const1.args][0][0] == [x.args for x in const2.args][0][0]

def test_constraint_construction_2():
    
    e = Encoding()

    @proposition(e)
    class V(object):
        def _prop_name(self):
            return f"V.{self.val}"

    e.add_constraint(V('x') | V('y'))
    e.add_constraint(V('x') | V('z'))

    const1 = e._custom_constraints.pop()
    const2 = e._custom_constraints.pop()

    #assert that Var(V.x) is the same in both constraints
    assert [x.args for x in const1.args][0][0] == [x.args for x in const2.args][0][0]

if __name__ == "__main__":
    constraint_construction_1()
    constraint_construction_2()
