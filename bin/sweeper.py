#!/usr/bin/python -W ignore::DeprecationWarning

import os
import sys
import subprocess
import time, sched
import logging

DIR = os.path.abspath(os.path.dirname(__file__))
PARENT_DIR = os.path.dirname(DIR)
sys.path = [DIR, PARENT_DIR, PARENT_DIR + '/lib'] + sys.path

from models import Cache
MONGO = '/opt/devel/mongodb/bin/mongo'
DB = 'peduli'

scheduler = sched.scheduler(time.time, time.sleep)

def new_timed_call(period, callback, *args, **kw):
    def reload():
        callback(*args, **kw)
        scheduler.enter(period, 0, reload, ())
    scheduler.enter(period, 0, reload, ())

def remove_old_caches(*args, **kw):
    logging.warn("[%s] Removing expired caches..." % time.ctime(time.time()))
    Cache.collection.remove({'expire':{'$lt':time.time()}})
    
def update_tags(*args, **kw):
    logging.warn("[%s] Updating tag count..." % time.ctime(time.time()))
    subprocess.Popen("%s %s %s/tag-count.js" % (MONGO, DB, DIR), shell=True, 
                     stdout=subprocess.PIPE).communicate()[0]
    subprocess.Popen("%s %s %s/tag-combination-count.js" % (MONGO, DB, DIR), shell=True, 
                     stdout=subprocess.PIPE).communicate()[0]

def main():
    new_timed_call(120, remove_old_caches)
    new_timed_call(60, update_tags)        
    scheduler.run()
    
if __name__ == '__main__':
    main()
