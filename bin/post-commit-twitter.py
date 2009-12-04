#!/usr/bin/python -u 

#
# Copyright 2009 rinjani team
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

""" 
Post commit hooks - Send commit message to twitter
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

