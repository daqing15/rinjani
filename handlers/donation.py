from .main import BaseHandler, authenticated
from forms import page_form, InvalidFormDataError
from web.utils import Storage
from models import Donation, User, Activity
import tornado.web

class ListHandler(BaseHandler):
    @authenticated()
    def get(self, slug=None):
        user_type = self.get_current_user()['type']
        
        donations = [{}, {}]
        if not donations:
            raise tornado.web.HTTPError(404)
        self.render(user_type + "/donations", donations=donations)

class ConfirmHandler(BaseHandler):
    def get(self, slug):
        user_type = self.get_current_user()['type']
        
        #activity = Activity.one({'slug': slug}, {'title':1, 'author':1})
        donation = {'aaa': 1}
        if not donation:
            raise tornado.web.HTTPError(404)
        
        self.render("donation-confirm", donation=donation)
            