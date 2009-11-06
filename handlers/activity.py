import datetime

from main import BaseHandler, authenticated
from forms import activity_form, CONTENT_TAGS_COLLECTION
from models import Activity, EditDisallowedError
from web.utils import Storage
from utils.pagination import Pagination
from utils.utils import move_attachments, parse_attachments
import tornado.web
from utils.time import striso_to_date

PERMISSION_ERROR_MESSAGE = "You are not allowed to edit this activity"

class ListHandler(BaseHandler):
    def get(self):
        pagination = Pagination(self, Activity, {'status':u'published'}, 2)
        self.render('activities', pagination=pagination)

class ViewHandler(BaseHandler):
    def get(self, dt, slug):
        date = striso_to_date(dt)
        one_day = datetime.timedelta(days=1)
        activity = Activity.one({"slug": slug, "created_at": {'$gte': date, '$lte': date + one_day}})
        if not activity:
            raise tornado.web.HTTPError(404)
        Activity.collection.update({'slug': slug}, {'$inc': { 'view_count': 1}})
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
            activity = Activity()
        self.render("activity-edit", f=f, activity=activity, suggested_tags=CONTENT_TAGS_COLLECTION)
    
    @authenticated(['agent', 'sponsor'])
    def post(self):
        f = activity_form()
        data = self.get_arguments()
        is_edit = data.has_key('is_edit')
        
        try:
            attachments = self.get_argument('attachments', None)
            if attachments:
                data['attachments'] = parse_attachments(data['attachments'], is_edit)   
                
            if f.validates(Storage(data)):
                activity = Activity.one({'slug': data['slug']}) if is_edit else Activity()
                activity.save(data, user=self.get_current_user())
                
                if attachments and not is_edit:
                    activity['attachments'] = move_attachments(self.settings.upload_path, data['attachments'])
                    activity.update_html()
                    activity.save()
                    
                self.set_flash("Activity has been saved.")
                self.redirect(activity.get_url())
                return
            activity = Activity()
            raise Exception("Form still have errors.")
        except EditDisallowedError:
            self.set_flash(PERMISSION_ERROR_MESSAGE)
            self.redirect(activity.get_url())
        except Exception, e:
            if attachments:
                activity['attachments'] = data['attachments']
            f.note = f.note if f.note else e
            self.render("activity-edit", f=f, activity=activity, suggested_tags=CONTENT_TAGS_COLLECTION)
        

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