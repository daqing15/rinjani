
from rinjani.string import dummy_translate as _

admin = (_('Dashboard'), [
    ('/dashboard', 'dashboard'),
    ('/admin/users', _('users')),
    ('/admin/verifications', _('verifications')),
    ('/admin/reports', _('reports')),
])

profile = ('%(fullname)s', [
    ('/profile/%(username)s', _('wall')),
    ('/profile/%(username)s/about', _('about')),
    ('/profile/%(username)s/donations', _('donations'), {'private':True}),
    ('/profile/%(username)s/articles', _('articles')),
    ('/profile/%(username)s/projects', _('projects')),
])

new_public = ('New', [
    ('/article/new', _('article'))
])

new_agent = new_sponsor = ('New', [
    ('/article/new', _('article')),
    ('/project/new', _('project')),    
])

new_admin = (_('New'), [
    ('/article/new', _('article')),
    ('/project/new', _('project')),    
    ('/page/new', _('page')),
])

articles = ('Articles', [
    ('/articles/latest', _('latest')),
    ('/articles/featured', _('featured')),
    ('/articles/popular', _('popular')),
])

projects = ('Projects', [
    ('/projects/latest', _('latest')),
    ('/projects/featured', _('featured')),
    ('/projects/popular', _('popular')),
])

users = ('Users', [
    ('/users?tab=social+org', _('social org')),
    ('/users?tab=sponsor', _('sponsor')),
    ('/users?tab=public', _('public')),
])

edit_profile = ('Profile', [
    ('/profile/edit', _('profile')),
    ('/preferences', _('preferences')),
])

tags = ('Tags', [
    ('/tags/content', _('content')),
    ('/tags/user', _('user'))
])

