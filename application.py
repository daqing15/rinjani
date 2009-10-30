"""
Blah blah
@author: apit
"""

import tornado.web
from tornado.web import ErrorHandler, RequestHandler, RedirectHandler

from utils.mod import get_mod_handler, import_module

class BaseApplication(tornado.web.Application):
    def __call__(self, request):
        """
        Called by HTTPServer to execute the request.
        monkey-patched to allow handler to be string, not class
        """
        transforms = [t(request) for t in self.transforms]
        handler = None
        args = []
        handlers = self._get_host_handlers(request)
        if not handlers:
            handler = RedirectHandler(
                request, "http://" + self.default_host + "/")
        else:
            for pattern, handler_class, kwargs in handlers:
                match = pattern.match(request.path)
                if match:
                    # here comes the patch
                    if not callable(handler_class):
                        mod_name, handler_classname = get_mod_handler(handler_class)
                        handler_class = import_module(mod_name, handler_classname)
                    # end of patch
                    handler = handler_class(self, request, **kwargs)
                    args = match.groups()
                    break
            if not handler:
                handler = ErrorHandler(self, request, 404)
        
        # force debug if ip in registered remote debugger ips
        if self.settings.get("debug_ip"):
            if request.remote_ip in self.settings.get("debug_ip"):
                self.settings['debug'] = True
                
        # In debug mode, re-compile templates and reload static files on every
        # request so you don't need to restart to see changes
        if self.settings.get("debug"):
            RequestHandler._templates = None
            RequestHandler._static_hashes = {}

        handler._execute(transforms, *args)
        return handler
    
    @property
    def queue(self):
        pass
