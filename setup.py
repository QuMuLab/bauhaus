import setuptools

with open("README.md") as f:
    long_description = f.read()

setuptools.setup(
    name="nnf",
    version='0.1.0',
    author="Karishma Daga, Christian Muise",
    author_email="karishma.daga@queensu.ca, christian.muise@queensu.ca",
    description="Build propositional theories for SAT solvers on the fly",
    url="https://github.com/QuMuLab/bauhaus",
    packages=setuptools.find_packages(where='bauhaus'),
    python_requires='>=3.4',
    install_requires=[
        'typing;python_version<"3.5"',
        'nnf;'
        'pysat;'
    ],
    license="MIT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
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
        "License :: OSI Approved :: ISC License (ISCL)",
    ],
    keywords="logic nnf sat constraints encodings",
    project_urls={
        'Source': "https://github.com/QuMuLab/bauhaus",
    },
    include_package_data=True,
    zip_safe=False,
)