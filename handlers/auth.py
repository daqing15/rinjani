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
import binascii
import urllib
import logging
import hashlib
import time
import uuid

from tornado import httpclient
import tornado.auth
import tornado.escape
import web.form

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
        f.validators = [web.form.Validator("The username or password you entered is incorrect", lambda x: bool(user))]
        next = self.get_argument('next', '/dashboard')
        if f.validates(Storage(self.get_arguments())):
            self.set_secure_cookie("username", username)
            from datetime import datetime
            user.last_login = datetime.now()
            user.save()
            self.redirect(next)
        else:
            self.render("login-form", f=f, next=next)


class RegisterHandler(BaseHandler):
    def get(self):
        f = register_form()
        self.render("register", f=f)

    def post(self):
        f = register_form()
        data = self.get_arguments()

        if data.has_key('username'):
            user = User.one({'username': data['username']})
            f.validators.append(web.form.Validator("The username you wanted is already taken",
                                lambda x: not bool(user)) )

        try:
            if f.validates(Storage(data)):
                logging.error(data)
                new_user = User()
                data['is_admin'] = False
                data['password_hashed'] = unicode(hashlib.sha1(data['password']).hexdigest())
                data['auth_provider'] = u'form'
                new_user.save(data)
                self.set_flash("You have been successfully registered. You can log in now.")
                self.redirect("/login-form")
                return
            raise InvalidFormDataError("Form still have errors.")
        except Exception, e:
            f.note = f.note if f.note else e
            self.render("register", f=f)


class NewUserHandler(BaseHandler):
    def get(self):
        if not self.get_secure_cookie("user"):
            raise tornado.web.HTTPError(403, "Authentication cookie does not exists. Please enable Cookie in your browser.")
        self.render("new-user", f=new_user_form())

    def post(self):
        f = new_user_form()
        user_cookie = self.get_secure_cookie("user")
        
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
                logging.info("\n=====\nNEW USER via %s: %s======\n" \
                                 % (user['auth_provider'], user['uid']))

                new_user = User()
                new_user.save(user)

                self.set_secure_cookie("username", user['username'])
                self.clear_cookie("user")
                self.clear_cookie("ap")
                self.set_flash("Thank your for joining with us. You are logged in now.")
                self.redirect("/")
                return
            raise InvalidFormDataError("Form still have errors.")
        except Exception, e:
            f.note = f.note if f.note else e
            self.render("new-user", f=f)

