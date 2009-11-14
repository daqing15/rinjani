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

from main import BaseHandler
from models import Tag, ContentTag, Article, Activity
from utils.pagination import Pagination
from itertools import islice

class ListHandler(BaseHandler):
    def get(self):
        tab = self.get_argument("tab", "content")
        pagination = Pagination(self, Tag, {})
        self.render('tags', pagination=pagination, tab=tab, islice=islice)

class ViewHandler(BaseHandler):
    def get(self, tag):
        pagination = Pagination(self, ContentTag({'tags': tag}, [Article, Activity]), {})
        self.render('articles', pagination=pagination)
