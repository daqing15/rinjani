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
from pymongo.dbref import DBRef

from main import BaseHandler, authenticated
from models import CONTENT_TYPE, User, Content, BankAccount, Comment, get_or_404
from utils.pagination import Pagination
from forms import profile_form, password_form, preferences_form, comment_form, InvalidFormDataError
from utils.utils import extract_input_array, move_attachments, parse_attachments

USER_TYPE = {'social org':'agent', 'sponsor': 'sponsor', 'public':'public'}

class AboutHandler(BaseHandler):
    def get(self, username):
        user = get_or_404(User, {'username': username})
        self.render("profile/about", user=user)

class DashboardHandler(BaseHandler):
    @authenticated()
    def get(self):
        user = self.current_user
        self.redirect("profile/%s" % user.username)
        
class PreferenceHandler(BaseHandler):
    @authenticated()
    def get(self):
        f_pwd = password_form()
        f_pref=preferences_form()
        prefs = self.current_user['preferences']
        f_pref.fill(tornado.web._O(prefs))
        self.render('profile/preference', user=self.current_user, f_pwd=f_pwd, f_pref=f_pref)

    @authenticated()
    def post(self):
        _ = self._
        f_pwd = password_form()
        f_pref = preferences_form()
        action = self.get_argument('action', 'pref')
        f = f_pwd if action == 'chpass' else f_pref
        
        data = self.get_arguments()
        del(data['action'])
        try:
            if f.validates(tornado.web._O(data)):
                user = self.current_user
                if action == 'chpass':
                    user['password_hashed'] = hashlib.sha1(data.get('password')).hexdigest()
                    message = _("Your password has been changed.")
                else:
                    user['preferences'] = data
                    message = _("Your preference has been saved.")
                user.save(data)
                self.set_flash(message)
                self.redirect("/preferences")
                return
            raise InvalidFormDataError(_("Form still have errors."))
        except Exception, e: 
            f.note = f.note if f.note else e
        self.render('account', f_pwd=f_pwd, f_pref=f_pref)

class VerifyHandler(BaseHandler):
    @authenticated(['agent', 'sponsor'])
    def get(self):
        f =password_form()
        self.render('verify', f=f)

    @authenticated(['agent', 'sponsor'])
    def post(self):
        f = password_form()
        data = self.get_arguments()
        user = self.current_user
        try:
            if f.validates(tornado.web._O(data)):
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
        self.render("profile/edit", f=f, user=user, accounts=accounts)

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

            if f.validates(tornado.web._O(data)):
                data['bank_accounts'] = accounts
                if data.get('password', None):
                    data['password_hashed'] = hashlib.sha1(data.get('password')).hexdigest()
                user.save(data, user)

                if attachments:
                    user['attachments'] = move_attachments(self.settings.upload_path, data['attachments'])
                    user.update_html()
                    user.save()
                
                self.set_flash(_("Profile saved."))
                self.redirect("/profile/%s" % user.username)
                return
            raise InvalidFormDataError(_("Form still have errors. Please correct them before saving."))
        except Exception, e:
            if not isinstance(e, InvalidFormDataError): raise
            f.note = f.note if f.note else e
            self.render('profile/edit', f=f, user=user, accounts=accounts)

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


class UserListHandler(BaseHandler):
    def get(self):
        tab = self.get_argument('tab', 'social org')
        try:
            type = USER_TYPE[tab]
        except:
            type = USER_TYPE['social org']
        pagination = Pagination(self, User, {'type':type})
        self.render('users', pagination=pagination, tab=tab)


class ProfileHandler(BaseHandler):
    def get_comments_for(self, user):
        spec = {'for': DBRef(User.collection_name, user._id)}
        return Pagination(self, Comment, spec)

    def get(self, username):
        user = User.one({'username': username})
        if not user:
            raise tornado.web.HTTPError(404)
        
        if user == self.current_user and user.is_admin:
            self.redirect('/admin')
            return
        
        pagination = self.get_comments_for(user)
        f = comment_form()
        self.render('profile/wall', pagination=pagination, user=user, f=f)

    @authenticated()
    def post(self, username):
        user, pagination = self.get_comments_for(username)
        f = comment_form()
        data = self.get_arguments()
        try:
            if f.validates(tornado.web._O(data)):
                comment = Comment()
                comment.save(
                        { 'from': self.current_user,
                          'for': user,
                          'comment': data['comment']
                         }
                    )
                self.set_flash(self._("Comment has been saved."))
                self.redirect("/profile/%s" % username)
                return
            raise Exception()
        except Exception, e:
            f.note = f.note if f.note else e
            self.render('profile/%s' % username, pagination=pagination, user=user, f=f)

class ContentHandler(BaseHandler):
    def get(self, username, type):
        user = User.one({'username': username})
        if not user:
            raise tornado.web.HTTPError(404)
        ctype = type[:-1] if type in ['articles', 'pages'] else 'activity'
        ctype = getattr(CONTENT_TYPE, ctype.upper())
        spec = {'type': ctype, 'status':'published', 'author': DBRef(User.collection_name, user._id)}
        pagination = Pagination(self, Content, spec)
        self.render('profile/items', pagination=pagination, user=user, type=type)



