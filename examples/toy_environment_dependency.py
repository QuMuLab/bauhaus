"""
Inspired by conda, which uses SAT solvers for managing
package dependencies.

Article: 
https://www.anaconda.com/blog/understanding-and-improving-condas-performance

Github:
https://github.com/conda/conda/blob/4.6.7/conda/resolve.py#L798

"""
from bauhaus import Encoding, proposition, constraint

class ToyPackage(object):
    
    def __init__(self, name: str,
                 version: str,
                 dependencies: list):
        self.name = name
        self.version = version
        self.dependencies = dependencies
    
