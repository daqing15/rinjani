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

from main import BaseHandler, authenticated
from forms import article_form
from models import EditDisallowedError, Article
from rinjani.pagination import Pagination
from rinjani.utils import move_attachments, parse_attachments

PERMISSION_ERROR_MESSAGE = "You are not allowed to edit this article"

class ListHandler(BaseHandler):
    def get(self, tab):
        spec = {'status':'published'}
        tab = tab or 'latest'
        if tab == 'featured':
            spec.update({'featured':True})
        
        if tab == 'popular':
            pagination = Pagination(self, Article, spec, sort_by='view_count')
        else:
            pagination = Pagination(self, Article, spec)
            
        self.render('articles', pagination=pagination, tab=tab)

class ViewHandler(BaseHandler):
    def get(self, slug):
        spec = {'status':'published', "slug": slug}
        article = Article.one(spec)
        if not article:
            raise tornado.web.HTTPError(404)
        article.increment_view_count()
        self.render("article", article=article)

class EditHandler(BaseHandler):
    @authenticated()
    def get(self, slug=None):
        f = article_form()
        if slug:
            try:
                spec = {'slug':slug}
                article = Article.one(spec)
                article.check_edit_permission(self.get_current_user())
                article.formify()
                f.fill(article)
            except EditDisallowedError:
                self.set_flash(PERMISSION_ERROR_MESSAGE)
                self.redirect(article.get_url())
                return
            except:
                raise tornado.web.HTTPError(500)
        else:
            article = Article()

        self.render("article-edit", f=f, article=article, user=self.current_user)

    @authenticated()
    def post(self, slug=None):
        f = article_form()
        data = self.get_arguments()
        attachments = self.get_argument('attachments', None)
        is_edit = bool(slug)
        
        _ = self._
        
        try:
            if attachments:
                data['attachments'] = parse_attachments(data['attachments'], is_edit)

            if f.validates(tornado.web._O(data)):
                article = Article.one({'slug':slug}) if is_edit else Article()
                article.save(data, user=self.current_user)

                if attachments:
                    # ganti sama $push nih
                    article['attachments'] = move_attachments(self.settings.upload_path, data['attachments'])
                    article.update_html()
                    article.save()

                self.set_flash(_("Article has been saved."))
                url =  article.get_url() if article.status == 'published' else '/dashboard'
                self.redirect(url)
                return
            article = Article()
            raise Exception(_("Form still have errors. Please check for required fields."))
        except EditDisallowedError:
            self.set_flash(PERMISSION_ERROR_MESSAGE)
            self.redirect(article.get_url())
        except Exception, e:
            if attachments:
                article['attachments'] = data['attachments']
            f.note = f.note if f.note else e
            self.render("article-edit", f=f, article=article, user=self.current_user)


class RemoveHandler(BaseHandler):
    def post(self, slug):
        article = Article.one({"slug": slug})
        if not article:
            raise tornado.web.HTTPError(404)

        article.remove()
        self.set_flash(self._("That article has been removed."))
        self.redirect("/articles")
