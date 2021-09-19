from bauhaus.bauhaus.core import Encoding, proposition, constraint
from nnf import Var

e = Encoding()

@proposition(e)
class A(object):
    def __init__(self, val):
        self.val = val

    def __repr__(self):
        return f"A.{self.val}"

a, b, c, d = A(1), A(2), A(3), A(4)
w, x, y, z = Var(1), Var(2), Var(3), Var(4)
neg_var = ~w
#imply_var = w >> x

# e.add_constraint(x >> y)