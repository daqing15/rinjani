import os
import random
import re
import tornado.web
import pymongo
from pymongo.dbref import DBRef
import urllib2
        
import forms
from rinjani.utils import calculate_cloud
from rinjani.pagination import Pagination
from models import Article, Project, User, Content, \
    TagCombination, UserTagCombination, Vote, Tag, UserTag, CONTENT_TYPE
from settings import MY_FLAGS

class BaseUIModule(tornado.web.UIModule):
    def render_string(self, path, **kwargs):
        kwargs.update(self.handler.template_vars)
        return self.handler.render_string(path, **kwargs)

class ProjectLatest(BaseUIModule):
    def render(self, **kwargs):
        projects = Project.all({'type':CONTENT_TYPE.PROJECT, \
                                  'status':'published'})\
                                  .sort([('created_at', -1)]).limit(5)
        if projects:
            return self.render_string('modules/project-latest', projects=projects)
        else: return ''

class ContentLatest(BaseUIModule):
    def render(self, type='article', **kwargs):
        spec = {'status':'published'}
        type = getattr(CONTENT_TYPE, type.upper(), CONTENT_TYPE.ARTICLE)
        spec.update({'type': type})
        limit = kwargs.pop('limit', 3)
        items = Content.all(spec).sort([('created_at', -1)]).limit(limit)
        if items:
            return self.render_string('modules/content-latest', items=items)
        else: return ''

class ArticlesRelated(BaseUIModule):
    def render(self, tags):
        return self.render_string('modules/articles-related', articles={})

class Avatar(BaseUIModule):
    def render(self, user):
        return self.render_string('modules/avatar', user=user)

class ByAuthor(BaseUIModule):
    def render(self, author):
        uref = DBRef(User.collection_name, author['_id'])
        spec = {'author': uref, 'status': 'published'}
        pagination = Pagination(self.handler, Content, spec,\
                                per_page = 5)
        return self.render_string('modules/by-author', pagination=pagination)
    
class CommentBox(BaseUIModule):
    def render(self, user=None):
        from forms import comment_form
        f = comment_form()
        return self.render_string('modules/comment-box', f=f)

class Draft(BaseUIModule):
    def render(self, user):
        drafts = Pagination(self.handler, Content, 
                    {'author': DBRef(User.collection_name, user._id), 
                     'status':'draft'})
        return self.render_string('modules/item-list-plain', title="Drafts", items=drafts)
    
class Disqus(BaseUIModule):
    def render(self, item):
        if False and not item.enable_comment:
            return ""
        return self.render_string('modules/disqus', id=id)

class FansOf(BaseUIModule):
    def render(self, user):
        fans = []
        return self.render_string('modules/fans-of', user=user, fans=fans)

class Facets(BaseUIModule):
    def render(self, facets):
        return self.render_string('modules/facets', facets=facets)
    
class Fans(BaseUIModule):
    def render(self, user):
        fans = []
        return self.render_string('modules/fans', user=user, fans=fans)

class Flash(BaseUIModule):
    def render(self):
        message = self.handler.get_cookie('f')
        if message:
            message = urllib2.unquote(message)
            self.handler.clear_cookie('f')
            return self.render_string('modules/flash', message=message)
        else:
            return ''
class FollowButton(BaseUIModule):
    def render(self, user):
        return self.render_string('modules/follow-button', user=user)
    
class Formfield(BaseUIModule):
    def render(self, i, label=None):
        return self.render_string('modules/field', i=i,
                                  is_checkbox=forms.is_checkbox,
                                  is_required=forms.is_required,
                                  label=label
                                  )

class FormfieldInColumns(BaseUIModule):
    def render(self, *inputs):
        return self.render_string('modules/field-incolumns',
                                  inputs=inputs, is_required=forms.is_required)

class GoogleAnalytic(BaseUIModule):
    def render(self):
        code = self.handler.settings.GOOGLE_ANALYTIC_CODE
        return self.render_string('modules/google-analytic', code=code, legacy=False)

class ItemAction(BaseUIModule):
    def render(self, item):
        return self.render_string('modules/item-action', item=item)

class ItemStat(BaseUIModule):
    def render(self, item):
        return self.render_string('modules/item-stat',
                                  item=item,
                                  )

class ItemSummary(BaseUIModule):
    def render(self, item, template='modules/item'):
        return self.render_string(template, item=item)

class ItemComment(BaseUIModule):
    def render(self, item):
        return self.render_string('modules/item-comment', item=item)

class Locale(BaseUIModule):
    def render(self):
        from tornado.locale import LOCALE_NAMES
        supported_locales = set(tornado.locale.get_supported_locales(self.handler.locale))

        locales = dict([(l,re.sub("\(.*\)","", LOCALE_NAMES[l]['name'].lower())) for l in supported_locales])
        locales.pop(self.handler.locale.code)
        return self.render_string('modules/locale', \
            locales=locales)

class Logintips(BaseUIModule):
    def render(self):
        users = User.all({'status':'active'}).sort('created_at', -1).limit(5)
        return self.render_string('modules/login-tips', users=users)
    
class Map(BaseUIModule):
    def render(self, location):
        locale = ('id', 'ID')
        return self.render_string('modules/map', locale=locale)

