from bauhaus.core import Encoding, proposition
from nnf import Var, flatten_one_level, And, Or

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
    nnf = e.compile()
    nnf = nnf & imply_var
    nnf = nnf.negate()
    print()
    e.pprint(nnf.simplify())
    print(nnf.solve())

    # test nnf nesting - and
    nnf = Var(1)
    for i in range(10):
        nnf = nnf & Var(i)
    nnf_2 = Var(10)
    for i in range(11, 20):
        nnf_2 = nnf_2 & Var(i)
    nnf_3 = nnf & nnf_2
    print("\nbefore")
    e.pprint(nnf_3)
    print("after")
    nnf = Var(1)
    for i in range(10):
        nnf = flatten_one_level(nnf & Var(i))
    nnf_2 = Var(10)
    for i in range(11, 20):
        nnf_2 = flatten_one_level(nnf_2 & Var(i))
    nnf_3_flat = flatten_one_level(nnf & nnf_2)
    e.pprint(nnf_3_flat)
    assert nnf_3_flat.equivalent(nnf_3)

    # test nnf nesting - or
    nnf = Var(1)
    for i in range(10):
        nnf = nnf | Var(i)
    nnf_2 = Var(10)
    for i in range(11, 20):
        nnf_2 = nnf_2 | Var(i)
    nnf_3 = nnf | nnf_2
    print("\nbefore")
    e.pprint(nnf_3)
    print("after")
    nnf = Var(1)
    for i in range(10):
        nnf = flatten_one_level(nnf | Var(i))
    nnf_2 = Var(10)
    for i in range(11, 20):
        nnf_2 = flatten_one_level(nnf_2 | Var(i))
    nnf_3_flat = flatten_one_level(nnf | nnf_2)
    e.pprint(nnf_3_flat)
    assert nnf_3_flat.equivalent(nnf_3)

    
    #test nnf nesting - both and's and or's
    nnf = Var(1)
    for i in range(10):
        nnf = nnf & (Var(i) | Var(i + 1))
    print("\nbefore")
    e.pprint(nnf)
    print("after")
    flat = Var(1)
    for i in range(10):
        flat = flatten_one_level(flat & (Var(i) | Var(i + 1)))
    e.pprint(flat)
    assert nnf.equivalent(flat)
    
    nnf = Var(1)
    for i in range(10):
        nnf = nnf | (Var(i) & Var(i + 1))
    print("\nbefore")
    e.pprint(nnf)
    print("after")
    flat = Var(1)
    for i in range(10):
        flat = flatten_one_level(flat | (Var(i) & Var(i + 1)))
    e.pprint(flat)
    assert nnf.equivalent(flat)

    nnf = And({Var(1), And({Var(2), Var(3), Or({Var(4), Var(5)})})})
    print("\nbefore")
    e.pprint(nnf)
    flat = flatten_one_level(nnf)
    print("after")
    e.pprint(flat)
    assert nnf.equivalent(flat)
