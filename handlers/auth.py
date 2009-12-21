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
import hashlib
import tornado.auth
import tornado.escape
import web.form
from recaptcha import captcha

from forms import login_form, new_user_form, register_form, InvalidFormDataError
from main import BaseHandler
from models import User
from web.utils import Storage

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
        f.add_notnull_validator(user, "The username or password you entered is incorrect")

        next = self.get_argument('next', '/dashboard')
        if f.validates(Storage(self.get_arguments())):
            if user.status != 'active':
                self.set_flash(self._("Your login has been disabled/deleted. Please contact admin."))
                self.redirect("/")
                return
            
            expire = 14 if self.get_argument('rememberme',None) else None
            self.set_secure_cookie("username", username, expire)
                
            from datetime import datetime
            user.last_login = datetime.now()
            user.save()
            self.redirect(next)
        else:
            self.render("login-form", f=f, next=next)

class LogoutHandler(BaseHandler, tornado.auth.FacebookMixin):
    def get(self):
        loc = self.get_cookie('loc')
        self.clear_all_cookies()
        if loc:
            self.set_cookie('loc', loc)
        self.set_flash(self._("You have been logged out."))
        self.redirect("/")

class RegisterHandler(BaseHandler):
    def get(self):
        f = register_form()
        captcha_html = captcha.displayhtml(self.settings.CAPTCHA_PUBLIC_KEY, True)
        self.render("register", f=f, captcha_html=captcha_html, captcha_error='')

    def post(self):
        f = register_form()
        captcha_html = captcha.displayhtml(self.settings.CAPTCHA_PUBLIC_KEY, True)
        captcha_error = ''
        data = self.get_arguments()
        _ = self._
        if False and data.has_key('username'):
            existing_user = User.one({'username': data['username']})
            f.add_notnull_validator(not existing_user, "The username you wanted is already taken.")

        try:
            if f.validates(Storage(data)):
                
                captcha_resp = captcha.submit(
                                    self.get_argument('recaptcha_challenge_field'),
                                    self.get_argument('recaptcha_response_field'),
                                    self.settings.CAPTCHA_PRIVATE_KEY,
                                    self.request.remote_ip
                                )
                if captcha_resp.is_valid:
                    new_user = User()
                    data['is_admin'] = False
                    data['password_hashed'] = unicode(hashlib.sha1(data['password']).hexdigest(), 'utf-8')
                    data['auth_provider'] = u'form'
                    new_user.save(data)
                    self.set_flash(_("You have been successfully registered. "))
                    self.redirect("/")
                    return
                captcha_error = captcha_resp.error_code
                raise Exception("Invalid captcha code") 
            raise InvalidFormDataError(_("Form still have errors."))
        except Exception, e:
            f.note = f.note if f.note else e
            self.render("register", f=f, captcha_html=captcha_html, captcha_error=captcha_error)


class NewUserHandler(BaseHandler):
    def get(self):
        if not self.get_secure_cookie("user"):
            raise tornado.web.HTTPError(403, self._("Authentication cookie does not exists. Please enable Cookie in your browser."))
        self.render("new-user", f=new_user_form())

    def post(self):
        f = new_user_form()
        user_cookie = self.get_secure_cookie("user")
        
        _ = self._

        if not user_cookie:
            raise tornado.web.HTTPError(403, "Authentication cookie does not exists. Please enable Cookie in your browser.")

        data = self.get_arguments()
        user = tornado.escape.json_decode(user_cookie)
        if data.has_key('username'):
            new_user = User.one({'username': data['username']})
            f.validators.append(web.form.Validator("The username you wanted is already taken",
                                lambda x: not bool(new_user)) )
        try:
            if f.validates(Storage(data)):
                user.update(data)
                self.log("\n=====\nNEW USER via %s: %s======\n" \
                                 % (user['auth_provider'], user['uid']))

                new_user = User()
                new_user.save(user)

                self.set_secure_cookie("username", user['username'])
                self.clear_cookie("user")
                self.clear_cookie("ap")
                self.set_flash(_("Thank your for joining with us. You are logged in now."))
                self.redirect("/")
                return
            raise InvalidFormDataError(_("Form still have errors."))
        except Exception, e:
            f.note = f.note if f.note else e
            self.render("new-user", f=f)

class AuthMixin(object):
    def _on_auth(self, user):
        peduli_user =  User.one({'uid': user['uid'], 'auth_provider': user['auth_provider']})
        if not peduli_user:
            """ New user """
            self.set_secure_cookie("user", tornado.escape.json_encode(user))
            self.set_flash(self._("You have been succefully authenticated. In order to be member, you need complete form shown below."))
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
        self.authorize_redirect(['email', 'offline_access'])

    def get_authenticated_user(self, callback):
        self.require_setting("facebook_api_key", "Facebook Connect")
        session = tornado.escape.json_decode(self.get_argument("session"))
        self.facebook_request(
            method="facebook.users.getInfo",
            callback=self.async_callback(
                self._on_get_user_info, callback, session),
            session_key=session["session_key"],
            uids=session["uid"],
            fields="uid,name,locale,pic_square," \
                   "profile_url,username,website,proxied_email,birthday_date,timezone")

    def _on_get_user_info(self, callback, session, users):
        if not users:
            raise tornado.web.HTTPError(500, "Authentication failed")

        if users is None:
            callback(None)
            return

        self.log(users)
        callback({
            "auth_provider": "facebook",
            "fullname": users[0]["name"],
            "uid": unicode(users[0]["uid"], 'utf-8'),
            "timezone": users[0]["timezone"],
            "avatar": users[0]["pic_square"],
            "access_token": session["session_key"],
            "website": users[0]["website"],
            "birthday_date": users[0]["birthday_date"],
        })

class GoogleLoginHandler(BaseHandler, AuthMixin, tornado.auth.GoogleMixin):
    @tornado.web.asynchronous
    def get(self):
        if self.get_argument("openid.mode", None):
            self.get_authenticated_user(self.async_callback(self._on_auth))
            return
        self.authenticate_redirect()

    def _on_auth(self, user):
        if not user:
            raise tornado.web.HTTPError(500, "Authentication failed")

        self.log(user)
        super(GoogleLoginHandler, self)._on_auth(
            {
                'auth_provider': 'google',
                'uid': user['email'],
                'fullname': user['name']
            }
        )

class TwitterLoginHandler(BaseHandler, AuthMixin, tornado.auth.TwitterMixin):
    @tornado.web.asynchronous
    def get(self):
        if self.get_argument("oauth_token", None):
            self.get_authenticated_user(self.async_callback(self._on_auth))
            return
        self.authorize_redirect()

    def _on_auth(self, user):
        if not user:
            raise tornado.web.HTTPError(500, "Authentication failed")
        self.log(user)
        super(TwitterLoginHandler, self)._on_auth(
            {
                'auth_provider': 'twitter',
                'uid': user['username'],
                'access_token': user['access_token'],
                'about': user['description'],
                'timezone': user['time_zone'],
                'avatar': user['profile_image_url'],
                'website': user['url']
            }
        )
