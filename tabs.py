dashboard_agent = ('Dashboard', [
    ('/dashboard', 'dashboard'),
    ('/profile/donations', 'donations'),
    ('/profile/comments', 'comments'),
    ('/profile/supporters', 'supporters'),
    ('/profile/supports', 'supports'),
])

dashboard_public = ('Dashboard', [
    ('/dashboard', 'messages'),
    ('/profile/comments', 'comments'),
    ('/profile/supports', 'supports'),
])

profile_public = ('Profile of %(fullname)s', [
    ('/profile/%(username)s', 'profile'),
    ('/profile/comments/%(username)s', 'comments'),
    ('/profile/articles/%(username)s', 'articles'),
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