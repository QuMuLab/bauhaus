from bauhaus import Encoding, proposition, constraint

e = Encoding()

@proposition(e)
class V(object):
    def __init__(self, val):
        self.val = val

    def __repr__(self):
        return self._prop_name()

    def _prop_name(self):
        return f"V.{self.val}"

# Works: x refers to the same proposition
x = V('x')
y = V('y')
z = V('z')
e.add_constraint(x | y)
e.add_constraint(x | z)

e.pprint(e.compile())


elem1 = e._custom_constraints.pop()
elem2 = e._custom_constraints.pop()
print([x.args for x in elem1.args])
print([x.args for x in elem2.args])

assert([x.args for x in elem1.args][0] == [x.args for x in elem2.args][0])

e._custom_constraints = set()

# Doesn't work: each x is a unique proposition
e.add_constraint(V('x') | V('y'))
e.add_constraint(V('x') | V('z'))

e.pprint(e.compile())

elem1 = e._custom_constraints.pop()
elem2 = e._custom_constraints.pop()
print([x.args for x in elem1.args])
print([x.args for x in elem2.args])

assert([x.args for x in elem1.args][0] == [x.args for x in elem2.args][0])

