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

import tornado.web

from main import BaseHandler, authenticated
from models import Donation, User, Project, CONTENT_TYPE

class ListHandler(BaseHandler):
    @authenticated()
    def get(self, username):
        user = User.one({'username': username})
        if user != self.current_user:
            self.set_flash(self._("You are not allowed to view that page"))
            self.redirect("/")
            return
        donations = [{}, {}]
        if not donations:
            raise tornado.web.HTTPError(404)
        self.render("profile/donations", user=user, donations=donations)

class ConfirmHandler(BaseHandler):
    def get(self, slug):
        project = Project.one({'slug': slug}, ['title','author'])
        donation = {'aaa': 1}
        if not donation:
            raise tornado.web.HTTPError(404)
        
        self.render("donation-confirm", donation=donation, project=project)
            