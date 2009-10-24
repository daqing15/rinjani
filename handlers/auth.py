import tornado.auth
import tornado.escape
import web.form
from forms import login_form
from .main import BaseHandler
from models import User
from web.utils import Storage
import logging
import hashlib

class LoginHandler(BaseHandler):
    def get(self):
        if self.get_current_user():
            self.set_flash("You're already logged in")
            self.redirect("/")
            return
        next = self.get_argument('next', '/dashboard')
        self.render("login", next=next)

class LoginFormHandler(BaseHandler):
    def get(self):
        if self.get_current_user():
            self.set_flash("You're already logged in")
            self.redirect("/")
            return
        next = self.get_argument('next', '/dashboard')
        self.render("login-form", f=login_form(), next=next)
        
    def post(self):
        username = self.get_argument('username', '')
        password_hashed = hashlib.sha1(self.get_argument('password', '')).hexdigest()
        f = login_form()
        user = User.one({'username': username, 'password_hashed': password_hashed})
        f.validators = [web.form.Validator("The username or password you entered is incorrect", lambda x: bool(user))]
        if f.validates(Storage(self.get_arguments())):
            self.set_secure_cookie("username", username)
            next = self.get_argument('next', '/dashboard')
            self.redirect(next)
        else:
            self.render("login-form", f=f)
                                   
class AuthMixin(object):
    def canonical(self, user):
        logging.error(user)
        
        uids = {'facebook': 'uid', 'google': 'email'}
        auth_provider = self.get_cookie("ap", None)
        user['auth_provider'] = auth_provider
        user['uid'] = str(user[uids[auth_provider]])      
        return user
    
    def _on_auth(self, user):
        user = self.canonical(user)
        if not user:
            raise tornado.web.HTTPError(500, "Authentication failed")
        
        peduli_user =  User.one({'uid': user['uid'], 'auth_provider': user['auth_provider']})
        if not peduli_user:
            self.set_secure_cookie("user", tornado.escape.json_encode(user))
            self.set_flash("You have been succefully authenticated. In order to be added as new member, you must complete form shown below.")
            self.redirect("/new-user")
            return
        self.set_secure_cookie("username", peduli_user['username'])
        self.redirect(self.get_argument("next", "/"))
        
class FacebookLoginHandler(BaseHandler, AuthMixin, tornado.auth.FacebookMixin):
    @tornado.web.asynchronous
    def get(self):
        if self.get_argument("session", None):
            self.get_authenticated_user(self.async_callback(self._on_auth))
            return
        self.set_cookie("ap", "facebook")
        self.authorize_redirect(['email', 'offline_access'])
    
class GoogleLoginHandler(BaseHandler, AuthMixin, tornado.auth.GoogleMixin):
    @tornado.web.asynchronous
    def get(self):
        if self.get_argument("openid.mode", None):
            self.get_authenticated_user(self.async_callback(self._on_auth))
            return
        self.set_cookie("ap", "google")
        self.authenticate_redirect()

class TwitterLoginHandler(BaseHandler, AuthMixin, tornado.auth.TwitterMixin):
    @tornado.web.asynchronous
    def get(self):
        if self.get_argument("oauth_token", None):
            self.get_authenticated_user(self.async_callback(self._on_auth))
            return
        self.set_cookie("ap", "twitter")
        self.authenticate_redirect()
            
class LogoutHandler(BaseHandler, tornado.auth.FacebookMixin):
    def get(self):
        loc = self.get_cookie('loc')
        self.clear_all_cookies()
        if loc:
            self.set_cookie('loc', loc)
        self.redirect(self.get_argument("next", "/"))

