Architecture Design
===================

Author: Karishma Daga

Github: https://github.com/QuMuLab/bauhaus

What is bauhaus?
----------------
Bauhaus is a library for building logical theories on the fly with Python.
The library allows people to take advantage of object-oriented principles to build theories about real-life
relationships and systems without the hassle of repetitive code. 

It is a companion library to ``nnf``, a library for building and manipulating logical NNF sentences.

How bauhaus works
-----------------
Bauhaus was designed to be simple and easy to work with for creating logical theories from object-oriented code.
Logical theories consist of propositional variables that are structured into constraints to represent relationships.
To find models that satisfy these formulas using an SAT solver, we represent the constraints in conjunctive normal
form (CNF).

The Bauhaus library can be broken down into three parts:

- Encoding objects
- Creating propositions and constraints
- Building the theory

Encoding objects store a theory's propositions and constraints, and once you're SATisfied (haha),
you can compile the Encoding object into a conjunctive or negation normal theory.

It's possible to build multiple theories at the same time by passing different
Encoding objects as parameters to proposition and constraint decorators and functions. 

Design decisions
----------------

Keep the interface simple
#########################
Keeping the user flow simple and expressive was important.
You only have to interact with three objects or functions
to be able to build complex logical theories.

Build constraints dynamically
#############################
Building a constraint dynamically means that we store
information about a constraint and wait until a user hits
``compile()`` on an Encoding object to build the constraint.
The benefit is in reducing redundant clauses and complexity
in the software. It also makes it simpler to debug as someone
can clearly catch when and where an error occurs.

Theory introspection
####################
Theories can grow incredibly large, so it's important
to be able to understand where a clause or constraint came from.
Introspection for bauhaus allows a user to view the per-instance
constraints and the final constraint that was added to the theory.



System Overview
---------------

Encoding Class
##############
An ``Encoding`` object has two public attributes: ``propositions`` and ``constraints``. 

Each time a class decorated with ``@proposition`` is instantiated, we need to 
store a reference to the object in ``Encoding.propositions`` so that we can 
build constraints associated with that object or class later.


**Storing Instances and Garbage Collection**

As Python doesn’t have a builtin method for storing instances of classes
and we wanted to store propositional variables (instantiated objects) 
in such a way that if they are not referenced anymore, we don’t want our
reference in ``Encoding.propositions`` to keep the object from being garbage collected.
The object could also not be relevant anymore to a user as well, which could
result in incorrect constraints if it’s kept in propositions. 

The solution to this is to use WeakValueDictionaries to weakly reference the 
``id`` of an object to the object. The propositions attribute looks like, ::

    encoding.propositions = {classname -> WeakValueDictionary(id -> obj,
                                                              id -> obj,
                                                              …
                                                              id -> obj)

``@proposition`` decorator
##########################
The proposition decorator wraps a class such that each time
the class is instantiated, it adds the instance to the given
Encoding's proposition attribute.


Constraint Class
################

**Creating Constraints**

A user can create constraints by decorating a class or method or by
calling a function. Since we're not compiling the constraint right away, the point
of both the decorators and functions are to create a ConstraintBuilder object
which will store the user-given information about the constraint.

So, we direct decorator and function calls to their own class methods with the
given parameters to,

- Build a ConstraintBuilder object
- Store that object in the given Encoding.
- In the case of constraint decorators, we are wrapping a ``@proposition`` decorator, so we must instantiate and return it so that a user can apply as many constraints as they'd like to a class

**Building Constraints**

Once a user hits compile on an Encoding, we iterate over each ConstraintBuilder
object in the Encoding's constraints attribute.

Building a constraint is a two step process:

- Get the propositional variables
- Construct the constraint


Both steps are relatively simple.

We check if a ConstraintBuilder was made from a decorator or not. If it was, then the only
variables we need are stored in the Encoding's propositions attribute.
If it was made from a function call, then we validate and return the user-given
arguments stored in the ConstraintBuilder. A user could have provided
a decorated class or method as an argument.

The only distinct implementation is for implies all, which requires
a left and right side of an implication, so there is a separate
function to retrieve its inputs and store them as a dictionary.

Constructing the constraint involves taking the given propositional
variables and using naive implementations of their SAT encoding constraints,
which were referenced from the following paper:

`Efficient CNF Encoding <http://www.cs.cmu.edu/~wklieber/papers/2007_efficient-cnf-encoding-for-selecting-1.pdf>`_


