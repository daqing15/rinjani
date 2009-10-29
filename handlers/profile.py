from web.utils import Storage
import web.form
from .main import BaseHandler, authenticated
from models import User, BankAccount
from utils.pagination import Pagination
from utils import extract_input_array
from forms import profile_form, register_form, new_user_form, account_form, InvalidFormDataError
import tornado.web
from tornado.escape import json_decode
import logging
import hashlib
from pymongo.dbref import DBRef

class ViewHandler(BaseHandler):
    def get(self, username):
        user = User.one({'username': username})
        if user == self.current_user:
            self.redirect("/dashboard")
            return
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
            f.validators.append(web.form.Validator("The username you wanted is already taken", 
                                lambda x: not bool(user)) )
        
        try:
            if f.validates(Storage(data)):
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
            raise
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
                    from utils import fillin_fb_data
                    fillin_fb_data(
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
        self.render('profile-account', f=f)
    
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
        self.render('profile-account', f=f)
                    
class EditHandler(BaseHandler):
    @authenticated()
    def get(self):
        from forms import BANKS
        f = profile_form()
        user = self.current_user
        accounts = user.related.bank_accounts()
        accounts = BankAccount.listify(accounts) if accounts else []
        user.formify()
        f.fill(user)
        self.render(user.type + "/profile-edit", f=f, accounts=accounts, BANKS=BANKS)
    
    @authenticated()
    def post(self):
        f = profile_form()
        data = self.get_arguments()
        user = self.current_user
        accounts = extract_input_array(self.request.arguments, 'acc_')
        accounts = User.filter_valid_accounts(accounts)
        logging.warning(accounts)
        try:
            if f.validates(Storage(data)):
                data['bank_accounts'] = accounts
                if data.get('password', None):
                    data['password_hashed'] = hashlib.sha1(data.get('password')).hexdigest()
                user.save(data, user)
                self.set_flash("Profile saved.")
                self.redirect("/dashboard")
                return
            raise InvalidFormDataError("Form still have errors. Please correct them before saving.")
        except Exception, e:
            if not isinstance(e, InvalidFormDataError): raise
            f.note = f.note if f.note else e
            self.render(user.type + '/profile-edit', f=f, accounts=accounts)
        
        
class Dashboard(BaseHandler):
    @authenticated()
    def get(self):
        self.render(self.current_user.type + "/dashboard")

class UserListHandler(BaseHandler):
    def get(self):
        pagination = Pagination(self, User, {}, 1)
        self.render('users', pagination=pagination)

class CommentsHandler(BaseHandler):
    @authenticated()
    def get(self):
        pagination = Pagination(self, User, {}, 1)
        self.render(self.current_user.type + '/comments', pagination=pagination)
    
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
        