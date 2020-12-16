# Bauhaus
`bauhaus` is a Python package for spinning up propositional logic encodings from object-oriented Python code. 

## Features
- Create propositional variables from Python classes
- Build naive SAT encoding constraints from propositional variables
   - At most one
   - At least one
   - Exactly one
   - At most K
   - Implies all
- Compile constraints into a theory in conjunctive or negation normal form
- With `python-nnf`, submit a theory to a SAT solver
- Theory introspection

## Installation

Install `bauhaus` by running
```
pip install bauhaus
```

## How is it used?

Create Encoding objects that you intend to compile to an SAT. Encoding objects will store your model's propositional variables and constraints on the fly.

```
from bauhaus import Encoding, proposition, constraint
e = Encoding()
```

Create propositional variables by decorating class definitions with `@proposition`.

```
@proposition(e) # Each instance of A is stored as a proposition
class A(object): pass
```

Create constraints by decorating classes, methods, or invoking the constraint methods.

```
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
```

Compile your theory into conjunctive or negation normal form (note: the theory is truncated),

```
objects = [A(val) for val in range(1,4)]
theory = e.compile()
>> And({And({Or({Var(3), ~Var(A.3)}), Or({Var(1), ~Var(A.1)}),
        ...
        And({Or({~Var(A.1), ~Var(A.2), ~Var(A.3)})})})
```

And view the origin of each constraint, from the propositional object to the final constraint.
(Note: the introspection is truncated)

```
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
```

## Contribute
Head over to our [code of conduct](CODE_OF_CONDUCT.md) and get a feel for the
library by reading our [architecture design](https://bauhaus.readthedocs.io/en/latest/architecture.html)
and [documentation](https://bauhaus.readthedocs.io/en/latest/index.html).
- Issue Tracker: https://github.com/QuMuLab/bauhaus/issues
- Source Code: https://github.com/QuMuLab/bauhaus
- Join us! http://mulab.ai/

## Support
If you are having issues, please let us know.
Reach out to us at karishma.daga@queensu.ca or by creating a GitHub issue.

## License
The project is licensed under the MIT license for the Queen's Mu Lab

### Citing This Work
`bauhaus` was created by Karishma Daga under mentorship of Christian Muise at Queen's University, Kingston.