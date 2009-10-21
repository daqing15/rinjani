# -*- coding: utf-8 -*-
import sys
import urllib
import tornado.web
import logging
import functools
import markdown2
from beakercache import cache
from forms import MyForm
from utils.helper import HtmlHelper
from pymongo.errors import ConnectionFailure


def authenticated(user_type=None, is_admin=False):
    def _authenticated(method):
        """Decorate methods with this to require that the user be logged in."""
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            user = self.current_user
            if not user:
                url = self.get_login_url()
                if "?" not in url:
                    url += "?" + urllib.urlencode(dict(next=self.request.uri))
                self.set_flash("You have to login in order to see that page")
                self.redirect(url)
                return 
            else:
                in_type = True
                if user_type:
                    if isinstance(user_type, list):
                        in_type = user_type.count(user['type'])
                    else:
                        in_type = user['type'] == user_type
                
                if (not user_type and not is_admin) \
                        or (in_type and not is_admin) \
                        or user['is_admin']:
                    return method(self, *args, **kwargs)
                
                if (user_type and not in_type and not user['is_admin']) \
                        or (not user_type and not user['is_admin']):
                    self.set_flash("You dont have privilleges to access that page")
                    self.redirect("/")
                    return
            raise tornado.web.HTTPError(403)
        return wrapper
    return _authenticated

class BaseHandler(tornado.web.RequestHandler):
    def __init__(self, application, request, transforms=None):
        super(BaseHandler, self).__init__(application, request, transforms)
        MyForm.locale = self.get_user_locale()
    
    @cache.cache('current_user')
    def get_current_user(self):
        username = self.get_secure_cookie("username")
        if not username: return None
        from models import User
        return User.one({'username': username})
    
    @property
    def is_logged_in(self):
        """Is the user logged in?"""
        return self.user is not None
    
    @property
    def base_path(self):
        import settings
        return getattr(settings, 'base_path', '')
    
    @property
    def cache(self):
        return self.application.cache
    
    @property 
    def settings(self): 
         return self.application.settings
    
    def set_flash(self, message):
        self.set_secure_cookie("f", message)
        
    def get_user_type(self):
        return self.get_cookie("t")
    
    def get_arguments(self):
        d = {}
        for _d in self.request.arguments.keys():
            if not _d.startswith('_'):
                d[_d] = self.get_argument(_d)
        return d

    def get_user_locale(self):
        # defaulted to bahasa
        loc = self.get_cookie("loc", "id_ID")  
        return tornado.locale.get(loc)

    def get_error_html(self, status_code):
        return self.render_string(str(status_code) + ".html", message=None, **self.template_vars)
    
    @property
    def template_vars(self):
        return dict(
            current_path = self.request.uri, 
            BP = self.base_path,
            h = HtmlHelper,
            settings = self.settings,
            markdown=markdown2.markdown
        ) 
    
    def is_xhr(self): 
        xhr = self.request.headers.get('X-Requested-With', '')
        return  xhr == 'XMLHttpRequest'
    
    # choose template based on request type
    def render(self, template, **kwargs):
        ''' Select appropriate template based on request type and add additional template vars '''
        ext = 'html'
        if self.is_xhr():
            ext = 'ajax'
        template = template + "." + ext
        kwargs.update(self.template_vars)
        super(BaseHandler, self).render(template, **kwargs)

class MissingHandler(BaseHandler):
    def get(self, path):
        self.set_status(404)
        self.render("404", path=path, message=None)


class LocaleHandler(tornado.web.RequestHandler):
    def get(self,loc):
        self.set_cookie("loc", loc)
        self.redirect(self.get_argument("next", "/"))


