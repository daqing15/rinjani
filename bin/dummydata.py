#!/usr/bin/python -W ignore::DeprecationWarning
from __future__ import print_function
import datetime
import time
import sys
import os
import shutil
import re
import random
from time import sleep

DIR = os.path.abspath(os.path.dirname(__file__))
PARENT_DIR = os.path.dirname(DIR)
INDEX_DIR = '/rinjani/opt/solr-svr/peduli/data/index'

sys.path = [DIR, PARENT_DIR, os.path.join(PARENT_DIR, "lib")] + sys.path

from markov import MarkovGenerator
import markdown2
import genericng

from pymongo.connection import Connection
from rinjani.string import slugify, truncate_words
from models import CONTENT_TYPE, Content, User, Article, Project
from settings import USERTYPE, CONTENT_TAGS, USER_TAGS
from rinjani.indexing import index


contents = []
titles = []
names = []
users = []

def choose_loc():
    # aceh (5.535072,95.29541), merauke (-8.512576,140.392456) 
    # square approx yg gak kena sing/mal, topleft: 1.090877,99.929809 
    loc = (random.randrange(-8,2) + random.random(), \
                random.randrange(96, 140) + random.random())
    return (unicode(loc[0]), unicode(loc[1]))

def generate_random_content():
    global contents
    global titles
    
    def random_content(): return ".\n\n".join([(mg.say().strip()) for _i in range(4)])
    
    start = time.time()
    print("Generating random content...", end="")
    sys.stdout.flush()
    
    mg = MarkovGenerator(2)
    txt = file('/rinjani/var/data/milton-paradise.txt').read()
    txt = re.sub('["*]*-', '', txt)
    mg.learn(txt)
    contents = [random_content() for _i in range(200)]
    titles = [re.sub(r'[^\w\s]+', '', truncate_words(mg.say().strip(), 10)) for _i in range(100)]
    
    print(" finished in %ds." % (time.time() - start))
    sys.stdout.flush()
    
def choose_tags(tsel=CONTENT_TAGS):
    tags = []
    tsel = tsel['mandatory']
    for i in range(random.randrange(1,5)):
        tags.append(tsel[random.randrange(0,len(tsel)-1)])
    return list(set(tags))
    
def create_new_content(idx):
    author = users[random.randrange(0,len(users)-1)]
    created_at = datetime.datetime.utcnow() - datetime.timedelta(hours=3*idx)
    type = CONTENT_TYPE.ARTICLE if author['type'] == 'public'\
        else random.choice([CONTENT_TYPE.ARTICLE, CONTENT_TYPE.PROJECT])
    
    loc = choose_loc() 
    doc = {
           'type': type,
            'title': unicode(titles[random.randrange(0,len(titles)-1)]),
            'content':  unicode(contents[random.randrange(0,len(contents)-1)]),
            'tags': choose_tags(),
            'created_at': created_at,
            'lat': loc[0],
            'lng': loc[1],
        }
    if doc['type'] == CONTENT_TYPE.ARTICLE:
        doc['excerpt'] = titles[random.randrange(0,len(titles)-1)]
        new_content = Article()
    else:
        new_content = Project()
        doc['need_donation'] = True
        doc['goal'] = unicode(titles[random.randrange(0,len(titles)-1)])
        
    if random.randrange(1,30) == 9:
        doc['featured'] = True
        print("X", end="")
    new_content.save(doc, author)

user_created_at = datetime.datetime.utcnow() - datetime.timedelta(days=100)

def create_new_user():
    loc = choose_loc()
    name =  genericng.generate(2)
    while name in names:
        name =  genericng.generate(2)
    doc = {
            'type': random.choice(USERTYPE)[0],
            'username': unicode(name),
            'password_hashed': unicode('a7257ef242a856304478236fe46fee00f23f8a25'),
            'fullname': unicode(name + ' ' + genericng.generate(1)),
            'about': unicode(titles[random.randrange(0,len(titles)-1)]),
            'profile_content':  unicode(contents[random.randrange(0,len(contents)-1)]),
            'tags': choose_tags(USER_TAGS),
            'lat': loc[0],
            'lng': loc[1],
            'created_at': user_created_at
           }        
    
    if random.randrange(1, 30) == 9:
        doc['featured'] = True
        print("X", end="")
    new_user = User()
    new_user.save(doc)
    users.append(new_user)
    
def generate_doc_content():
    generate_random_content()
    
    conn = Connection()
    conn.drop_database('peduli')
    
    print("Adding users.", sep="")
    for i in range(50): 
        create_new_user()
        print(".", end="")
    print(".\nAdding contents.", end="")
    for i in range(500): 
        create_new_content(i)
        print(".", end="")
        sys.stdout.flush()
    print(".")
        
if __name__ == '__main__':
    #generate_doc_content()
    #shutil.rmtree(INDEX_DIR, ignore_errors=True)
    index.rebuild_index()