class AuthMixin(object):
    def _on_auth(self, user):
        peduli_user =  User.one({'uid': user['uid'], 'auth_provider': user['auth_provider']})
        if not peduli_user:
            """ New user """
            self.set_secure_cookie("user", tornado.escape.json_encode(user))
            self.set_flash("You have been succefully authenticated. In order to be member, you need complete form shown below.")
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
        
        logging.warning(users)
        callback({
            "auth_provider": "facebook",
            "fullname": users[0]["name"],
            "uid": unicode(users[0]["uid"]),
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
        
        logging.warning(user)
        super(GoogleLoginHandler, self)._on_auth(
            {
                'auth_provider': 'google',
                'uid': user['email'],
                'fullname': user['name']
            }
        )
        
class YahooMixin(tornado.auth.OAuthMixin):
    _OAUTH_REQUEST_TOKEN_URL = "https://api.login.yahoo.com/oauth/v2/get_request_token"
    _OAUTH_ACCESS_TOKEN_URL = "https://api.login.yahoo.com/oauth/v2/get_token"
    _OAUTH_AUTHORIZE_URL = "https://api.login.yahoo.com/oauth/v2/request_auth"
    OAUTH_NO_CALLBACKS = True
    
    def _oauth_request_token_urlX(self):
        consumer_token = self._oauth_consumer_token()
        url = self._OAUTH_REQUEST_TOKEN_URL
        args = dict(
            oauth_consumer_key=consumer_token["key"],
            oauth_signature_method="HMAC-SHA1",
            oauth_timestamp=str(int(time.time())),
            oauth_nonce=binascii.b2a_hex(uuid.uuid4().bytes),
            oauth_version="1.0",
            oauth_callback=self.request.full_url()
        )
        signature = tornado.auth._oauth_signature(consumer_token, "GET", url, args)
        args["oauth_signature"] = signature
        return url + "?" + urllib.urlencode(args)
    
    def _oauth_access_token_url(self, request_token):
        consumer_token = self._oauth_consumer_token()
        url = self._OAUTH_ACCESS_TOKEN_URL
        args = dict(
            oauth_consumer_key=consumer_token["key"],
            oauth_token=request_token["key"],
            oauth_verifier=self.get_argument("oauth_verifier"),
            oauth_signature_method="HMAC-SHA1",
            oauth_timestamp=str(int(time.time())),
            oauth_nonce=binascii.b2a_hex(uuid.uuid4().bytes),
            oauth_version="1.0",
        )
        signature = tornado.auth._oauth_signature(consumer_token, "GET", url, args,
                                     request_token)
        args["oauth_signature"] = signature
        return url + "?" + urllib.urlencode(args)
    
    def _oauth_consumer_token(self):
        self.require_setting("YAHOO_API_KEY", "Yahoo OAuth")
        self.require_setting("YAHOO_SECRET", "Yahoo OAuth")
        return dict(
            key=self.settings["YAHOO_API_KEY"],
            secret=self.settings["YAHOO_SECRET"])
    
    def yahoo_request(self, url, callback, access_token=None,
                           post_args=None, **args):
        # Add the OAuth resource request signature if we have credentials
        if access_token:
            all_args = {}
            all_args.update(args)
            all_args.update(post_args or {})
            method = "POST" if post_args is not None else "GET"
            oauth = self._oauth_request_parameters(
                url, access_token, all_args, method=method)
            args.update(oauth)
        
        args = args if args else {}
        args.update({'format': 'json'})
        url += "?" + urllib.urlencode(args)
        callback = self.async_callback(self._on_yahoo_request, callback)
        http = httpclient.AsyncHTTPClient()
        if post_args is not None:
            http.fetch(url, method="POST", body=urllib.urlencode(post_args),
                       callback=callback)
        else:
            http.fetch(url, callback=callback)
    
    def _on_yahoo_request(self, callback, response):
        if response.error:
            logging.warning("Error response %s fetching %s", response.error,
                            response.request.url)
            callback(None)
            return
        callback(tornado.escape.json_decode(response.body))
        
    def _oauth_get_user(self, access_token, callback):
        callback = self.async_callback(self._parse_user_response, callback)
        logging.error(access_token)
        url = "http://social.yahooapis.com/v1/user/%s/profile" \
                % access_token["xoauth_yahoo_guid"]
        self.yahoo_request(url, callback, access_token)

    def _parse_user_response(self, callback, user):
        if user:
            user["username"] = user["nickname"]
        callback(user)
        
class YahooLoginHandler(BaseHandler, AuthMixin, YahooMixin):
    @tornado.web.asynchronous
    def get(self):
        if self.get_argument("oauth_token", None):
            self.get_authenticated_user(self.async_callback(self._on_auth))
            return
        self.authorize_redirect()

    def _on_auth(self, user):
        if not user:
            logging.error(self.get_arguments())
            raise tornado.web.HTTPError(500, "Authentication failed")
        
        logging.warning(user)
        super(GoogleLoginHandler, self)._on_auth(
            {
                'auth_provider': 'yahoo',
                'uid': user['guid'],
                'fullname': user['nickname']
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
        logging.warning(user)
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
    
class LogoutHandler(BaseHandler, tornado.auth.FacebookMixin):
    def get(self):
        loc = self.get_cookie('loc')
        self.clear_all_cookies()
        if loc:
            self.set_cookie('loc', loc)
        self.redirect(self.get_argument("next", "/"))

