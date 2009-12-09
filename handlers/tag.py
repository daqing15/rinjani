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
import urllib2
from main import BaseHandler, authenticated
import models
from models import User, Content, Vote, Tag, UserTag
from utils.pagination import Pagination
from settings import MY_FLAGS

class ListHandler(BaseHandler):
    def get(self, tab):
        tab = tab or 'content'
        doc = Tag if tab == 'content' else UserTag
        pagination = Pagination(self, doc, {}, sort_by='_id', sort=1)
        self.render('tags', tab=tab, pagination=pagination)

class ViewHandler(BaseHandler):
    def get(self, tab, tags):
        tab = tab or 'content'
        tags = urllib2.unquote(tags).split('+')
        doc = Content if tab == 'content' else User
        pagination = Pagination(self, doc, {'tags': {'$all':tags}}, 10)
        self.render('tag-view', tab=tab, tags=tags, pagination=pagination)
        
class FlagHandler(BaseHandler):
    @authenticated()
    def post(self):
        data = self.get_arguments()
        try:
            cls = getattr(models, self.get_argument('type'))
            flag = self.get_argument('flag')
            slug = self.get_argument('slug')
            cid = cls.one({'slug': slug})['_id']
            uid = self.current_user['_id']
            if int(flag) in [x for x,_y in MY_FLAGS]:
                has_vote = Vote.one({'uid': uid ,'cid': cid})
                if not has_vote:
                    cls.collection.update(
                        {'slug': slug}, {'$inc': { "votes." + flag: 1}}
                    )
                    vote = Vote()
                    vote['uid'],  vote['cid'], vote['vote'] = uid, cid, int(flag)
                    vote.save()
                    self.json_response("Your vote has been noted", "OK")
                raise Exception("Has vote")
            raise Exception("Invalid vote")
        except Exception, e:
            return self.json_response(e.__str__(), "ERROR", data)
        
        self.json_response(None, "OK", data)
        
        