"""
Blah blah
@author: apit
"""

import tornado.web
from tornado.web import RequestHandler, RedirectHandler

from utils.mod import get_mod_handler, import_module
from pymongo.errors import ConnectionFailure, AutoReconnect
from handlers.main import ErrorHandler
import logging

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
            if request.path != "/":
                request.path = request.path.rstrip('/')
            for pattern, handler_class, kwargs in handlers:
                match = pattern.match(request.path)
                if match:
                    # here comes the patch
                    if not callable(handler_class):
                        try:
                            mod_name, handler_classname = get_mod_handler(handler_class)
                            handler_class = import_module(mod_name, handler_classname)
                            handler = handler_class(self, request, **kwargs)
                        except ConnectionFailure:
                            logging.critical("=======DB Connection error=============")
                            handler = ErrorHandler(self, request, 500, message="DB died?")
                    # end of patch
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
        
        try:
            handler._execute(transforms, *args)
        except AutoReconnect:
            from pymongo.connection import Connection
            logging.critical("===== Reconnects to DB ========")
            Connection("localhost", 27017)
            RequestHandler(self, request, 500)._execute(transforms, *args)
        except:
            logging.critical("=========WTF? ===========")
            RequestHandler(self, request, 500)._execute(transforms, *args)
            
        return handler
    
    @property
    def queue(self):
        pass
