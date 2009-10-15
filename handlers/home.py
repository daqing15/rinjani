from .main import BaseHandler
from models import Article

class HomeHandler(BaseHandler):
    def get(self):
        articles = Article.all({'slug': 'article-pertama'}) 
        self.render("home", articles=articles)
