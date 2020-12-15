# Bauhaus

`bauhaus` is a Python package for spinning up propositional logic encodings from object-oriented Python code. 

## Usage
Create Encoding objects that you intend to compile to an SAT. Encoding objects will store your model's propositional variables and constraints on the fly. 

    from bauhaus import Encoding, proposition, constraint

    e = Encoding()

Using object-oriented principles, you can create propositional variables from decorating
class definitions with `@proposition`. 

    @proposition(e) # Each instance of A is stored as a proposition
    class A(object): pass

You can create constraints by decorating classes, methods, or invoking the constraint methods.

    @constraint.implies_all(e, right=['hello']) # Each instance of A implies the right side
    @constraint.at_most_k(e, 2) # At most two of the A instances are true
    @proposition(e)
    class A(object):

    def __init__(self, val):
        self.val = val

    def __repr__(self):
        return f"A.{self.val}"

    # Each instance of A implies the result of the method
    @constraint.implies_all(e)
    def method(self):
        return self.val
    
    # At most one of the inputs is true. 
    constraint.add_at_most_one(e, A, A.method, Var('B'))

Compile your theory into conjunctive or negation normal form,

    objects = [A(val) for val in range(1,4)]
    theory = e.compile()
    >> And({And({Or({Var(3), ~Var(A.3)}), Or({Var(1), ~Var(A.1)}), ... Or({~Var(A.2), hello})}), And({Or({~Var(A.1), ~Var(A.2), ~Var(A.3)})})})

And view the origin of each constraint, from the propositional object to the final constraint. (Note: the '...' is to shorten the output)

    e.introspect()
    >> 
    constraint.implies_all:  function = A.foo   left implication = None   right implication = None: 

    (Var(A.1),) =>
    Or({Var(1), ~Var(A.1)})

    ...

    Final implies_all: And({Or({Var(3), ~Var(A.3)}), Or({Var(1), ~Var(A.1)}), Or({~Var(A.2), Var(2)})}) 

    constraint.implies_all:  function = A   left implication = None   right implication = ('hello',): 

    (Var(A.1),) =>
    Or({~Var(A.1), hello})

    ...

    Final implies_all: And({Or({hello, ~Var(A.3)}), Or({~Var(A.1), hello}), Or({~Var(A.2), hello})}) 

    constraint.at_most_k:  function = A  k = 2: 

    (~Var(A.3), ~Var(A.1)) =>
    Or({~Var(A.1), ~Var(A.2), ~Var(A.3)})


    (~Var(A.3), ~Var(A.2)) =>
    Or({~Var(A.1), ~Var(A.2), ~Var(A.3)})


    (~Var(A.1), ~Var(A.2)) =>
    Or({~Var(A.1), ~Var(A.2), ~Var(A.3)})


    Final at_most_k: And({Or({~Var(A.1), ~Var(A.2), ~Var(A.3)})}) 

    ...


## Requirements
- `python-nnf`
- `python >= 3.0`
- `pysat`

## Citing This Work
`bauhaus` was created by Karishma Daga under mentorship of Christian Muise at Queen's University, Kingston.
