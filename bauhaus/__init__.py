"bauhaus is a library for building logical theories on the fly with Python."

from .core import Encoding, proposition, constraint, Or, And, print_theory

__all__ = [
    "Encoding",
    "proposition",
    "constraint",
    "Or",
    "And",
    "print_theory"
]

__version__ = "1.0.0dev"
