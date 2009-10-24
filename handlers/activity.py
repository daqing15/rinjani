from .main import BaseHandler, authenticated
from forms import activity_form, InvalidFormDataError
from models import Activity, User, EditDisallowedError
from web.utils import Storage
from utils.pagination import Pagination
import markdown2
import tornado.web
import logging

PERMISSION_ERROR_MESSAGE = "You are not allowed to edit this activity"

class ListHandler(BaseHandler):
    def get(self):
        pagination = Pagination(self, Activity, {})
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
            except EditDisallowedError:
                self.set_flash(PERMISSION_ERROR_MESSAGE)
                self.redirect(activity.get_url())
                return
            except:
                raise tornado.web.HTTPError(404)
            if isinstance(activity['tags'], list):
                activity['tags'] = ', '.join(activity['tags'])
            f.validates(Storage(activity))
            # aneh
            f['need_donation'].checked = bool(activity['need_donation'])
            f['need_volunteer'].checked = bool(activity['need_volunteer'])
            f['enable_comment'].checked = bool(activity['enable_comment'])
        self.render("activity-edit", f=f, slug=slug)
    
    @authenticated(['agent', 'sponsor'])
    def post(self):
        f = activity_form()
        data = self.get_arguments()
        is_edit = data.has_key('is_edit')
        
        try:
            if f.validates(Storage(data)):
                activity = Activity.one({'slug': data['slug']}) if is_edit else Activity() 
                activity.save(data, user=self.current_user)
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
        
        