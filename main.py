#!/usr/bin/python

import os.path
import sys
sys.path.insert(0, os.path.dirname(__file__) + "/lib")

import re
import logging
import tornado.httpserver
import tornado.ioloop
import tornado.locale
import tornado.options
from handlers.main import MissingHandler
from application import BaseApplication
import uimodules
import settings
from urls import url_handlers

# we'll run one app per core
from tornado.options import define, options
define("port", default=getattr(settings, 'port', 8888), help="run on the given port", type=int)
define("mobile", default=getattr(settings, 'mobile', False), help="is this a mobile-site frontend?", type=int)

class Application(BaseApplication):
    def __init__(self):
        app_settings = settings.app_settings
        app_settings['ui_modules'] = uimodules
        super(Application, self).__init__(url_handlers, **app_settings)

app = Application()
tornado.locale.load_translations(os.path.join(os.path.dirname(__file__), "translations"))

def main():
    tornado.options.parse_command_line()
    app.handlers[0][1].append((re.compile(r'/(.+)$'), MissingHandler, {}))
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
