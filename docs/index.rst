Welcome to bauhaus!
===================

``bauhaus`` is a library for building logical theories on the fly with Python.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   getting_started
   bauhaus
   architecture


Features
--------
- Create propositional variables from Python classes
- Build naive SAT encoding constraints from propositional variables
   - At most one
   - At least one
   - Exactly one
   - At most K
   - Implies all
   - None of
- Compile constraints into a theory in conjunctive or negation normal form
- With ``python-nnf``, submit a theory to a SAT solver
- Theory introspection

Installation
------------

Install ``bauhaus`` by running::

   pip install bauhaus


Usage
-----
:doc:`getting_started` is the place to go to hit the ground running on using bauhaus.

The :doc:`bauhaus` documentation provides documentation for the library.

Contribute
----------
Head over to our `Code of Conduct <https://github.com/QuMuLab/bauhaus/blob/master/CODE_OF_CONDUCT.md>`_ and get a feel for the
library by reading our :doc:`architecture` and :doc:`bauhaus`.

- Issue Tracker: https://github.com/QuMuLab/bauhaus/issues
- Source Code: https://github.com/QuMuLab/bauhaus
- Join us! http://mulab.ai/

Support
-------
If you are having issues, please let us know.
Reach out to us at karishma.daga@queensu.ca or by creating a GitHub issue.

License
-------
The project is licensed under the MIT license for the Queen's Mu Lab.
