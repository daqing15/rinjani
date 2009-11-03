import tornado.web
import logging
from web.utils import Storage

from main import BaseHandler, authenticated
from forms import article_form, CONTENT_TAGS_COLLECTION
from models import EditDisallowedError, Article
from utils.pagination import Pagination

PERMISSION_ERROR_MESSAGE = "You are not allowed to edit this article"

class ListHandler(BaseHandler):
    def get(self):
        pagination = Pagination(self, Article, {'status':'published'}, 4)
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
                article.formify()
                f.fill(article)
            except EditDisallowedError:
                self.set_flash(PERMISSION_ERROR_MESSAGE)
                self.redirect(article.get_url())
                return
            except:
                raise tornado.web.HTTPError(404)
        else:
            article = Article()
        
        self.render("article-edit", f=f, article=article, suggested_tags=CONTENT_TAGS_COLLECTION)
    
    @authenticated()
    def post(self):
        f = article_form()
        data = self.get_arguments()
        is_edit = data.has_key('is_edit')
        
        try:
            if f.validates(Storage(data)):
                article = Article.one({'slug': data['slug']}) if is_edit else Article()
                if self.request.files.has_key('photo'):
                    self.update_attachments(article, self.request.files['attachments'])                        
                article.save(data, user=self.current_user)
                self.set_flash("Article has been saved.")
                self.redirect(article.get_url())
                return
            article = Article()
            raise Exception("Form still have errors.")
        except EditDisallowedError:
            self.set_flash(PERMISSION_ERROR_MESSAGE)
            self.redirect(article.get_url())
        except Exception, e:
            f.note = f.note if f.note else e
            slug = None if not is_edit else data.get('slug', None)
            self.render("article-edit", f=f, article=article, suggested_tags=CONTENT_TAGS_COLLECTION)
    
    def update_attachments(self, article, attachments):
        from utils.utils import unique_filename, save_user_upload
        if attachments:
            uploaded_photos = []
            for p in attachments:
                filename = unique_filename([self.current_user.username, 'article', p['filename']])
                save_user_upload(self.upload_dir, filename, p['body'])
                uploaded_photos.append(filename)
                logging.error("%s - %s" % (p['content_type'], p['filename']))
        
        if article._id:
            pass
        
class RemoveHandler(BaseHandler):
    def post(self, slug):
        article = Article.one({"slug": slug})
        if not article:
            raise tornado.web.HTTPError(404)
        
        article.remove()
        self.set_flash("That article has been removed")
        self.redirect("/articles")           