"""
Show that it is impossible to put n+1 pidgeons
into n holes, if each pidgeon were to go into a
distinct hole.

Constraint 1: Every pidgeon must be in at least one hole
Constraint 2: At most one pidgeon can be in a hole
"""

class Pidgeon:

    def __init__(self, name):
        self.name = name

class Hole:

    def __init__(self, hole):
        self.hole = hole
