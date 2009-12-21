#!/usr/bin/python -W ignore::DeprecationWarning

import os
import sys
import subprocess
import time, sched
import logging
from utils.json import JSONEncoder

DIR = os.path.abspath(os.path.dirname(__file__))
PARENT_DIR = os.path.dirname(DIR)
sys.path = [DIR, PARENT_DIR, PARENT_DIR + '/lib'] + sys.path

from models import Cache, Queue
from settings import DB as DBSETTING
from utils.indexing import SolrIndex

MONGO = '/opt/devel/mongodb/bin/mongo'

scheduler = sched.scheduler(time.time, time.sleep)
db_host, db_port, DB = DBSETTING
logging.getLogger().setLevel("DEBUG")

def new_timed_call(period, callback, *args, **kwargs):
    def reload():
        callback(*args, **kwargs)
        scheduler.enter(period, 0, reload, ())
    scheduler.enter(period, 0, reload, ())

def remove_old_caches(*args, **kwargs):
    print("[%s] Removing expired caches in mongo..." % time.ctime(time.time()))
    Cache.collection.remove({'expire':{'$lt':time.time()}})
    
def update_tags(*args, **kwargs):
    print("[%s] Updating tag count..." % time.ctime(time.time()))
    subprocess.Popen("%s %s %s/tag-count.js" % (MONGO, DB, DIR), shell=True, 
                     stdout=subprocess.PIPE).communicate()[0]
    subprocess.Popen("%s %s %s/tag-combination-count.js" % (MONGO, DB, DIR), shell=True, 
                     stdout=subprocess.PIPE).communicate()[0]

def indexer():
    index = SolrIndex()
    print("\nChecking queue for docs to be indexed..."),
    doc = Queue.one({'_id': 'indexing'})
    if doc and doc['payload'][-1:]:
        Queue.collection.update({'_id': 'indexing'}, {'$pop':{'payload': 1}})
        payload = doc['payload'][-1:]
        index.add(payload)
        print(" added!")
    
    print("\nChecking queue for docs to be removed from idx..."),
    doc = Queue.one({'_id': 'indexremoval'})
    if doc and doc['payload']:
        Queue.collection.update({'_id': 'indexremoval'}, {'$pop':{'payload': 1}})
        payload = doc['payload'].pop()
        index.delete(payload)
        print(" removed!")
    
def main():
    new_timed_call(2, indexer)
    #new_timed_call(60, update_tags)   
    #new_timed_call(120, remove_old_caches)
    scheduler.run()
    
if __name__ == '__main__':
    main()
