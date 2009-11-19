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


import tornado.web
from tornado.web import RequestHandler, RedirectHandler
from pymongo.errors import ConnectionFailure, AutoReconnect
from utils.mod import get_mod_handler, import_module

class ErrorHandler(tornado.web.RequestHandler):
    def __init__(self, application, request, status_code, message=""):
        self.message = message
        self.status_code = self.set_status(status_code)
        super(ErrorHandler, self).__init__(application, request)
    
    def get_error_html(self, status_code):
        return self.render_string(status_code)
    
    @property
    def template_vars(self):
        return {}
    
    def render_string(self, template, **kwargs):
        kwargs = {'BP':'', 'message': self.message}
        if self.settings:
            kwargs.update({'settings': tornado.web._O(self.application.settings)})
        return super(ErrorHandler, self).render_string("%d.html" % self.status_code, **kwargs)

class MissingHandler(ErrorHandler):
    def __init__(self, application, request, transforms=None):
        super(MissingHandler, self).__init__(application, request, 404)
    
class BaseApplication(tornado.web.Application):
    def __call__(self, request):
        """
        Called by HTTPServer to execute the request.
        monkey-patched to allow handler to be string, not class
        plus handle MongoDB connection error
        """
        transforms = [t(request) for t in self.transforms]
        handler = None
        args = []
        handlers = self._get_host_handlers(request)
        if not handlers:
            handler = RedirectHandler(
                request, "http://" + self.default_host + "/")
        else:
            if request.path != "/":
                request.path = request.path.rstrip('/')
            for pattern, handler_class, kwargs in handlers:
                match = pattern.match(request.path)
                if match:
                    if not callable(handler_class):
                        try:
                            mod_name, handler_classname = get_mod_handler(handler_class)
                            handler_class = import_module(mod_name, handler_classname)
                            handler = handler_class(self, request, **kwargs)
                        except (AutoReconnect, ConnectionFailure):
                            handler = ErrorHandler(self, request, 500, "Database Connection Error")
                            
                    args = match.groups()
                    break
            if not handler:
                handler = ErrorHandler(self, request, 404)
        
        # force debug if ip in registered remote debugger ips
        if self.settings.get("debug_ip", None):
            if request.remote_ip in self.settings.get("debug_ip"):
                self.settings['debug'] = True
                
        # In debug mode, re-compile templates and reload static files on every
        # request so you don't need to restart to see changes
        if self.settings.get("debug"):
            RequestHandler._templates = None
            RequestHandler._static_hashes = {}
        
        handler._execute(transforms, *args)
            
        return handler
    
