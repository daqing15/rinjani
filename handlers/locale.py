import tornado.web

class SetHandler(tornado.web.RequestHandler):
    def get(self,loc):
        supported_locales = set(tornado.locale.get_supported_locales(self.locale))
        if loc in supported_locales:
            self.set_cookie("loc", loc)
        self.redirect(self.get_argument("next", "/"))
