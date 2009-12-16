#!/usr/bin/python -W ignore::DeprecationWarning

import sys
import os
import time
DIR = os.path.abspath(os.path.dirname(__file__))
PARENT_DIR = os.path.dirname(DIR)
LIB_DIR = os.path.join(PARENT_DIR, "lib")
sys.path = [DIR, PARENT_DIR, LIB_DIR, '/usr/lib/python2.6',
            '/usr/lib/python2.6/dist-packages',
            '/usr/lib/python2.6/lib-dynload',] # + sys.path

from utils.index import Index, SCHEMA
from whoosh.qparser import QueryParser

def find(q):
    ix = Index()
    parser = QueryParser("content", schema=SCHEMA)
    print parser.parse(unicode(q))
    results = ix.find(q)
    if len(results):
        print "Found in %d documents" % len(results)
    else:
        print "Not found"

if __name__ == '__main__':
    if len(sys.argv) > 1:
        find(sys.argv[1])
    else:
        print "Usage: %s query" % sys.argv[0]
