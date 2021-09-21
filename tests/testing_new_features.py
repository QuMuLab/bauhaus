from bauhaus.core import Encoding, proposition
from nnf import Var, flatten, And, Or

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
    e.pprint(nnf_formula.simplify())
    print(nnf_formula.solve())

    # test nnf nesting - and
    nnf_formula = Var(1)
    for i in range(10):
        nnf_formula = nnf_formula & Var(i)
    nnf_formula_2 = Var(10)
    for i in range(11, 20):
        nnf_formula_2 = nnf_formula_2 & Var(i)
    nnf_formula_3 = nnf_formula & nnf_formula_2
    print("\nbefore")
    e.pprint(nnf_formula_3)
    print("after")
    flat = flatten(nnf_formula_3)
    e.pprint(flat)
    assert nnf_formula_3.equivalent(flat)

    # test nnf nesting - or
    nnf_formula = Var(1)
    for i in range(10):
        nnf_formula = nnf_formula | Var(i)
    nnf_formula_2 = Var(10)
    for i in range(11, 20):
        nnf_formula_2 = nnf_formula_2 | Var(i)
    nnf_formula_3 = nnf_formula | nnf_formula_2
    print("\nbefore")
    e.pprint(nnf_formula_3)
    print("after")
    flat = flatten(nnf_formula_3)
    e.pprint(flat)
    assert nnf_formula_3.equivalent(flat)

    #test nnf nesting - both and's and or's
    nnf_formula = Var(1)
    for i in range(10):
        nnf_formula = nnf_formula & (Var(i) | Var(i + 1))
    print("\nbefore")
    e.pprint(nnf_formula)
    print("after")
    flat = flatten(nnf_formula)
    e.pprint(flat)
    assert nnf_formula.equivalent(flat)

    nnf_formula = Var(1)
    for i in range(10):
        nnf_formula = nnf_formula | (Var(i) & Var(i + 1))
    print("\nbefore")
    e.pprint(nnf_formula)
    print("after")
    flat = flatten(nnf_formula)
    e.pprint(flat)
    assert nnf_formula.equivalent(flat)

    x, a, y, z, b, c = Var("x"), Var("a"), Var("y"), Var("z"), Var("b"), Var("c")
    nnf_formula = x | ((a & y) & z & (b | c))
    print("\nbefore")
    e.pprint(nnf_formula)
    print("after")
    flat = flatten(nnf_formula)
    e.pprint(flat)
    assert nnf_formula.equivalent(flat)

