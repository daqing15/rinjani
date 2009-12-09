
from utils.string import dummy_translate as _

dashboard_agent = (_('Dashboard'), [
    ('/dashboard', 'dashboard'),
    ('/profile/donations', _('donations')),
    ('/profile/donations', _('module2')),
    ('/profile/donations', _('module3')),
])

new_public = ('New', [
    ('/article/new', _('article'))
])

new_agent = new_sponsor = ('New', [
    ('/article/new', _('article')),
    ('/activity/new', _('activity')),    
])

new_admin = (_('New'), [
    ('/article/new', _('article')),
    ('/activity/new', _('activity')),    
    ('/page/new', _('page')),
])

dashboard_public = (_('Dashboard'), [
    ('/dashboard', _('messages')),
    ('/profile/comments', _('comments')),
    ('/profile/supports', _('supports')),
])

profile_public = ('%(fullname)s', [
    ('/profile/%(username)s', _('about')),
    ('/profile/articles/%(username)s', _('articles')),
    ('/profile/activities/%(username)s', _('activities')),
    ('/profile/comments/%(username)s', _('comments')),
])

articles = ('Articles', [
    ('/articles/latest', _('latest')),
    ('/articles/featured', _('featured')),
    ('/articles/popular', _('popular')),
])

activities = ('Activities', [
    ('/activities/latest', _('latest')),
    ('/activities/featured', _('featured')),
    ('/activities/popular', _('popular')),
])

users = ('Users', [
    ('/users?tab=social+org', _('social org')),
    ('/users?tab=sponsor', _('sponsor')),
    ('/users?tab=public', _('public')),
])


tags = ('Tags', [
    ('/tags/content', _('content')),
    ('/tags/user', _('user'))
])