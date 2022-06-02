# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list of options see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
sys.path.insert(0, os.path.abspath('..'))


# -- Project information -----------------------------------------------------

# The following are set from setup.py when building using the distutils
# custom command 'build_sphinx'
#
#project = 'Rubrik Polaris SDK for Python'
#release = '2021.01.08'
#author = 'Rubrik Inc'
#copyright = '{}, {}'.format(datetime.datetime.now().year, author)


# -- General configuration ---------------------------------------------------

master_doc = 'index'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.coverage',
    'sphinx.ext.napoleon',
    'myst_parser',
    'sphinx_copybutton',
    'sphinx_autopackagesummary'
]

autosummary_generate = True

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


source_suffix = ['.rst', '.md']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = 'furo'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']


html_favicon = '_static/rubrik.ico'
html_logo = '_static/rubrik.png'
html_style = 'rubrik.css'

html_theme_options = {
    'navigation_with_keys': True,
    #'announcement': '<em>This is a BETA version!</em>'
}
