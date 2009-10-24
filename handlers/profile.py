from web.utils import Storage
import web.form
from .main import BaseHandler, authenticated
from models import User
from utils.pagination import Pagination
from forms import profile_public_form, profile_form, register_form, new_user_form
import tornado.web
from tornado.escape import json_decode
import logging
import hashlib

class ViewHandler(BaseHandler):
    def get(self, username):
        user = User.one({'username': username})
        if user == self.current_user:
            self.redirect("/dashboard")
        if not user:
            raise tornado.web.HTTPError(404)
        self.render(user['type'] + "/profile", user=user)

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
                new_user['password_hashed'] = unicode(hashlib.sha1(data['password']).hexdigest())
                new_user['auth_provider'] = u'form'
                new_user.validate()
                new_user.save()
                self.set_flash("You have been successfully registered. You can log in now.")
                self.redirect("/login-form")
                return
            except:
                raise
            
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
            
            if data['auth_provider'] == 'facebook':
                from utils import fillin_fb_data
                fillin_fb_data(
                        self.settings['facebook_api_key'], 
                        self.settings['facebook_secret'],
                        ['pic_square', 'pic_smal', 'sex', 'website', 'birthday_date', 
                         'timezone', 'interests'],
                        data
                        )
                
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
            f = profile_form()
        else:
            f = profile_form()
        f.fill(self.current_user)
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
        