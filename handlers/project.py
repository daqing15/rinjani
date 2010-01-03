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
from forms import project_form
from models import EditDisallowedError, Project
from rinjani.pagination import Pagination
from rinjani.utils import move_attachments, parse_attachments

class ListHandler(BaseHandler):
    def get(self, tab):
        spec = {'status':'published'}
        tab = tab or 'latest'
        if tab == 'featured':
            spec.update({'featured':True})
        
        if tab == 'popular':
            pagination = Pagination(self, Project, spec, sort_by='view_count')
        else:
            pagination = Pagination(self, Project, spec)
            
        self.render('projects', pagination=pagination, tab=tab)

class ViewHandler(BaseHandler):
    def get(self, slug):
        spec = {'status':'published', 'slug': slug}
        project = Project.one(spec)
        if not project:
            raise tornado.web.HTTPError(404)
        project.increment_view_count()
        self.render("project", project=project)

class EditHandler(BaseHandler):
    @authenticated(['agent', 'sponsor'])
    def get(self, slug=None):
        f = project_form()
        if slug:
            try:
                project = Project.one({'slug': slug})
                project.check_edit_permission(self.get_current_user())
                project.formify()
                f.fill(project)
            except EditDisallowedError:
                self.set_flash(self._("You are not allowed to edit this project."))
                self.redirect(project.get_url())
                return
            except:
                raise tornado.web.HTTPError(500)
        else:
            project = Project()
        self.render("project-edit", f=f, project=project, user=self.current_user)

    @authenticated(['agent', 'sponsor'])
    def post(self, slug=None):
        f = project_form()
        data = self.get_arguments()
        attachments = self.get_argument('attachments', None)
        is_edit = bool(slug)
        
        _ = self._
        
        try:
            if attachments:
                data['attachments'] = parse_attachments(data['attachments'], is_edit)
                
            project = Project.one({'slug': slug}) \
                    if is_edit else Project()
            
            if f.validates(tornado.web._O(data)):
                project.save(data, user=self.current_user)

                if attachments and not is_edit:
                    project['attachments'] = move_attachments(self.settings.upload_path, data['attachments'])
                    project.update_html()
                    project.save()

                self.set_flash(_("Project has been saved."))
                url =  project.get_url() if project.status == 'published' else '/dashboard'
                self.redirect(url)
                return
            raise Exception(_("Form still have errors. Please check for required fields."))
        except EditDisallowedError:
            self.set_flash(_("You are not allowed to edit the project."))
            self.redirect(project.get_url())
        except Exception, e:
            if attachments:
                project['attachments'] = data['attachments']
            f.note = f.note if f.note else e
            self.render("project-edit", f=f, project=project, user=self.current_user)


class RemoveHandler(BaseHandler):
    @authenticated(['agent', 'sponsor'])
    def post(self, slug):
        project = Project.one({'slug': slug})
        if not project:
            raise tornado.web.HTTPError(404)

        #project.delete()
        project.status = u'deleted'
        project.save()
        self.set_flash(self._("The project has been removed."))
        self.redirect("/projects")
