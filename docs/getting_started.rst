Getting Started
================

Installing
----------
bauhaus can be installed with pip::

    pip install bauhaus


Using Bauhaus
-------------

First things first, import the bauhaus library::

    from bauhaus import Encoding, proposition, constraint

Create Encoding objects that you intend to transform into a theory.
Encoding objects will store your model's propositional variables and constraints on the fly. ::

    e = Encoding()

Create propositional variables by decorating class definitions with ``@proposition``. ::

    @proposition(e) # Each instance of A is stored as a proposition
    class A(object):
        pass

Create constraints by decorating classes, methods, or invoking the constraint methods. ::

    # Each instance of A implies the right side
    @constraint.implies_all(e, right=['hello'])
    # At most two of the A instances are true
    @constraint.at_most_k(e, 2)
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

    # Add arbitrary constraints on objects anotated with @proposition
    x, y = A(1), A(2)
    e.add_constraint(~x | y)

Compile your theory into conjunctive or negation normal form (note: the theory is truncated), ::

    objects = [A(val) for val in range(1,4)]
    theory = e.compile()
    >> And({And({Or({Var(3), ~Var(A.3)}), Or({Var(1), ~Var(A.1)}),
            ...
            And({Or({~Var(A.1), ~Var(A.2), ~Var(A.3)})})})

And view the origin of each constraint, from the propositional object to the final constraint.
(Note: the introspection is truncated) ::

    e.introspect()
    >>
    constraint.at_most_k:  function = A  k = 2:

    (~Var(A.3), ~Var(A.1)) =>
    Or({~Var(A.1), ~Var(A.2), ~Var(A.3)})


    (~Var(A.3), ~Var(A.2)) =>
    Or({~Var(A.1), ~Var(A.2), ~Var(A.3)})


    (~Var(A.1), ~Var(A.2)) =>
    Or({~Var(A.1), ~Var(A.2), ~Var(A.3)})


    Final at_most_k: And({Or({~Var(A.1), ~Var(A.2), ~Var(A.3)})})
    ...
    ...
