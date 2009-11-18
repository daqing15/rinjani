dashboard_agent = ('Dashboard', [
    ('/dashboard', 'dashboard'),
    ('/profile/donations', 'donations'),
    ('/profile/comments', 'comments')
])

new_public = ('New', [
    ('/article/new', 'article')
])

new_agent = new_sponsor = ('New', [
    ('/article/new', 'article'),
    ('/activity/new', 'activity'),    
])

new_admin = ('New', [
    ('/article/new', 'article'),
    ('/activity/new', 'activity'),    
    ('/page/new', 'page'),
])

dashboard_public = ('Dashboard', [
    ('/dashboard', 'messages'),
    ('/profile/comments', 'comments'),
    ('/profile/supports', 'supports'),
])

profile_public = ('%(fullname)s', [
    ('/profile/%(username)s', 'about'),
    ('/profile/articles/%(username)s', 'articles'),
    ('/profile/activities/%(username)s', 'activities'),
    ('/profile/comments/%(username)s', 'comments'),
])

articles = ('Articles', [
    ('/articles?tab=latest', 'latest'),
    ('/articles?tab=featured', 'featured'),
    ('/articles?tab=popular', 'popular'),
])

activities = ('Activities', [
    ('/activities?tab=latest', 'latest'),
    ('/activities?tab=featured', 'featured'),
    ('/activities?tab=popular', 'popular'),
])

users = ('Users', [
    ('/users?tab=social+org', 'social org'),
    ('/users?tab=sponsor', 'sponsor'),
    ('/users?tab=public', 'public'),
])


tags = ('Tags', [
    ('/tags?tab=article', 'article'),
    ('/tags?tab=activity', 'activity'),
    ('/tags?tab=user', 'user')
])