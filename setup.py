
import io
from setuptools import setup
from setuptools import find_packages

VERSION = '1.0.0dev'

NAME = 'bauhaus'

DESCRIPTION = 'Build logical theories for SAT solvers on the fly'

DEPENDENCIES = [
    'nnf>=0.1.0',
]

EXTRAS = {
    'pysat': ['python-sat>=0.1'],
}

CLASSIFIERS = [
    "Intended Audience :: Science/Research",
    "Topic :: Scientific/Engineering",
    "Topic :: Scientific/Engineering :: Mathematics",
    "Development Status :: 4 - Beta",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3 :: Only",
]

with io.open('LICENSE', 'r', encoding='utf-8') as f:
    LICENSE = f.read()

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    classifiers=CLASSIFIERS,
    author='Karishma Daga, Christian Muise',
    author_email='karishma.daga@queensu.ca, christian.muise@queensu.ca',
    license=LICENSE,
    python_requires='>=3.4',
    install_requires=DEPENDENCIES,
    extras_require=EXTRAS,
    packages=find_packages(exclude=['tests', 'tests.*']),
    keywords='logic nnf sat constraints encodings',
    include_package_data=True
)