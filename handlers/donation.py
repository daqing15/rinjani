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

from .main import BaseHandler, authenticated
from forms import page_form, InvalidFormDataError
from web.utils import Storage
from models import Donation, User, Activity
import tornado.web

class ListHandler(BaseHandler):
    @authenticated()
    def get(self, slug=None):
        user_type = self.get_current_user()['type']
        
        donations = [{}, {}]
        if not donations:
            raise tornado.web.HTTPError(404)
        self.render(user_type + "/donations", donations=donations)

class ConfirmHandler(BaseHandler):
    def get(self, slug):
        #activity = Activity.one({'slug': slug}, {'title':1, 'author':1})
        donation = {'aaa': 1}
        if not donation:
            raise tornado.web.HTTPError(404)
        
        self.render("donation-confirm", donation=donation)
            