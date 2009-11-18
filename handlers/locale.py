import tornado.web

class SetHandler(tornado.web.RequestHandler):
    def get(self,loc):
        if loc in ['id_ID', 'en_US']:
            self.set_cookie("loc", loc)
        self.redirect(self.get_argument("next", "/"))
