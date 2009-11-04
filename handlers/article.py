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
            attachments = self.get_argument('attachments', None)
            if attachments:
                data['attachments'] = self.parse_attachments(data['attachments'], is_edit)   
            
            if f.validates(Storage(data)):
                article = Article.one({'slug': data['slug']}) if is_edit else Article()
                article.save(data, user=self.current_user)
                
                if attachments:
                    self.move_attachments(data['attachments'])
                    
                self.set_flash("Article has been saved.")
                self.redirect(article.get_url())
                return
            article = Article()
            raise Exception("Form still have errors.")
        except EditDisallowedError:
            self.set_flash(PERMISSION_ERROR_MESSAGE)
            self.redirect(article.get_url())
        except Exception, e:
            if attachments:
                article['attachments'] = data['attachments']
            f.note = f.note if f.note else e
            self.render("article-edit", f=f, article=article, suggested_tags=CONTENT_TAGS_COLLECTION)
    
    def move_attachments(self, attachments):
        import shutil, os
        
        def get_path(path):
            basepath = self.settings.upload_path
            path = os.path.join(basepath, path)
            dest_path = os.path.join(basepath, path.lstrip("tmp/"))
            return (path, dest_path)
            
        for a in attachments:
            if a['src'][0:4] == "tmp/":
                shutil.move(*get_path(a['src']))
                shutil.move(*get_path(a['thumb_src']))
            
    
    def parse_attachments(self, _attachments, is_edit=False):
        separator = "$"
        field_separator = "#"
        attachments = []
        
        from utils.utils import sanitize_path
        
        for a in _attachments.split(separator):
            a = a.split(field_separator)
            # no#filetype#src#thumb_src#filename
            prefix = 'tmp' if not is_edit else ''
            src = sanitize_path(a[2], prefix)
            thumb_src = sanitize_path(a[3], prefix)
            attachment = dict(no=int(a[0]), type=a[1], src=src, thumb_src=thumb_src, filename=a[4])
            attachments.append(attachment)
        
        return attachments
    
    
class RemoveHandler(BaseHandler):
    def post(self, slug):
        article = Article.one({"slug": slug})
        if not article:
            raise tornado.web.HTTPError(404)
        
        article.remove()
        self.set_flash("That article has been removed")
        self.redirect("/articles")           