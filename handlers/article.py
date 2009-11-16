#
# Copyright 2009 rinjani team
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import tornado.web
import datetime

from web.utils import Storage

from main import BaseHandler, authenticated
from forms import article_form
from settings import CONTENT_TAGS, MY_FLAGS
from models import EditDisallowedError, Article
from utils.pagination import Pagination
from utils.utils import move_attachments, parse_attachments


PERMISSION_ERROR_MESSAGE = "You are not allowed to edit this article"

class ListHandler(BaseHandler):
    def get(self):
        pagination = Pagination(self, Article, {'status':'published'})
        self.render('articles', pagination=pagination)

class ViewHandler(BaseHandler):
    def get(self, slug):
        article = Article.one({'status':'published', "slug": slug})
        if not article:
            raise tornado.web.HTTPError(404)
        Article.collection.update({'slug': slug}, {'$inc': { 'view_count': 1}})
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
        
        self.render("article-edit", f=f, article=article, content_tags=CONTENT_TAGS)
    
    @authenticated()
    def post(self):
        f = article_form()
        data = self.get_arguments()
        is_edit = data.has_key('is_edit')
        
        try:
            attachments = self.get_argument('attachments', None)
            if attachments:
                data['attachments'] = parse_attachments(data['attachments'], is_edit)   
            
            if f.validates(Storage(data)):
                article = Article.one({'slug': data['slug']}) if is_edit else Article()
                article.save(data, user=self.current_user)
                
                if attachments and not is_edit:
                    # ganti sama $push nih
                    article['attachments'] = move_attachments(self.settings.upload_path, data['attachments'])
                    article.update_html()
                    article.save()
                    
                self.set_flash("Article has been saved.")
                url =  article.get_url() if article.status == 'published' else '/dashboard'
                self.redirect(url)
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
            self.render("article-edit", f=f, article=article, content_tags=CONTENT_TAGS)
    
    
class RemoveHandler(BaseHandler):
    def post(self, slug):
        article = Article.one({"slug": slug})
        if not article:
            raise tornado.web.HTTPError(404)
        
        article.remove()
        self.set_flash("That article has been removed")
        self.redirect("/articles")           