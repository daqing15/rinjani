import tornado.web
import logging
import os
import shutil
import datetime

from web.utils import Storage

from main import BaseHandler, authenticated
from forms import article_form, CONTENT_TAGS_COLLECTION
from models import EditDisallowedError, Article
from utils.pagination import Pagination
from utils.utils import sanitize_path
from utils.time import striso_to_date


PERMISSION_ERROR_MESSAGE = "You are not allowed to edit this article"

class ListHandler(BaseHandler):
    def get(self):
        pagination = Pagination(self, Article, {'status':'published'}, 4)
        self.render('articles', pagination=pagination)

class ViewHandler(BaseHandler):
    def get(self, dt, slug):
        logging.error(dt)
        date = striso_to_date(dt)
        one_day = datetime.timedelta(days=1)
        
        article = Article.one({"slug": slug, "created_at": {'$gte': date, '$lte': date + one_day}})
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
                
                if attachments and not is_edit:
                    # ganti sama $push nih
                    article['attachments'] = self.move_attachments(data['attachments'])
                    logging.warning("Moving attachments")
                    article.update_html()
                    article.save()
                    
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
        def get_path(path):
            basepath = self.settings.upload_path
            src = os.path.join(basepath, sanitize_path(path, "tmp"))
            dest = os.path.join(basepath, sanitize_path(path))
            logging.warning("Moving from %s to %s" % (src, dest))
            return (src, dest)
        
        for i, a in enumerate(attachments):
            if a['src'][0:4] == "tmp/":
                shutil.move(*get_path(a['src']))
                shutil.move(*get_path(a['thumb_src']))
                a['src'] = a['src'].lstrip("tmp/")
                a['thumb_src'] = a['thumb_src'].lstrip("tmp/")
                attachments[i] = a
        return attachments
    
    def parse_attachments(self, _attachments, is_edit=False):
        separator = "$"
        field_separator = "#"
        
        attachments = []
        for a in _attachments.split(separator):
            a = a.split(field_separator)
            # filetype#src#thumb_src#filename
            prefix = 'tmp' if not is_edit else ''
            src = sanitize_path(a[1], prefix)
            thumb_src = sanitize_path(a[2], prefix)
            attachment = dict(type=a[0], src=src, thumb_src=thumb_src, filename=a[3])
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