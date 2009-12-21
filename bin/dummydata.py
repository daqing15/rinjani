#!/usr/bin/python -W ignore::DeprecationWarning

import sys
import os
DIR = os.path.abspath(os.path.dirname(__file__))
PARENT_DIR = os.path.dirname(DIR)
sys.path = [DIR, PARENT_DIR, os.path.join(PARENT_DIR, "lib")] + sys.path

from rinjani.indexing import index, generate_doc_content

generate_doc_content()
index.rebuild_index()