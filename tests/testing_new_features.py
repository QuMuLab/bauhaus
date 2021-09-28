from bauhaus.core import Encoding, proposition, constraint
from nnf import Var, And, Or
import nnf as n

if __name__ == "__main__":
    e = Encoding()

    @proposition(e)
    class A(object):
        def __init__(self, val):
            self.val = val

        def __repr__(self):
            return f"A.{self.val}"

        def __hash__(self):
            return hash(self.val)

        def __eq__(self, other):
            if not isinstance(other, self.__class__):
                return False
            return self.val == other.val

    # figuring out limitations of bauhaus
    w, x, y, z = Var(1), Var(2), Var(3), Var(4)
    a, b, c, d = A(1), A(2), A(3), A(4)    

    # can ONLY make constraints using bauhaus annotated propositions, as these use CustomNNFs
    e.add_constraint(a & b)


    nnf = e.compile()

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

    # test nesting - basic examples
    a, b, c = Var("a"), Var("b"), Var("c")
    nnf = a & b & c
    print()
    print(nnf)
    n.auto_simplify = True
    nnf = a & b & c
    print(nnf)

    n.auto_simplify = False
    nnf = And({Var(1), And({Var(2), Var(3), Or({Var(4), Var(5)})})})
    print("\nbefore")
    e.pprint(nnf)
    n.auto_simplify = True
    flat = And({Var(1), And({Var(2), Var(3), Or({Var(4), Var(5)})})})
    print("after")
    e.pprint(flat)
    assert nnf.equivalent(flat)

    # test nnf nesting - chains of and
    n.auto_simplify = False
    print("\nbefore")
    nnf = Var(1)
    for i in range(10):
        nnf = nnf & Var(i)
    nnf_2 = Var(10)
    for i in range(11, 20):
        nnf_2 = nnf_2 & Var(i)
    nnf_3 = nnf & nnf_2
    e.pprint(nnf_3)
    print("after")
    n.auto_simplify = True
    nnf = Var(1)
    for i in range(10):
        nnf = nnf & Var(i)
    nnf_2 = Var(10)
    for i in range(11, 20):
        nnf_2 = nnf_2 & Var(i)
    nnf_3_flat = nnf & nnf_2
    e.pprint(nnf_3_flat)
    assert nnf_3_flat.equivalent(nnf_3)

    # test nnf nesting - chains of or
    n.auto_simplify = False
    print("\nbefore")
    nnf = Var(1)
    for i in range(10):
        nnf = nnf | Var(i)
    nnf_2 = Var(10)
    for i in range(11, 20):
        nnf_2 = nnf_2 | Var(i)
    nnf_3 = nnf | nnf_2
    e.pprint(nnf_3)
    print("after")
    n.auto_simplify = True
    nnf = Var(1)
    for i in range(10):
        nnf = nnf | Var(i)
    nnf_2 = Var(10)
    for i in range(11, 20):
        nnf_2 = nnf_2 | Var(i)
    nnf_3_flat = nnf | nnf_2
    e.pprint(nnf_3_flat)
    assert nnf_3_flat.equivalent(nnf_3)

    #test nnf nesting - chains of both and's and or's
    n.auto_simplify = False
    nnf = Var(1)
    for i in range(10):
        nnf = nnf & (Var(i) | Var(i + 1))
    print("\nbefore")
    e.pprint(nnf)
    print("after")
    n.auto_simplify = True
    flat = Var(1)
    for i in range(10):
        flat = flat & (Var(i) | Var(i + 1))
    e.pprint(flat)
    assert nnf.equivalent(flat)
    
    n.auto_simplify = False
    nnf = Var(1)
    for i in range(10):
        nnf = nnf | (Var(i) & Var(i + 1))
    print("\nbefore")
    e.pprint(nnf)
    print("after")
    n.auto_simplify = True
    flat = Var(1)
    for i in range(10):
        flat = flat | (Var(i) & Var(i + 1))
    e.pprint(flat)
    assert nnf.equivalent(flat)
