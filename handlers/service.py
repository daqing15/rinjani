from main import BaseHandler, from_local

class testHandler(BaseHandler):
    @from_local
    def get(self,param=None):
        self.finish("HI")