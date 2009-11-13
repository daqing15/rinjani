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
import markdown2
from utils.string import sanitize

class HomeHandler(BaseHandler):
    def get(self):
        was_here = self.get_cookie('was_here', False)
        if not was_here:
            self.set_cookie('was_here', '1')
        articles = Article.all({'slug': 'article-pertama'}) 
        self.render("home", articles=articles, was_here=was_here)

class MarkdownPreviewHandler(BaseHandler):
    def post(self):
        data = self.get_argument('data', None)
        if data:
            self.finish(sanitize(markdown2.markdown(data)))
