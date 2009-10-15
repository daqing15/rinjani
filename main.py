#!/usr/bin/python -u

import os.path
import sys
sys.path.insert(0, os.path.dirname(__file__) + "/lib")

import re
import httplib
import logging
import tornado.httpserver
import tornado.ioloop
import tornado.locale
from handlers.main import MissingHandler
from application import BaseApplication
import uimodules
import settings

class Application(BaseApplication):
    def __init__(self):
        app_settings = settings.app_settings
        app_settings['ui_modules'] = uimodules
        super(Application, self).__init__(settings.url_handlers, **app_settings)

app = Application()
tornado.locale.load_translations(os.path.join(os.path.dirname(__file__), "translations"))

def main():
    app.handlers[0][1].append((re.compile(r'/(.+)$'), MissingHandler, {}))
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(getattr(settings, 'port', 8888))
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
