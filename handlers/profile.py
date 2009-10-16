from web.utils import Storage
import web.form
from .main import BaseHandler, authenticated
from models import User
from utils.pagination import Pagination
from forms import profile_public_form, profile_form, register_form

class ViewHandler(BaseHandler):
    def get(self, username):
        user = User.one({'username': username})
        
        if user == self.get_current_user():
            self.redirect("/dashboard")
             
        if user:
            self.render(user['type'] + "/profile", user=user)
        else:
            raise self.render('404', message="User with name %s does not exists" % username)

class RegisterHandler(BaseHandler):
    def get(self):
        f = register_form()
        self.render("register", f=f)

    def post(self):
        f = register_form()
        data = self.get_arguments()
        
        if data.has_key('username'):
            user = User.one({'username': data['username']})
            print "user already exists? %s" % data['username']
            f.validators.append(web.form.Validator("The username you wanted is already taken", 
                                lambda x: not bool(user)) )
        
        if f.validates(Storage(data)):
            new_user = User()
            try:
                new_user.populate(data)
                new_user['is_admin'] = False
                new_user.validate()
                new_user.save()
                self.set_flash("You have been successfully registered. You can log in now.")
                self.redirect(self.get_login_url())
                return
            except:
                raise
        self.render("register", f=f)


class EditHandler(BaseHandler):
    @authenticated()
    def get(self):
        user_type = self.get_user_type()
        if user_type == 'public':
            f = profile_public_form()
        else:
            f = profile_form()
        self.render(user_type + "/profile-edit", f=f)
    
    @authenticated()
    def post(self):
        self.set_flash("Profile saved")
        self.redirect("/dashboard")
        
class Dashboard(BaseHandler):
    @authenticated()
    def get(self):
        self.render(self.get_user_type() + "/dashboard")

class UserListHandler(BaseHandler):
    def get(self):
        pagination = Pagination(self, User, {}, 1)
        self.render('users', pagination=pagination)

class CommentsHandler(BaseHandler):
    @authenticated()
    def get(self):
        pagination = Pagination(self, User, {}, 1)
        self.render('public/comments', pagination=pagination)
    
    @authenticated()
    def post(self):
        pagination = Pagination(self, User, {}, 1)
        self.render('public/comments', pagination=pagination)
        


        