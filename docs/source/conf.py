# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import sys
import os
sys.path.insert(0, os.path.abspath('../..'))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'BENT'
copyright = '2023, Pedro Ruas'
author = 'Pedro Ruas'
release = '0.1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

sphinxemoji_source = 'https://unpkg.com/twemoji@latest/dist/twemoji.min.js'
sphinxemoji_style = 'twemoji'

extensions = [
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc', 
    'sphinx.ext.coverage', 
    'sphinx.ext.napoleon',
    'myst_parser',
    'sphinxemoji.sphinxemoji',
    'sphinxcontrib.bibtex'
    #'sphinx.ext.autoapi'
    ]

bibtex_bibfiles = ['refs.bib']
bibtex_default_style = 'plain'
#extensions.append('autoapi.extension')

#autoapi_type = 'python'
#autoapi_dirs = ['source', 'src']

#autosummary_generate = True 

templates_path = ['_templates']
exclude_patterns = []

source_suffix = {
    '.rst': 'restructuredtext',
    '.txt': 'markdown',
    '.md': 'markdown',
}


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
