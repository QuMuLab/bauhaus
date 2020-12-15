
import io
from setuptools import setup
from setuptools import find_packages

VERSION = '1.0.0'

NAME = 'bauhaus'

DESCRIPTION = 'Build logical theories for SAT solvers on the fly'

DEPENDENCIES = [
    'nnf>=',
    'pysat>='
]

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

with io.open('LICENSE.txt', 'r', encoding='utf-8') as f:
    LICENSE = f.read()

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    classifiers=CLASSIFIERS,
    author='Karishma Daga',
    author_email="karishma.daga@queensu.ca",
    license=LICENSE,
    install_requires=DEPENDENCIES,
    packages=find_packages(exclude=['tests', 'tests.*']),
    keywords="logic nnf sat constraints encodings",
    project_urls={
        'Source': "https://github.com/QuMuLab/bauhaus",
    },
    include_package_data=True
)