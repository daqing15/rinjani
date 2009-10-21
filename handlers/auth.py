import tornado.auth
import tornado.escape
import web.form
from forms import login_form
from .main import BaseHandler
from models import User
from web.utils import Storage
import logging

class LoginHandler(BaseHandler):
    def get(self):
        if self.get_current_user():
            self.set_flash("You're already logged in")
            self.redirect("/")
            return
        next = self.get_argument('next', '/dashboard')
        self.render("login", f=login_form, next=next)

    def post(self):
        from models import User
        
        username = self.get_argument('username', '')
        password = self.get_argument('password', '')
        f = login_form()
        user = User.one({'username': username, 'password': password})
        f.validators = [web.form.Validator("The username or password you entered is incorrect", lambda x: bool(user))]
        if f.validates(Storage(self.get_arguments())):
            self.set_cookie("t", user['type'])
            self.set_secure_cookie("username", username)
            self.set_secure_cookie("u", user['_id'])
            
            next = self.get_argument('next', '/dashboard')
            self.redirect(next)
        else:
            self.render("login", f=f)

class LogoutHandler(BaseHandler, tornado.auth.FacebookMixin):
    def get(self):
        loc = self.get_cookie('loc')
        self.clear_all_cookies()
        self.set_cookie('loc', loc)
        self.redirect(self.get_argument("next", "/"))

