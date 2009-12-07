
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

import os.path
import urllib
import tornado.web
from forms import MyForm
import logging
from models import User
from utils import cache

class authenticated(object):
    """Decorate methods with this to require authenticated access"""
    def __init__(self, allowed_types=None, admin_access=None, verified_access=None):
        if type(allowed_types) is str:
            allowed_types = allowed_types.split(',')
        
        self.allowed_types = allowed_types if allowed_types is not None else []
        self.admin_access = admin_access if admin_access is not None else False
        self.verified_access = verified_access if verified_access is not None else False
    
    def __call__(self, method):
        cls = self
        
        def wrapped_method(self, *args, **kwargs):
            user = self.current_user
            if not user:
                url = self.get_login_url()
                if '?' not in url:
                    url += "?" + urllib.urlencode(dict(next=self.request.uri))
                self.set_flash('You have to login in order to see that page')
                self.redirect(url)
                return 
            else:
                in_type = True
                if cls.allowed_types:
                    in_type = bool(cls.allowed_types.count(user['type']))
                
                if (not cls.allowed_types and not cls.admin_access) \
                        or in_type or user['is_admin']:
                    
                    if not cls.verified_access or (cls.verified_access and (user['is_admin'] or user['is_verified'])):
                        return method(self, *args, **kwargs)
                    
                    self.set_flash('Access to that page is only for verified user. \
                        Please <a href="/profile/verify">verify your account</a>.')
                    self.redirect('/')    
                    return
                if (cls.allowed_types and not in_type and not user['is_admin']) \
                        or (not cls.allowed_types and not user['is_admin']):
                    self.set_flash('You dont have privilleges to access that page')
                    self.redirect('/')
                    return
            raise tornado.web.HTTPError(403)
        return wrapped_method

class BaseHandler(tornado.web.RequestHandler):
    def __init__(self, application, request, transforms=None):
        super(BaseHandler, self).__init__(application, request, transforms)
        is_mobile = False
        if self.settings.is_mobile_site:
            if not self.get_cookie('is_mobile', None):
                from utils.utils import is_mobile_agent
                is_mobile = is_mobile_agent(request)
                self.set_cookie('is_mobile', str(int(is_mobile)))
            else:
                is_mobile = bool(self.get_cookie('is_mobile'))
        self.is_mobile = is_mobile
        MyForm.locale = self.get_user_locale()
    
    def get_current_user(self):
        username = self.get_secure_cookie('username')
        if not username: return None
        return User.one({'username': username})
    
    @property
    def is_logged_in(self):
        """Is the user logged in?"""
        return self.user is not None
    
    @property
    def cache(self):
        return cache.CacheManager()
    
    @property 
    def settings(self): 
        return tornado.web._O(self.application.settings)
    
    def set_flash(self, message):
        self.set_secure_cookie("f", message)
        
    def get_user_type(self):
        return self.get_current_user()['type']
    
    def get_arguments(self):
        return dict([(k, self.get_argument(k)) \
              for k,_v in self.request.arguments.iteritems() \
                if not k.startswith('_')])

    def get_user_locale(self):
        # defaulted to bahasa
        loc = self.get_cookie("loc", "id_ID")  
        return tornado.locale.get(loc)

    def get_error_html(self, status_code):
        return self.render_string(str(status_code), message=None, **self.template_vars)
    
    @property
    def template_vars(self):
        from utils import defaulthelper, string
        
        return dict(
            current_path = self.request.uri, 
            BP = self.settings.BASE_URL,
            get = lambda x,y: x or y,
            log = logging,
            settings = self.settings,
            h = defaulthelper,
            s = string
        ) 
    
    def is_xhr(self): 
        xhr = self.request.headers.get('X-Requested-With', '')
        return  xhr == 'XMLHttpRequest'
    
    def json_response(self, message, status='OK', data=None):
        self.finish(dict(status=status, message=message, data=data))
    
    def prepare(self):
        pass
        
    def render_string(self, template, **kwargs):
        kwargs.update(self.template_vars)
        if self.settings.is_mobile_site:
            template = os.path.join("mobile", template)   
        template += '.html'
        return super(BaseHandler, self).render_string(template, **kwargs)


