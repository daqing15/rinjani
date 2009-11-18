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

import logging
import hashlib

import tornado.web
from tornado.escape import json_decode
from web.utils import Storage
import web.form
from pymongo.dbref import DBRef

from main import BaseHandler, authenticated
from models import User, Article, Activity, BankAccount, Comment, get_or_404
from utils.pagination import Pagination, ListPagination
from forms import profile_form, register_form, new_user_form, account_form, comment_form, InvalidFormDataError
from utils.utils import extract_input_array, move_attachments, parse_attachments
from settings import BANKS, FIELD_TAGS


USER_TYPE = {'social org':'agent', 'sponsor': 'sponsor', 'public':'public'}

class ViewHandler(BaseHandler):
    def get(self, username):
        user = get_or_404(User, {'username': username})
        #if user == self.current_user:
        #    self.redirect("/dashboard")
        #    return
        self.render("profile", user=user)

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
        f = new_user_form()
        user_cookie = self.get_secure_cookie("user")
        if not user_cookie:
            raise tornado.web.HTTPError(403, "Direct access to new-user page")
        
        self.render("new-user", f=f)
    
    def post(self):
        f = new_user_form()
        data = self.get_arguments()
        user_cookie = self.get_secure_cookie("user")
        if not user_cookie:
            raise tornado.web.HTTPError(403, "Direct access to new-user page")
        
        if data.has_key('username'):
            user = User.one({'username': data['username']})
            f.validators.append(web.form.Validator("The username you wanted is already taken", 
                                lambda x: not bool(user)) )
            
        try:
            if f.validates(Storage(data)):
                data.update(json_decode(user_cookie))
                
                """
                if data['auth_provider'] == 'facebook':
                    from utils import fill_fb_data
                    data = fillin_fb_data(
                            self.settings['facebook_api_key'], 
                            self.settings['facebook_secret'],
                            ['pic_square', 'pic_smal', 'sex', 'website', 'birthday_date', 
                             'timezone', 'interests'],
                            data
                            )
                """
                 
                user = User()
                logging.info("\n=============\nNEW USER via %s: %s %s============\n" \
                                 % (user['auth_provider'], user['first_name'], user['last_name']))
                user.save(data)
                self.set_secure_cookie("username", user['username'])
                self.clear_cookie("user")
                self.clear_cookie("ap")
                self.set_flash("Thank your for joining with us. You may log in anytime.")
                self.redirect("/")
                return
            raise InvalidFormDataError("Form still have errors.")
        except Exception, e:
            f.note = f.note if f.note else e
            self.render("new-user", f=f)

class AccountHandler(BaseHandler):
    @authenticated()
    def get(self):
        f = account_form()
        self.render('account', f=f)
    
    @authenticated()
    def post(self):
        f = account_form()
        data = self.get_arguments()
        user = self.current_user
        try:
            if f.validates(Storage(data)):
                if data.get('password', None):
                    data['password_hashed'] = hashlib.sha1(data.get('password')).hexdigest()
                    user.save(data)
                    self.set_flash("Your password has been changed.")
                    self.redirect("/account")
                    return
            raise InvalidFormDataError("Form still have errors.")
        except: pass
        self.render('account', f=f)
                    
class EditHandler(BaseHandler):
    @authenticated()
    def get(self):
        f = profile_form()
        user = self.current_user
        accounts = user.get_bank_accounts()
        accounts = BankAccount.listify(accounts) if accounts.count() else []
        user.formify()
        f.fill(user)
        self.render(user.type + "/profile-edit", f=f, user=user, accounts=accounts, BANKS=BANKS, FIELD_TAGS=FIELD_TAGS)
    
    @authenticated()
    def post(self):
        f = profile_form()
        data = self.get_arguments()
        user = self.current_user
        accounts = extract_input_array(self.request.arguments, 'acc_')
        accounts = User.filter_valid_accounts(accounts)
        try:
            attachments = self.get_argument('attachments', None)
            if attachments:
                data['attachments'] = parse_attachments(data['attachments'], True)  
                
            if f.validates(Storage(data)):
                data['bank_accounts'] = accounts
                if data.get('password', None):
                    data['password_hashed'] = hashlib.sha1(data.get('password')).hexdigest()
                user.save(data, user)
                
                if attachments:
                    user['attachments'] = move_attachments(self.settings.upload_path, data['attachments'])
                    user.update_html()
                    user.save()
                    
                self.set_flash("Profile saved.")
                self.redirect("/dashboard")
                return
            raise InvalidFormDataError("Form still have errors. Please correct them before saving.")
        except Exception, e:
            if not isinstance(e, InvalidFormDataError): raise
            f.note = f.note if f.note else e
            self.render(user.type + '/profile-edit', f=f, user=user, accounts=accounts, BANKS=BANKS, FIELD_TAGS=FIELD_TAGS)

