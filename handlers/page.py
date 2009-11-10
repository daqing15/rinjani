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
from models import Page, User
import tornado.web

class ViewHandler(BaseHandler):
    def get(self, slug):
        page = Page.one({'slug': slug})
        if not page:
            raise tornado.web.HTTPError(404)
        self.render("page", page=page)
        
class EditHandler(BaseHandler):
    @authenticated(None, True)
    def get(self, slug=None):
        f = page_form()
        if slug:
            try:
                page = Page.one({'slug': slug})
            except:
                raise tornado.web.HTTPError(404)
            f.fill(page)
        self.render("page-edit", f=f, slug=slug)
    
    @authenticated(None, True)
    def post(self):
        f = page_form()
        data = self.get_arguments()
        is_edit = data.has_key('ori_slug')
        
        try:
            if f.validates(Storage(data)):
                if is_edit:
                    page = Page.one({'slug': data['ori_slug']})
                    page['author'] = User.one({'username':page['author']['username']})
                else:
                    page = Page()
                    page['author'] = self.get_current_user()
                    
                page.populate(data)
                page.validate()
                import markdown2
                page['content_html'] = markdown2.markdown(data['content'])
                page.save()
                self.set_flash(u"Page has been saved.")
                self.redirect(page.get_url())
                return
            raise Exception("Invalid form data")
        except Exception, e:
            slug = article['ori_slug'] if is_edit else None
            self.render("page-edit", f=f, slug=slug)