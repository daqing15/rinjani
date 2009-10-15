import markdown2
from .main import BaseHandler, authenticated
from forms import article_form, InvalidFormDataError
from models import EditDisallowedError, Article, User
from web.utils import Storage
from utils.pagination import Pagination
import tornado.web

PERMISSION_ERROR_MESSAGE = "You are not allowed to edit this article"

class ListHandler(BaseHandler):
    def get(self):
        pagination = Pagination(self, Article, {})
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
                if is_edit:
                    article = Article.one({'slug': data['slug']})
                    article.check_edit_permission(self.get_current_user())
                    #SchemaTypeError: author must be an instance of User not SON
                    article['author'] = User.one({'username':article['author']['username']})
                else:
                    article = Article()
                    article['author'] = self.get_current_user()
                    
                article.populate(data)
                tags = data.get('tags', None)
                if tags:
                    tags = [tag.strip() for tag in tags.split(',')]
                    article['tags'] = tags
                
                article.validate()
                article.fill_slug_field(data['title'])
                article['content_html'] = markdown2.markdown(data['content'])
                article.save()
                self.set_flash("Article has been saved.")
                self.redirect(article.get_url())
                return
            raise Exception("Invalid form data")
        except EditDisallowedError:
            self.set_flash(PERMISSION_ERROR_MESSAGE)
            self.redirect(article.get_url())
        except Exception, e:
            self.render("article-edit", f=f, slug=None)
        
        