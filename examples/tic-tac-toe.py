from bauhaus import Encoding, constraint, proposition

e = Encoding()

class StrHash(object):
    def __hash__(self):
        return hash(str(self))

@proposition(e)
class Mark(StrHash):
    def __init__(self, i, j):
        self.i = i
        self.j = j
    def __repr__(self):
        return f'x_{self.i}_{self.j}'

@constraint.at_most_one(e)
@proposition(e)
class Row(StrHash):

    #@constraint.implies_all(e)    # Says that r_i implies the conjunction of variables corresponding to the marks returned
    def row_is_marked(self):
        return self.marks

    def __init__(self, i, all_marks):
        self.i = i
        self.marks = [m for m in all_marks if m.i == self.i]
    def __repr__(self):
        return f'r_{self.i}'

@constraint.at_most_one(e)
@proposition(e)
class Col(StrHash):
    
    #@constraint.implies_all(e)    # Says that r_i implies the conjunction of variables corresponding to the marks returned
    def col_is_marked(self):
        return self.marks
    
    def __init__(self, j, all_marks):
        self.j = j
        self.marks = [m for m in all_marks if m.j == self.j]
    def __repr__(self):
        return f'c_{self.j}'

def main():
    marks = [Mark(i,j) for i in range(1,4) for j in range(1,4)]
    rows = [Row(i, marks) for i in range(1,4)]
    cols = [Col(j, marks) for j in range(1,4)]
    theory = e.compile()
    print(theory)
    print()
    debug = e.pretty_debug()

main()