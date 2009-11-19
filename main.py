#!/usr/bin/python

import os.path
import sys

DIR = os.path.abspath(os.path.dirname(__file__))
sys.path = [ DIR, os.path.join(DIR, "lib") ] + sys.path

import re
import tornado.httpserver
import tornado.ioloop
import tornado.locale
import tornado.options

from application import BaseApplication, MissingHandler
import uimodules
from urls import url_handlers

def get_settings():
    import settings
    return dict([(varname,getattr(settings,varname))
         for varname in dir(settings)
         if not varname.startswith("_") ])

app_settings = get_settings()

# we'll run one app per core
from tornado.options import define, options
define("port", default=app_settings.get('PORT', 8888), help="run on the given port", type=int)
define("mobile", default=app_settings.get('MOBILE', False), help="is this a mobile-site frontend?", type=int)
tornado.options.parse_command_line()

class Application(BaseApplication):
    def __init__(self):
        app_settings['ui_modules'] = uimodules
        app_settings['is_mobile_site'] = bool(options.mobile)
        super(Application, self).__init__(url_handlers, **app_settings)

app = Application()
tornado.locale.load_translations(os.path.join(os.path.dirname(__file__), "translations"))

def main():
    app.handlers[0][1].append((re.compile(r'/(.+)$'), MissingHandler, {}))
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