class FollowHandler(BaseHandler):
    @authenticated()
    def post(self, username):
        user = User.one({'username': username})
        
        action = self.get_argument('action', 'follow')
        
        OK = False
        if user:
            follower = self.current_user['username']
            dbaction = '$push' if action == 'follow' else '$pull' 
            try:
                User.collection.update({'username': username}, {dbaction: {'followers': follower}})
                msg = 'You are now following that user' if action == 'follow' \
                    else 'You are not following that user again'
                OK = True
            except:
                msg = 'Error. Your admin has been notified. Please try again later'
                  
            if self.is_xhr():
                return self.json_response(msg, 'OK' if OK else 'ERROR',\
                    self.render_string('modules/user-block', user=user))
            else:
                self.set_flash(msg)
        self.redirect(self.get_argument('next'))

class FollowersHandler(BaseHandler):
    def get(self, username):
        user = get_or_404(User, {'username': username})
        pagination = ListPagination(self, user.followers)
        self.render("profile-followers", user=user, pagination=pagination)
                
class Dashboard(BaseHandler):
    @authenticated()
    def get(self):
        pg_article = Pagination(self, Article, {'status':'draft'}, 5)
        pg_activity = Pagination(self, Activity, {'status':'draft'}, 5)
        self.render(self.current_user.type + "/dashboard", pg_article=pg_article, pg_activity=pg_activity)

class UserListHandler(BaseHandler):
    def get(self):
        tab = self.get_argument('tab', 'social org')
        try:
            type = USER_TYPE[tab]
        except:
            type = USER_TYPE['social org']
        pagination = Pagination(self, User, {'type':type})
        self.render('users', pagination=pagination, tab=tab)

class CommentsHandler(BaseHandler):
    @authenticated()
    def get(self):
        pagination = Pagination(self, User, {}, 1)
        self.render(self.current_user.type + '/comments', pagination=pagination)
    
    @authenticated()
    def post(self):
        pass
        
class ProfileCommentsHandler(BaseHandler):
    def get_comments_for(self, username):
        user = User.one({'username': username})
        if not user:
            raise tornado.web.HTTPError(404)
        spec = {'for': DBRef(User.collection_name, user._id)}
        return (user, Pagination(self, Comment, spec))
    
    def get(self, username):
        import math
        user, pagination = self.get_comments_for(username)
        f = comment_form()
        self.render('public/profile-comments', pagination=pagination, user=user, f=f, math=math)
    
    @authenticated()
    def post(self, username):
        user, pagination = self.get_comments_for(username)
        f = comment_form()
        data = self.get_arguments()
        try:
            if f.validates(Storage(data)):
                comment = Comment()
                comment['from'] = self.current_user
                comment['for'] = user
                comment['comment'] = data['comment']
                comment.save()
                self.set_flash("Comment has been saved")
                self.redirect("/profile/comments/" + username)
                return
            raise Exception()
        except Exception, e:
            f.note = f.note if f.note else e
            self.render('public/profile-comments', pagination=pagination, user=user, f=f)

class ArticlesHandler(BaseHandler):
    def get(self, username):
        user = User.one({'username': username})
        if not user:
            raise tornado.web.HTTPError(404)
        spec = {'status':'published', 'author': DBRef(User.collection_name, user._id)}
        pagination = Pagination(self, Article, spec)
        self.render('public/profile-items', pagination=pagination, user=user, type='articles')
            
class ActivitiesHandler(BaseHandler):
    def get(self, username):
        user = User.one({'username': username})
        if not user:
            raise tornado.web.HTTPError(404)
        spec = {'status':'published', 'author': DBRef(User.collection_name, user._id)}
        pagination = Pagination(self, Activity, spec)
        self.render('public/profile-items', pagination=pagination, user=user, type='activities')
    


