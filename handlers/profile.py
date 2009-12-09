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
import tornado.web
from web.utils import Storage
from pymongo.dbref import DBRef

from main import BaseHandler, authenticated
from models import User, Content, Article, Activity, BankAccount, Comment, get_or_404
from utils.pagination import Pagination, ListPagination
from forms import profile_form, account_form, comment_form, InvalidFormDataError
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

class VerifyHandler(BaseHandler):
    @authenticated(['agent', 'sponsor'])
    def get(self):
        f = account_form()
        self.render('verify', f=f)

    @authenticated(['agent', 'sponsor'])
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
        self.render('verify', f=f)
        
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
        
        _ = self._
        
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
                
                self.set_flash(_("Profile saved."))
                self.redirect("/dashboard")
                return
            raise InvalidFormDataError(_("Form still have errors. Please correct them before saving."))
        except Exception, e:
            if not isinstance(e, InvalidFormDataError): raise
            f.note = f.note if f.note else e
            self.render(user.type + '/profile-edit', f=f, user=user, accounts=accounts, BANKS=BANKS, FIELD_TAGS=FIELD_TAGS)

class FollowHandler(BaseHandler):
    @authenticated()
    def post(self, username):
        user = User.one({'username': username})
        action = self.get_argument('action', 'follow')
        _ = self._
        
        OK = False
        if user:
            follower = self.current_user['username']
            dbaction = '$push' if action == 'follow' else '$pull'
            try:
                User.collection.update({'username': username}, {dbaction: {'followers': follower}})
                User.collection.update({'username': follower}, {dbaction:{'following': username}})
                msg = _('You are now following that user') if action == 'follow' \
                        else _('You are not following that user again.')
                OK = True
            except:
                msg = _('Error. Your admin has been notified. Please try again later.')

            if self.is_xhr():
                user = User.one({'username': username}) # reload user
                html = self.render_string('modules/follow-button', user=user)
                return self.json_response(msg, 'OK' if OK else 'ERROR',\
                            {'html_target':'#followButton', 'html': html})
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
        drafts = Pagination(self, Content, {'user': DBRef(User.collection_name, self.current_user._id), 'status':'draft'}, 5)
        self.render(self.current_user.type + "/dashboard", drafts=drafts)

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
                self.set_flash(self._("Comment has been saved."))
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
        spec = {'type': 'ART', 'status':'published', 'author': DBRef(User.collection_name, user._id)}
        pagination = Pagination(self, Article, spec)
        self.render('public/profile-items', pagination=pagination, user=user, type='articles')

class ActivitiesHandler(BaseHandler):
    def get(self, username):
        user = User.one({'username': username})
        if not user:
            raise tornado.web.HTTPError(404)
        spec = {'type': 'ACT', 'status':'published', 'author': DBRef(User.collection_name, user._id)}
        pagination = Pagination(self, Activity, spec)
        self.render('public/profile-items', pagination=pagination, user=user, type='activities')



