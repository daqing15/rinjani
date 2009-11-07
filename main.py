#!/usr/bin/python

import os.path
import sys
sys.path = [
    '.',
    os.path.dirname(__file__) + "/lib",
    '/usr/lib/python2.6',
    '/usr/lib/python2.6/lib-dynload', 
    '/usr/lib/python2.6/dist-packages', 
    '/usr/lib/python2.6/dist-packages/PIL',
    '/var/lib/python-support/python2.6', 
]

import re
import tornado.httpserver
import tornado.ioloop
import tornado.locale
import tornado.options
from handlers.main import MissingHandler
from application import BaseApplication
import uimodules
from settings import app_settings
from urls import url_handlers

# we'll run one app per core
from tornado.options import define, options
define("port", default=app_settings.get('port', 8888), help="run on the given port", type=int)
define("mobile", default=app_settings.get('mobile', False), help="is this a mobile-site frontend?", type=int)
tornado.options.parse_command_line()

class Application(BaseApplication):
    def __init__(self):
        app_settings['ui_modules'] = uimodules
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
