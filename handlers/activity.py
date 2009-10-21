from .main import BaseHandler, authenticated
from forms import activity_form, InvalidFormDataError
from models import Activity, User, EditDisallowedError
from web.utils import Storage
from utils.pagination import Pagination
import markdown2

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
            f.fill(activity)
        self.render("activity-edit", f=f, slug=slug)
    
    @authenticated(['agent', 'sponsor'])
    def post(self):
        f = activity_form()
        data = self.get_arguments()
        is_edit = data.has_key('is_edit')
        
        try:
            if f.validates(Storage(data)):
                if is_edit:
                    activity = Activity.one({'slug': data['slug']})
                    activity.check_edit_permission(self.get_current_user())
                    #SchemaTypeError: author must be an instance of User not SON
                    activity['author'] = User.one({'username':activity['author']['username']})
                else:
                    activity = Activity()
                    activity['author'] = self.get_current_user()
                    activity.fill_slug_field(data['title'])
                    
                activity.populate(data)
                tags = data.get('tags')
                if tags:
                    tags = [tag.strip() for tag in tags.split(',')]
                    activity['tags'] = tags
                activity.validate()
                activity['content_html'] = markdown2.markdown(data['content'])
                activity.save()
                self.set_flash("Activity has been saved.")
                self.redirect("/activity/" + str(activity['slug']))
                return
            raise Exception("Invalid form data")
        except EditDisallowedError:
            self.set_flash(PERMISSION_ERROR_MESSAGE)
            self.redirect(activity.get_url())
        except Exception, e:
            if is_edit:
                self.render("activity-edit", f=f, slug=data['slug'])
            else:
                self.render("activity-edit", f=f, slug=None)
        
        