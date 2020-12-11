from bauhaus import Encoding, constraint, proposition

"""
A k-colouring of a graph is a labelling of its vertices
with at most k colours, such that no two vertices
sharing the same edge have the same colour.

The minimum number of colours necessary to colour 
a graph is known as the chromatic number of the graph.
We can find the chromatic number by encoding the
problem in Boolean logic.

We can reduce this problem to SAT as follows,
- Constraint 1: every vertex has been coloured with one of the colours
- Constraint 2: if (u, v) is an edge, then u and v have different colors
- Constraint 3: each vertex has not been assigned two colours
                -> ~vertex_i_k | ~vertex_i_j (where k, j are distinct colours)

"""
e = Encoding()
valid_colours = [1,2,3,4,5]

class StrHash(object):
    def __hash__(self):
        return hash(str(self))

@constraint.exactly_one(e)
@proposition(e)
class Vertex:
    
    def __init__(self, index: int, colour: int):
        self.index = index
        self.colour = colour
    
    def __repr__(self):
        return f'v_{self.colour}'


@proposition(e)
class Edge:

    def __init__(self, u: Vertex, v: Vertex):
        self.u = u
        self.v = v
    
    def __repr__(self):
        return f'e_({vertex_i}, {vertex_j})'
    
    def vertex_colouring(self):
        pass
    
def main():
    # create vertices and edges
    #vertices = [Vertex(i) for i in range(1, 10)]
    #edges =
    theory = e.compile()
    

