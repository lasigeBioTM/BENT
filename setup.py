#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name="bent",
    version="0.0.32",
    description = "BENT: Biomedical Entity Annotator",
    long_description=open("README.rst").read(),
    author = "Pedro Ruas",
    author_email = "pedrosimruas@gmail.com",
    packages = find_packages(),
    python_requires=">=3.7, <=3.10.13",
    license = open("LICENSE.txt").read(),
    url="https://github.com/lasigeBioTM/bent",
    keywords=["text mining", "natural language processing", "entity extraction",
        "named entity recognition", "named entity linking", "normalization", 
        "disambiguation", "NER", "NEL", "information extraction"],
   
    install_requires=open("bent/requirements.txt").readlines(),
    
    include_package_data=True,

    entry_points={
        "console_scripts": [
            "bent_setup = bent.setup_package_wrapper:main",
        ] },
   
    classifiers = [
        # How mature is this project? 
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 3 - Alpha",

        # Indicate who your project is intended for
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Information Technology",
        
        # Topics
        "Topic :: Software Development :: Build Tools",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",

        
        # Specify the Python versions you support here.
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python",

        "Programming Language :: Unix Shell",
        "Programming Language :: Java",

        # OS
        "Operating System :: POSIX :: Linux",

        "License :: OSI Approved :: Apache Software License"
        ]
    )
