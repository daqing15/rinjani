import os
import time
import tornado.web
from pymongo.connection import Connection
from beakercache import cache

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
        return self.render_string("modules/map.html")
           
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

class Tags(BaseUIModule):
    def render(self, tags):
        if not tags or not isinstance(tags, list):
            return ''
        return self.render_string("modules/tags.html", tags=tags)
    
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
    

    