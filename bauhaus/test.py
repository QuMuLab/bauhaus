from core import Encoding, proposition, constraint

e = Encoding()

@constraint.at_most_one(e)
@proposition(e)
class A(object): pass

objects = [A() for i in range(0,3)]
theory = e.compile()