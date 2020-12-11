from bauhaus import Encoding, proposition, constraint
"""
Reference:
https://github.com/ContinuumIO/pycosat/blob/master/examples/sudoku.py

Cell Constraints
Each cell contains exactly one copy of any number
(At least one number and at most one number)

Region Constraints

Row Constraints
Each row contains every number exactly once (no duplicates)

Column Constraints
Each column contains every number exactly once (no duplicates)
"""

class Cell:
    pass

class Region:
    pass

class Row:
    pass

class Col:
    pass