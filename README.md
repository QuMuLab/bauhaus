# Bauhaus

`bauhaus` is a Python package for spinning up logical NNF models from object-oriented Python code. 

## Usage
Create Encoding objects that you intend to compile to an SAT. Encoding objects will store your model's propositional variables and constraints on the fly. 

Using object-oriented principles, you can create propositional variables from decorating
class definitions with `@proposition`. 

You can create constraints by decorating classes, methods, or invoking the constraint method. 

Valid parameters are decorated classes or methods, instances of those classes, an nnf.Var variable, or an iterable containing any of these parameters. 

The functionalities of bauhaus are shown in the following example:

    from bauhaus import Encoding, proposition, constraint

    e = Encoding()

    @constraint.at_least_one(e) # Disjunction across all instances of class A
    @proposition(e) # Each instance of A is stored as a proposition
    class A:
        
        # Each instance of A implies the result of the method
        @constraint.implies_all(e)
        def method(self):
            return self.val
        
        def __init__(self):
            ...
    # At most one of the inputs is true. 
    constraint.at_most_one(e, A, A(), Var('B'), [A(), Var('C')]) 
    theory = e.compile() # NNF theory!


## Requirements
- `python-nnf`
- `python >= 3.0`

## Citing This Work
`bauhaus` was created by Karishma Daga under mentorship of Christian Muise at Queen's University, Kingston.