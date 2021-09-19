from bauhaus.core import Encoding, proposition
from nnf import Var

if __name__ == "__main__":
    e = Encoding()

    @proposition(e)
    class A(object):
        def __init__(self, val):
            self.val = val

        def __repr__(self):
            return f"A.{self.val}"

    # works
    w, x, y, z = Var(1), Var(2), Var(3), Var(4)
    imply_var = (w >> x) & (y | ~z)

    # works
    a, b, c, d = A(1), A(2), A(3), A(4)      
    imply_prop = (a >> b) & (c | ~d)

    e.add_constraint(imply_prop)
    nnf_formula = e.compile()
    nnf_formula = nnf_formula & imply_var
    nnf_formula = nnf_formula.negate()

    print()
    print(nnf_formula.to_CNF())
    print(nnf_formula.solve())