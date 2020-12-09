Welcome to ``bauhaus``!
=========================================
``bauhaus`` is a Python library for building logical theories on the fly from object-oriented code. Theories can be passed to SAT solvers using the companion library ``python-nnf``.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installing
   module_index
   architecture

How is it used?
---------------

Create an Encoding object to store propositions and SAT constraints: ::

   from bauhaus import Encoding

   e = Encoding()

Create propositions by decorating classes with ``@proposition(encoding)`` and an Encoding object.
Each instance of decorated class is stored as a propositional variable in the Encoding::

   @proposition(e)
   class Object:
      pass

Create SAT constraints by decorating classes, methods, or invoking ``@constraint`` as a function.
To create a constraint for a method, the return object must be from a decorated class or a propositional variable created with ``python-nnf``::

   @constraint.at_most_one(e) # At most one of the Object instances are true
   @proposition(e)
   class Object:
      
      def __init__(self, x):
         from nnf import Var
         self.x = Var(x)
      
      def __repr__(self): return f'Object.{self.x}'
      
      @constraint.implies_all(e): # Each instance implies self.x
      def func(self):
         return self.x
      
      # create object instances
      objects = [Object(i) for i in 'abc'] # Object_a,..., Object_c
      constraint.at_least_one(e, Object, [objects[3], objects[2]])
      theory = e.compile(CNF=True)
      # spaced for clarity,
      >> theory = And({And({Or({~Var(Object.c), c}),
                            Or({~Var(Object.a), a}),
                            Or({~Var(Object.b), b})}),
                      And({Or({~Var(Object.c), ~Var(Object.a)}),
                           Or({~Var(Object.c), ~Var(Object.b)}),
                           Or({~Var(Object.a), ~Var(Object.b)})}),
                      Or({Var(Object.c), Var(Object.b), Var(Object.a)})})
