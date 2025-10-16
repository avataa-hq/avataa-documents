# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------
import os
import sys

sys.path.insert(0, os.path.abspath("../../app"))


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Documents"
copyright = "2023, Temur Tozhieff"
author = "Temur Tozhieff"
release = "0.9"


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx.ext.autodoc", "sphinxcontrib.autodoc_pydantic"]

templates_path = ["_templates"]
exclude_patterns = []


# -- Autopidantic ------------------------------------------------------------
# https://autodoc-pydantic.readthedocs.io/
autodoc_pydantic_model_show_json = True
autodoc_pydantic_settings_show_json = True


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "alabaster"
html_static_path = ["_static"]
