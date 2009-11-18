#!/usr/bin/python -u 

"""
update Twitter with git commits
"""

import git
import twitter
import sys
sys.path.insert(0,'..')

from settings import BASE_PATH, TWITTER_USER, TWITTER_PASSWORD

api = twitter.Api(username=TWITTER_USER, password=TWITTER_PASSWORD)
repo = git.Repo(BASE_PATH)

head = [head for head in repo.heads if head.name == repo.active_branch][0]
lc = head.commit
stats = lc.stats.total

post = """ %s -- %d lines (+%d/-%d) in %d file(s)""" % (
                lc.summary, 
                stats['lines'], 
                stats['insertions'], 
                stats['deletions'],
                stats['files']
        )

api.PostUpdate(post)

