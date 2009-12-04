#!/usr/bin/python
import os.path
import sys
DIR = os.path.abspath(os.path.dirname(__file__))
sys.path = [ DIR, os.path.join(DIR, "lib") ] + sys.path

import tornado.httpserver
import tornado.ioloop
import tornado.locale
from tornado.options import define, options, parse_command_line

from application import Application

define("host", default='127.0.0.1', help="run on the given host (default 127.0.0.1)", type=str)
define("port", default=9999, help="run on the given port", type=int)
define("mobile", default=False, help="is this a mobile-site frontend?", type=bool)
args = parse_command_line()

def runserver():
    tornado.locale.load_translations(\
        os.path.join(os.path.dirname(__file__), "translations"))
    
    app = Application(options)
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port, options.host)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    runserver()
    
    
