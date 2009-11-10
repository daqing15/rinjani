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
from models import Article
from utils.pagination import Pagination
import tornado.web

class ListHandler(BaseHandler):
    def get(self):
        pagination = Pagination(self, Article, {})
        self.render('tags', pagination=pagination)

class Handler(BaseHandler):
    def get(self):
        self.render('report')
        
    def post(self):
        return "X"