class Menu(BaseUIModule):
    cp = None
    def check(self, paths):
        for path in paths:
            if re.match(r"^%s" % path, self.cp):
                return 'current'
        return ''

    def render(self):
        self.cp = self.request.path.strip('/')
        return self.render_string('modules/menu', check=self.check)

class Poll(BaseUIModule):
    def render(self):
        return self.render_string('modules/poll')

class Profile(BaseUIModule):
    def render(self):
        return self.render_string('modules/profile')

class Rating(BaseUIModule):
    def render(self, o):
        return self.render_string('modules/rating')

class ReportBox(BaseUIModule):
    def render(self, uri):
        return self.render_string('modules/report-box')

class Static(BaseUIModule):
    def render(self, template, **kwargs):
        path = os.path.join(self.handler.settings['template_path'], \
            'statics', template.lower() + '.html')
        if os.path.exists(path):
            return self.render_string('statics/%s' % template.lower(), **kwargs)
        return ''

class SimilarContent(BaseUIModule):
    def render(self, content):
        # hmm.. kena yg tags >= yg lagi ditampilin aja
        spec = {'_id': {'$ne':content._id}, 'tags': {'$all':content.tags}}
        pagination = Pagination(self.handler, Content, spec, 5)
        return self.render_string('modules/content-similar', pagination=pagination)
                                  
class Slideshow(BaseUIModule):
    def render(self):
        return self.render_string('modules/slideshow')

class Splash(BaseUIModule):
    def render(self):
        spec = {'type':CONTENT_TYPE.PROJECT, 'status':'published', 'attachments': {'$ne':[]}}
        items = Project.all(spec)\
            .sort('created_at', pymongo.DESCENDING).limit(3)
        return self.render_string('modules/splash', items=items)

class Streams(BaseUIModule):
    def render(self, user=None):
        return self.render_string('modules/streams')

class PhotoThumbnails(BaseUIModule):
    def render(self, photos):
        if not photos: return ''
        return self.render_string('modules/item-photo-thumbnails', photos=photos)

class ProfileStreams(BaseUIModule):
    def render(self, user=None):
        return self.render_string('modules/profile-streams')

class Tabs(BaseUIModule):
    def get_tabs(self, name):
        import tabs
        return getattr(tabs, name, [None,None])

    def render(self, user, tabs, selected=0, title=None, dashboard=False, **kwargs):
        _title, tabs = self.get_tabs(tabs)
        if tabs:
            title = title if title else _title
            html = self.render_string('modules/tabs',
                                      user=user,
                                      title=title,
                                      tabs=tabs,
                                      selected=selected,
                                      dashboard=dashboard
                                      )
            if kwargs:
                html = html % kwargs
            return html
        else:
            return ''

class TagCloud(BaseUIModule):
    def render(self, type='user', limit=15):
        cls = UserTag if type=='user' else Tag 
        tags = cls.all().sort('value', -1).limit(limit)
        tags = [tag for tag in tags]
        tags = calculate_cloud(tags, 10, 2)
        random.shuffle(tags)
        return self.render_string('modules/tag-cloud', tags=tags[0:10], min=min)

class Tags(BaseUIModule):
    def render(self, tags):
        return self.render_string('modules/tags', tags=tags)

class TagSuggestion(BaseUIModule):
    def render(self, tags, el=None):
        #tm = tags.pop('mandatory',None)
        #tags = {'Mandatory':tm} if tm else {}
        return self.render_string('modules/tags-suggestion', tags=tags, el=el)

class RelatedTags(BaseUIModule):
    def render(self, _tags, type):
        doc = TagCombination if type == 'content' else UserTagCombination
        size = len(_tags) + 1
        tags = doc.all(
                    {'value.tags': {'$size': size, '$all': _tags}}
                ).sort('value.count',-1)
        if tags.count():
            return self.render_string('modules/related-tags', tags=tags, _tags=_tags,type=type)
        return ''
    
class TagContent(BaseUIModule):
    def render(self, slug, type='content'):
        action = '/%s/tagged/%s' % (type, slug)
        return self.render_string('modules/tag-content', action=action)

class UserFeatured(BaseUIModule):
    def render(self, **kwargs):
        users = User.all({'type':{"$in":['agent','sponsor']}, 
                          'status':'active', 'featured': True}).limit(5)
        return self.render_string('modules/user-featured', users=users)
    
class UserMostActive(BaseUIModule):
    def get_user_most_active(self):
        users = self.handler.cache.get("users.most.active")
        if not users:
            users = User.get_most_active()
            _users = [u for u in users]
            self.handler.cache.set("users.most.active", [u.to_json() for u in users], 1800)
            return _users
        
        import simplejson
        return [simplejson.loads(u) for u in users]
    
    def render(self):
        users = self.get_user_most_active()
        return self.render_string('modules/user-mostactive', users=users)
    
class UserBlock(BaseUIModule):
    def render(self, user):
        return self.render_string('modules/user-block', user=user)

class UserItems(BaseUIModule):
    def render(self, user):
        return self.render_string('modules/user-items', user=user)

class UsersThumbs(BaseUIModule):
    def render(self, users, title='', style=''):
        if isinstance(users, list):
            users = User.all({'username': {"$in": users}})
        return self.render_string('modules/users-thumbs',
                                  users=users,
                                  title=title,
                                  style=style)
