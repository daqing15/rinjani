from .main import BaseHandler
from forms import article_form, InvalidFormDataError
from models import Article
from web.utils import Storage
from utils.string import slugify
from utils.pagination import Pagination
import tornado.web

class ListHandler(BaseHandler):
    def get(self):
        pagination = Pagination(self, Article, {})
        self.render('tags', pagination=pagination)

class ViewHandler(BaseHandler):
    def get(self, slug):
        article = Article.one({"slug": slug})
        if not article:
             raise tornado.web.HTTPError(404)
        self.render("article", article=article)
