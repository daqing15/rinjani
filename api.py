#!/usr/bin/python -W ignore::DeprecationWarning
import os.path
import sys
DIR = os.path.abspath(os.path.dirname(__file__))
sys.path = [ DIR, os.path.join(DIR, "lib") ] + sys.path

import logging
import httplib
import hashlib
import datetime
import simplejson

import tornado.httpserver
import tornado.options
import tornado.ioloop
import tornado.web
from tornado.options import define, options, parse_command_line
from web.utils import Storage

from forms import api_request_form
from models import IS, Simpledoc, User, Article, Activity, CONTENT_MAP
from rinjani.string import generate_random_password
from rinjani.pagination import Pagination
from rinjani.json import JSONEncoder

KEY_SIZE = 18
SECRET_SIZE = 32
VERIFIER_SIZE = 10
CONSUMER_STATES = [u'pending', u'confirmed', u'accepted', u'rejected']
HEADER_SERVER = 'PeduliAPI/0.1a'

class Consumer(Simpledoc):
    collection_name = 'consumers'
    structure = {
            'fullname': unicode,
            'website': unicode,
            'about': unicode,
            'key': unicode,
            'secret': unicode,
            'status': IS(*CONSUMER_STATES),
            'created_at': datetime.datetime
        }
    required_fields = ['email', 'fullname', 'about', 'key', 'secret']
    default_values = {'status': u'pending', 'created_at':datetime.datetime.utcnow}
    
    def generate_random_code(self):
        key = generate_random_password(length=KEY_SIZE)
        secret = generate_random_password(length=SECRET_SIZE)
        
        while self.one({'key': key}):
            key = generate_random_password(length=KEY_SIZE) 
            
        return key, secret
    
class authenticated(object):
    """Decorate methods with this to require authenticated access"""
    def __init__(self, group=None, admin=False, verified=False):
        pass
    
    def __call__(self, method):
        cls = self
        def wrapped_method(self, *args, **kwargs):
            username = self.get_argument('username')
            password = hashlib.sha1(self.get_argument('password'))
            self.unauthenticated_response()
            return
        return wrapped_method
    
class BaseHandler(tornado.web.RequestHandler):
    def get_arguments(self):
        return dict([(k, self.get_argument(k)) \
              for k,_v in self.request.arguments.iteritems() \
                if not k.startswith('_')])
        
class APIHandler(BaseHandler):
    def __init__(self, application, request, transforms=None):
        super(APIHandler, self).__init__(application, request, transforms)
        key = self.get_argument('key', None)
        secret = self.get_argument('secret', None)
        
        if key and secret:
            consumer = Consumer.one({'key': key, 'secret': secret})
            if consumer:
                return
            return self.error_response("Invalid key/secret", 403)
        return self.unauthenticated_response()
    
    def get_model(self, type):
        return Article if type == 'articles' else Activity
        
    def finish(self, chunk):
        self.set_header("Content-Type", "text/javascript; charset=UTF-8")
        super(APIHandler, self).finish(chunk)
        
    def get_error_html(self, status_code):
        message = httplib.responses[status_code]
        return {'error_text': message}
    
    def response(self, data):
        chunk = simplejson.dumps({'success_text':'ok', 'data': data}, 
                                 cls=JSONEncoder)
        self.finish(chunk)
        
    def error_response(self, message, code=None):
        code = code or 400
        self.set_status(code)
        self.finish({'error_text': message})
    
    def unauthenticated_response(self):
        self.error_response('Requires key/secret information', 403)
    
    def unauthorized_response(self):
        self.error_response('You dont have sufficient privileges', 403)
    
    def bad_request_response(self):
        self.error_response('Incomplete/invalid request body', 400)
        
class ContentHandler(APIHandler):
    def get(self, type, slug):
        spec = {'status': 'published', 'slug': 'slug'}
        doc = self.get_model(type).one()
         
    @authenticated()
    def post(self): pass
    
    @authenticated()
    def put(self): pass
    
    @authenticated()
    def delete(self): pass

class ListHandler(APIHandler):
    def get(self, type):
        cls = self.get_model(type)
        spec = {'status':'published'}
        pagination = Pagination(self, cls, spec,
                                per_page=1, fields=cls.api_fields, wrap=False)
        docs = [doc for doc in pagination.get_objects()]
        self.response(docs)

class RequestHandler(BaseHandler):
    def get(self, action=None):
        f = api_request_form()
        self.render('api-request.html', f=f)
    
    def post(self):
        self.check_xsrf_cookie()
        f = api_request_form()
        data = self.get_arguments()
        
        try:
            if f.validates(Storage(data)):
                consumer = Consumer()
                consumer['_id'] = data['email']
                consumer['about'] = data['about']
                consumer['fullname'] = data['fullname']
                consumer['website'] = data['website']
                consumer['key'], consumer['secret'] = \
                    Consumer.generate_random_code()
                
                if consumer.validate():
                    consumer.save()
                    self.redirect('/')
            raise Exception("Form still have errors.")
        except Exception, e:
            f.note = f.note if f.note else e 
            self.render('api-request.html', f=f)
        
class HomeHandler(BaseHandler):
    def get(self):
        self.render('api-home.html')
        
class RegisterHandler(APIHandler):
    def post(self):
        pass


define("host", default='127.0.0.1', help="run on the given host (default 127.0.0.1)", type=str)
define("port", default=2222, help="run on the given port", type=int)

class Application(tornado.web.Application):
    def __init__(self):
        static_dir = DIR + '/static'
        handlers = [
            (r'/(articles|projects)', ListHandler),
            (r'/(article|project|page|post)/([\w\-]+)', ContentHandler),
            (r'/activate/\w+', RequestHandler),
            (r'/request', RequestHandler),
            (r'/register', RegisterHandler),
            (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': static_dir}),
            (r'/', HomeHandler)
        ]
        settings = dict(
            debug=True,
            template_path=os.path.join(DIR, "templates"),
            static_path = os.path.join(DIR, "static"),
            xsrf_cookies = False,
            cookie_secret="xkBeTzKXQApCYqpL5gEmGeJJFuYh7EQnp2XdTP1o/Vom",
        )
        tornado.web.Application.__init__(self, handlers, **settings)
        
def runserver():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port, options.host)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    runserver()
    
