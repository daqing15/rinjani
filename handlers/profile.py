from web.utils import Storage
import web.form
from .main import BaseHandler, authenticated
from models import User
from utils.pagination import Pagination
from forms import profile_public_form, profile_form, register_form, new_user_form
import tornado.web
from tornado.escape import json_decode
import logging

class ViewHandler(BaseHandler):
    def get(self, username):
        user = User.one({'username': username})
        if user == self.get_current_user():
            self.redirect("/dashboard")
        if user:
            self.render(user['type'] + "/profile", user=user)
        else:
            raise tornado.web.HTTPError(404)

class NewUserHandler(BaseHandler):
    def get(self):
        f = new_user_form()
        self.render("new-user", f=f)
    
    def post(self):
        f = new_user_form()
        data = self.get_arguments()
        
        if data.has_key('username'):
            user = User.one({'username': data['username']})
            f.validators.append(web.form.Validator("The username you wanted is already taken", 
                                lambda x: not bool(user)) )
            
        if f.validates(Storage(data)):
            data.update(json_decode(self.get_secure_cookie("user")))
            user = User()
            user.populate(data)
            logging.info("\n=============\nNEW USER via %s: %s %s============\n" \
                             % (user['auth_provider'], user['first_name'], user['last_name']))
            user.save()
            self.set_secure_cookie("username", user['username'])
            self.clear_cookie("user")
            self.clear_cookie("ap")
            self.redirect("/")
            return
        
        self.render("new-user", f=f)
            

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
        user = self.get_current_user()
        pagination = Pagination(self, User, {}, 1)
        self.render(user['type'] + '/comments', pagination=pagination)
    
    @authenticated()
    def post(self):
        pass
        
class ProfileCommentsHandler(BaseHandler):
    def get(self, username):
        user = User.one({'username': username})
        if not user:
            raise tornado.web.HTTPError(404)
        pagination = Pagination(self, User, {}, 1)
        self.render('public/profile-comments', pagination=pagination, user=user)
    
    @authenticated()
    def post(self):
        pass
        