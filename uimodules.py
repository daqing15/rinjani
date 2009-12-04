import os
import tornado.web
import pymongo

from models import Article, Activity, User, Vote, Tag
from settings import MY_FLAGS

class BaseUIModule(tornado.web.UIModule):
    def render_string(self, path, **kwargs):
        kwargs.update(self.handler.template_vars)
        return self.handler.render_string(path, **kwargs)

class ActivityLatest(BaseUIModule):
    def render(self, **kwargs):
        activities = Activity.all({'status':'published'}).sort([('created_at', -1)]).limit(5)
        if activities:
            return self.render_string('modules/activities-latest', activities=activities)
        else: return ''

class ActivitySupporters(BaseUIModule):
    def render(self, activity):
        supporters = self.handler.get_current_user()
        if supporters:
            return self.render_string('modules/activity-supporters', supporters=supporters)
        else: return ''

class AgentFeatured(BaseUIModule):
    def render(self, **kwargs):
        agents = []
        return self.render_string('modules/agents-featured', agents=agents)

class ArticleLatest(BaseUIModule):
    def render(self, **kwargs):
        articles = Article.all({'status':'published'}).sort([('created_at', -1)]).limit(3)
        if articles:
            return self.render_string('modules/articles-latest', articles=articles)
        else: return ''

class ArticlesRelated(BaseUIModule):
    def render(self, tags):
        return self.render_string('modules/articles-related', articles={})

class Avatar(BaseUIModule):
    def render(self, user):
        return self.render_string('modules/avatar', user=user)

class CommentBox(BaseUIModule):
    def render(self, user=None):
        from forms import comment_form
        f = comment_form()
        return self.render_string('modules/comment-box', f=f)

class Disqus(BaseUIModule):
    def render(self, id):
        return self.render_string('modules/disqus', id=id)

class FansOf(BaseUIModule):
    def render(self, user):
        fans = []
        return self.render_string('modules/fans-of', user=user, fans=fans)

class Fans(BaseUIModule):
    def render(self, user):
        fans = []
        return self.render_string('modules/fans', user=user, fans=fans)

class Flash(BaseUIModule):
    def render(self):
        message = self.handler.get_secure_cookie('f')
        if message:
            self.handler.clear_cookie('f')
            return self.render_string('modules/flash', message=message)
        else:
            return ''

def is_required(input):
    for v in input.validators:
        if getattr(v, 'test', None):
            if v.test is bool:
                return True
    return False

class Formfield(BaseUIModule):
    def render(self, i):
        import forms
        is_checkbox = isinstance(i, forms.Checkbox)
        return self.render_string('modules/field', i=i,
                                  is_checkbox=is_checkbox,
                                  is_required=is_required)

class FormfieldInColumns(BaseUIModule):
    def render(self, *inputs):
        return self.render_string('modules/field-incolumns',
                                  inputs=inputs, is_required=is_required)

class GoogleAnalytic(BaseUIModule):
    def render(self):
        code = self.handler.settings.GOOGLE_ANALYTIC_CODE
        return self.render_string('modules/google-analytic', code=code, legacy=False)

class ItemAction(BaseUIModule):
    def render(self, item):
        return self.render_string('modules/item-action', item=item)

class ItemStat(BaseUIModule):
    def render(self, item):
        votes = {}
        for f in MY_FLAGS:
            votes[str(f[0])] = 0
        votes.update(item.votes or {})
        FLAGS = {}
        for f in MY_FLAGS:
            FLAGS[str(f[0])] = f[1]

        if self.handler.current_user:
            vote = Vote.one({'uid':self.handler.current_user['_id'], 'cid': item._id})
        else:
            vote = False
        return self.render_string('modules/item-stat',
                                  item=item,
                                  vote=vote,
                                  votes=votes,
                                  FLAGS=FLAGS
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

        locales = dict([(l,LOCALE_NAMES[l]['name'].lower()) for l in supported_locales])
        locales.pop(self.handler.locale.code)
        return self.render_string('modules/locale', \
            locales=locales)

class Map(BaseUIModule):
    def render(self, location):
        locale = ('id', 'ID')
        return self.render_string('modules/map', locale=locale)

class Menu(BaseUIModule):
    def check(self, paths):
        if self.cp in paths:
            return 'current'
        return ''

    def render(self):
        self.cp = self.request.path.strip('/').split('/')[0]
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
    def render(self, template):
        path = os.path.join(self.handler.application.settings['template_path'], \
            'modules', 'statics', template.lower() + '.html')
        if os.path.exists(path):
            return self.render_string('modules/statics/%s' % template)
        return ''

class Slideshow(BaseUIModule):
    def render(self):
        return self.render_string('modules/slideshow')

class Splash(BaseUIModule):
    def render(self):
        items = Activity.all({'status':'published', 'attachments': {'$ne':[]}})\
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

    def render(self, tabs, selected=0, title=None, dashboard=False, **kwargs):
        _title, tabs = self.get_tabs(tabs)
        if tabs:
            title = title if title else _title
            html = self.render_string('modules/tabs',
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
    def render(self, **kwargs):
        from utils.utils import calculate_cloud
        import random
        tags = Tag.all().sort('value', -1).limit(15)
        tags = [tag for tag in tags]
        tags = calculate_cloud(tags, 10, 2)
        random.shuffle(tags)
        return self.render_string('modules/tag-cloud', tags=tags[0:10], min=min)

class Tags(BaseUIModule):
    def render(self, tags):
        return self.render_string('modules/tags', tags=tags)

class TagSuggestion(BaseUIModule):
    def render(self, tags, el=None):
        return self.render_string('modules/tags-suggestion', tags=tags, el=el)

class TagContent(BaseUIModule):
    def render(self, slug, type='article'):
        action = '/%s/tag/%s' % (type, slug)
        return self.render_string('modules/tag-content', action=action)

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
