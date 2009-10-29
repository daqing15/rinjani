import tornado.web
import logging
from web.utils import Storage

from .main import BaseHandler, authenticated
from forms import article_form
from models import EditDisallowedError, Article
from utils.pagination import Pagination

PERMISSION_ERROR_MESSAGE = "You are not allowed to edit this article"

class ListHandler(BaseHandler):
    def get(self):
        pagination = Pagination(self, Article, {'status':'published'}, 2)
        self.render('articles', pagination=pagination)

class ViewHandler(BaseHandler):
    def get(self, slug):
        article = Article.one({"slug": slug})
        if not article:
            raise tornado.web.HTTPError(404)
        self.render("article", article=article)

class EditHandler(BaseHandler):
    @authenticated()
    def get(self, slug=None):
        f = article_form()
        if slug:
            try:
                article = Article.one({"slug": slug})
                article.check_edit_permission(self.get_current_user())
            except EditDisallowedError:
                self.set_flash(PERMISSION_ERROR_MESSAGE)
                self.redirect(article.get_url())
                return
            except:
                raise tornado.web.HTTPError(404)
            if isinstance(article['tags'], list):
                article['tags'] = ', '.join(article['tags'])
            f.fill(article)
        self.render("article-edit", f=f, slug=slug)
    
    @authenticated()
    def post(self):
        f = article_form()
        data = self.get_arguments()
        is_edit = data.has_key('is_edit')
        
        try:
            if f.validates(Storage(data)):
                article = Article.one({'slug': data['slug']}) if is_edit else Article() 
                article.save(data, user=self.get_current_user())
                self.set_flash("Article has been saved.")
                self.redirect(article.get_url())
                return
            raise Exception("Form still have errors. Please correct them before saving.")
        except EditDisallowedError:
            self.set_flash(PERMISSION_ERROR_MESSAGE)
            self.redirect(article.get_url())
        except Exception, e:
            f.note = f.note if f.note else e
            slug = None if not is_edit else data.get('slug', None)
            self.render("article-edit", f=f, slug=slug)
        
class RemoveHandler(BaseHandler):
    def post(self, slug):
        article = Article.one({"slug": slug})
        if not article:
            raise tornado.web.HTTPError(404)
        
        article.status = u'deleted'
        article.save()
        self.set_flash("That article has been removed")
        self.redirect("/articles")           