import os
import time
import tornado.web
from pymongo.connection import Connection
from beakercache import cache
import logging

class BaseUIModule(tornado.web.UIModule):
    def render_string(self, path, **kwargs):
        ''' add additional vars to be available to template here'''
        kwargs.update(self.handler.template_vars)
        return super(BaseUIModule, self).render_string(path, \
            next = self.request.uri, 
            **kwargs)

class ActivityLatest(BaseUIModule):
    def render(self, **kwargs):
        from models import Activity
        activities = Activity.all().sort([('created_at', -1)]).limit(5)
        if activities:
            return self.render_string("modules/activities-latest.html", activities=activities)
        else: return ''

class ActivitySupporters(BaseUIModule):
    def render(self, activity):
        supporters = self.handler.get_current_user()
        if supporters:
            return self.render_string("modules/activity-supporters.html", supporters=supporters)
        else: return ''        
        
class AgentFeatured(BaseUIModule):
    def render(self, **kwargs):
        agents = []
        return self.render_string("modules/agents-featured.html", agents=agents)
                
class ArticleLatest(BaseUIModule):
    def render(self, **kwargs):
        from models import Article
        articles = Article.all().sort([('created_at', -1)]).limit(5)
        if articles:
            return self.render_string("modules/articles-latest.html", articles=articles)
        else: return ''
        
class ArticleStat(BaseUIModule):
    def render(self, id):
        stat = {}
        return self.render_string("modules/article-stat.html", stat=stat)

class ArticlesRelated(BaseUIModule):
    def render(self, tags):
        return self.render_string("modules/articles-related.html", articles={}) 

class Cloud(BaseUIModule):
    def render(self, **kwargs):
        return self.render_string("modules/cloud.html")

class CommentBox(BaseUIModule):
    def render(self, **kwargs):
        from forms import commentbox_form
        f = commentbox_form()
        return self.render_string("modules/comment-box.html", f=f)

class Disqus(BaseUIModule):
    def render(self, url):
        return self.render_string("modules/disqus.html", url=url)
           
class FansOf(BaseUIModule):
    @cache.cache('fans_of', expire=10)
    def render(self, user):
        fans = []
        return self.render_string("modules/fans-of.html", user=user, fans=fans)

class Fans(BaseUIModule):
    def render(self, user):
        fans = []
        return self.render_string("modules/fans.html", user=user, fans=fans)

class Flash(BaseUIModule):
    def render(self):
        message = self.handler.get_secure_cookie("f")
        if message:
            self.handler.clear_cookie("f")
            return self.render_string("modules/flash.html", message=message) 
        else:
            return ''

class Formfield(BaseUIModule):
    def render(self, i):
        import forms
        is_checkbox = isinstance(i, forms.Checkbox)
        return self.render_string('modules/field.html', i=i, is_checkbox=is_checkbox)

class FormfieldInColumns(BaseUIModule):
    def render(self, *inputs):
        return self.render_string('modules/field-incolumns.html', inputs=inputs)
                                      
class HtmlComponent(BaseUIModule):
    ''' Render html widget '''
    def select(self, **kwargs):
        pass

    def search(self, **kwargs):
        pass

    def render(self, elem, **kwargs):
        return ""

class ItemSummary(BaseUIModule):
    def render(self, item, template='modules/item.html'):
        return self.render_string(template, item=item)
    
class Locale(BaseUIModule):
    def render(self):
        from tornado.locale import LOCALE_NAMES
        supported_locales = set(tornado.locale.get_supported_locales(self.handler.locale))
        
        locales = dict([(l,LOCALE_NAMES[l]['name'].lower()) for l in supported_locales])
        locales.pop(self.handler.locale.code)
        return self.render_string("modules/locale.html", \
            locales=locales)

class Map(BaseUIModule):
    def render(self, location):
        locale = ('id', 'ID')
        return self.render_string("modules/map.html", locale=locale)
           
class Poll(BaseUIModule):
    def render(self):
        return self.render_string("modules/poll.html")

class Profile(BaseUIModule):
    def render(self):
        return self.render_string("modules/profile.html")
    
class ReportBox(BaseUIModule):
    def render(self, uri):
        return self.render_string("modules/report-box.html")
    
class Static(BaseUIModule):
    def render(self, template):
        path = os.path.join(self.handler.application.settings['template_path'], \
            "modules", "statics", template + ".html")
        if os.path.exists(path):
            return self.render_string("modules/statics/%s.html" % template)
        return ''

class Slideshow(BaseUIModule):
    def render(self):
        return self.render_string("modules/slideshow.html")

class Streams(BaseUIModule):
    def render(self, user=None):
        return self.render_string("modules/streams.html")
    
class ProfileStreams(BaseUIModule):
    def render(self, user=None):
        return self.render_string("modules/profile-streams.html")

class Tabs(BaseUIModule):
    def get_tabs(self, name):
        import tabs
        return getattr(tabs, name, [None,None])
    
    def render(self, tabs, selected=0, **kwargs):
        heading, tabs = self.get_tabs(tabs)
        if tabs:
            html = self.render_string("modules/tabs.html", heading=heading, tabs=tabs, selected=selected)
            if kwargs:
                html = html % kwargs
            return html
        else:
            return ''
    
class Tags(BaseUIModule):
    def render(self, tags):
        if not tags or not isinstance(tags, list):
            return ''
        return self.render_string("modules/tags.html", tags=tags)

class TagContent(BaseUIModule):
    def render(self, slug, type='article'):
        action = '/%s/tag/%s' % (type, slug)
        return self.render_string("modules/tag-content.html", action=action)
        
class User(BaseUIModule):
    def embedded_css(self):
        return ".entry { margin-bottom: 1em; }"

    def render(self):
        from models import User
        users = User.all().sort([('popularity', 1)]).limit(5)
        return self.render_string("modules/user.html", users=users)
    
class UserBlock(BaseUIModule):
    def render(self, user):
        return self.render_string("modules/user-block.html", user=user)
    
    