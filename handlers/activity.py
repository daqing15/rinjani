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
from forms import activity_form
from models import CONTENT_TYPE, Activity, EditDisallowedError
from rinjani.pagination import Pagination
from rinjani.utils import move_attachments, parse_attachments

class ListHandler(BaseHandler):
    def get(self, tab):
        spec = {'type': CONTENT_TYPE.ACTIVITY, 'status':'published'}
        tab = tab or 'latest'
        if tab == 'featured':
            spec.update({'featured':True})
        
        if tab == 'popular':
            pagination = Pagination(self, Activity, spec, sort_by='view_count')
        else:
            pagination = Pagination(self, Activity, spec)
            
        self.render('activities', pagination=pagination, tab=tab)

class ViewHandler(BaseHandler):
    def get(self, slug):
        spec = {'type': CONTENT_TYPE.ACTIVITY, 'status':'published', 'slug': slug}
        activity = Activity.one(spec)
        if not activity:
            raise tornado.web.HTTPError(404)
        Activity.collection.update({'slug': slug}, {'$inc': { 'view_count': 1}})
        self.render("activity", activity=activity)

class EditHandler(BaseHandler):
    @authenticated(['agent', 'sponsor'], False, True)
    def get(self, slug=None):
        f = activity_form()
        if slug:
            try:
                activity = Activity.one({'type': CONTENT_TYPE.ACTIVITY, 'slug': slug})
                activity.check_edit_permission(self.get_current_user())
                activity.formify()
                f.fill(activity)
            except EditDisallowedError:
                self.set_flash(self.__("You are not allowed to edit this activity."))
                self.redirect(activity.get_url())
                return
            except:
                raise tornado.web.HTTPError(404)
        else:
            activity = Activity()
        self.render("activity-edit", f=f, activity=activity, user=self.current_user)

    @authenticated(['agent', 'sponsor'], False, True)
    def post(self):
        f = activity_form()
        data = self.get_arguments()
        is_edit = data.has_key('is_edit')
        
        _ = self._
        
        try:
            attachments = self.get_argument('attachments', None)
            if attachments:
                data['attachments'] = parse_attachments(data['attachments'], is_edit)

            if f.validates(tornado.web._O(data)):
                spec = {'type': CONTENT_TYPE.ACTIVITY, 'slug': data['slug']}
                activity = Activity.one(spec) if is_edit else Activity()
                activity.save(data, user=self.get_current_user())

                if attachments and not is_edit:
                    activity['attachments'] = move_attachments(self.settings.upload_path, data['attachments'])
                    activity.update_html()
                    activity.save()

                self.set_flash(_("Activity has been saved."))
                url =  activity.get_url() if activity.status == 'published' else '/dashboard'
                self.redirect(url)
                return
            activity = Activity()
            raise Exception(_("Form still have errors. Please check for required fields."))
        except EditDisallowedError:
            self.set_flash(_("You are not allowed to edit this activity."))
            self.redirect(activity.get_url())
        except Exception, e:
            if attachments:
                activity['attachments'] = data['attachments']
            f.note = f.note if f.note else e
            self.render("activity-edit", f=f, activity=activity, user=self.current_user)


class RemoveHandler(BaseHandler):
    def post(self, slug):
        activity = Activity.one({'type': 'Activity', 'slug': slug})
        if not activity:
            raise tornado.web.HTTPError(404)

        #activity.delete()
        activity.status = u'deleted'
        activity.save()
        self.set_flash(self._("That activity has been removed."))
        self.redirect("/activities")
