from .main import BaseHandler, authenticated
from forms import activity_form, CONTENT_TAGS_COLLECTION
from models import Activity, EditDisallowedError
from web.utils import Storage
from utils.pagination import Pagination
import tornado.web
import logging

PERMISSION_ERROR_MESSAGE = "You are not allowed to edit this activity"

class ListHandler(BaseHandler):
    def get(self):
        pagination = Pagination(self, Activity, {'status':u'published'})
        self.render('activities', pagination=pagination)

class ViewHandler(BaseHandler):
    def get(self, slug):
        activity = Activity.one({"slug": slug})
        if not activity:
            raise tornado.web.HTTPError(404)
        self.render("activity", activity=activity)

class EditHandler(BaseHandler):
    @authenticated(['agent', 'sponsor'])
    def get(self, slug=None):
        f = activity_form()
        if slug:
            try:
                activity = Activity.one({"slug": slug})
                activity.check_edit_permission(self.get_current_user())
                f['need_donation'].checked = bool(activity['need_donation'])
                f['need_volunteer'].checked = bool(activity['need_volunteer'])
                f['enable_comment'].checked = bool(activity['enable_comment'])
                activity.formify()
                f.fill(activity)
            except EditDisallowedError:
                self.set_flash(PERMISSION_ERROR_MESSAGE)
                self.redirect(activity.get_url())
                return
            except:
                raise tornado.web.HTTPError(404)
        else:
            activity = None
        self.render("activity-edit", f=f, slug=slug, activity=activity, suggested_tags=CONTENT_TAGS_COLLECTION)
    
    @authenticated(['agent', 'sponsor'])
    def post(self):
        f = activity_form()
        data = self.get_arguments()
        logging.error(data)
        is_edit = data.has_key('is_edit')
        
        try:
            if f.validates(Storage(data)):
                activity = Activity.one({'slug': data['slug']}) if is_edit else Activity()
                activity.save(data, user=self.get_current_user())
                self.set_flash("Activity has been saved.")
                self.redirect(activity.get_url())
                return
            raise Exception("Form still have errors. Please correct them before saving.")
        except EditDisallowedError:
            self.set_flash(PERMISSION_ERROR_MESSAGE)
            self.redirect(activity.get_url())
        except Exception, e:
            logging.error(e)
            f.note = f.note if f.note else e
            slug = None if not is_edit else data.get('slug', None)
            self.render("activity-edit", f=f, slug=slug)
        

class RemoveHandler(BaseHandler):
    def post(self, slug):
        activity = Activity.one({"slug": slug})
        if not activity:
            raise tornado.web.HTTPError(404)
        
        #activity.delete()
        activity.status = u'deleted'
        activity.save()
        self.set_flash("That activity has been removed")
        self.redirect("/activities")        