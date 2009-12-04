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

from main import BaseHandler, authenticated
from forms import page_form
from web.utils import Storage
from models import Page, EditDisallowedError
from utils.utils import move_attachments, parse_attachments
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
                page.check_edit_permission(self.get_current_user())
                page.formify()
                f.fill(page)
            except EditDisallowedError:
                self.set_flash("You are not allowed to edit that page")
                self.redirect(page.get_url())
                return
            except:
                raise tornado.web.HTTPError(404)
        else:
            page = Page()
        
        self.render("page-edit", f=f, page=page)
    
    @authenticated(None, True)
    def post(self):
        f = page_form()
        data = self.get_arguments()
        is_edit = data.has_key('ori_slug')
        
        try:
            attachments = self.get_argument('attachments', None)
            if attachments:
                data['attachments'] = parse_attachments(data['attachments'], is_edit) 
                
            if f.validates(Storage(data)):
                page = Page.one({'slug': data['ori_slug']}) if is_edit else Page()
                page.save(data, user=self.current_user)
                
                if attachments and not is_edit:
                    page['attachments'] = move_attachments(self.settings.upload_path, data['attachments'])
                    page.update_html()
                    page.save()
                    
                self.set_flash(u"Page has been saved.")
                self.redirect(page.get_url())
                return
            page = Page()
            raise Exception("Invalid form data")
        except Exception, e:
            raise
            if attachments:
                page['attachments'] = data['attachments']
            f.note = f.note if f.note else e
            self.render("page-edit", f=f, page=page)
            
class RemoveHandler(BaseHandler):
    def post(self, slug):
        page = Page.one({"slug": slug})
        if not page:
            raise tornado.web.HTTPError(404)
        
        page.remove()
        self.set_flash("That page has been removed")
        self.redirect("/")                 