from .main import BaseHandler, authenticated
from forms import page_form, InvalidFormDataError
from web.utils import Storage
from models import Donation, User
import tornado.web

class ListHandler(BaseHandler):
    @authenticated()
    def get(self):
        user_type = self.get_current_user()['type']
        
        donations = [{}, {}]
        if not donations:
            raise tornado.web.HTTPError(404)
        self.render(user_type + "/donations", donations=donations)
      