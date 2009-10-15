import os.path

base_path = '' # no trailing slash
port = 9999

db_host = 'localhost'
db_port = 27017
db_name = 'peduli'

url_handlers = [
    (r"/", 'handlers.home.HomeHandler'),
    (r"/l/(\w+)", 'handlers.main.LocaleHandler'),
    (r"/profile/edit", 'handlers.profile.EditHandler'),
    (r"/profile/(\w+)", 'handlers.profile.ViewHandler'),
    (r"/register", 'handlers.profile.RegisterHandler'),
    (r"/dashboard", 'handlers.profile.Dashboard'),
    
    (r"/activities", 'handlers.activity.ListHandler'),
    (r"/activity/new", 'handlers.activity.EditHandler'),
    (r"/activity/edit", 'handlers.activity.EditHandler'),
    (r"/activity/edit/([a-z0-9\-]+)", 'handlers.activity.EditHandler'),
    (r"/activity/([a-z0-9\-]+)", 'handlers.activity.ViewHandler'),
    
    (r"/articles", 'handlers.article.ListHandler'),
    (r"/article/new", 'handlers.article.EditHandler'),
    (r"/article/edit", 'handlers.article.EditHandler'),
    (r"/article/edit/([a-z0-9\-]+)", 'handlers.article.EditHandler'),
    (r"/article/([a-z0-9\-]+)", 'handlers.article.ViewHandler'),
    
    (r"/page/new", 'handlers.page.EditHandler'),
    (r"/page/edit", 'handlers.page.EditHandler'),
    (r"/page/edit/([a-z0-9\-]+)", 'handlers.page.EditHandler'),
    (r"/page/([a-z0-9\-]+)", 'handlers.page.ViewHandler'),
    
    (r"/users", 'handlers.profile.UserListHandler'),
    (r"/tags", 'handlers.tag.ListHandler'),
    (r"/report", 'handlers.report.Handler'),
    (r"/login", 'handlers.auth.LoginHandler'),
    (r"/logout.*", 'handlers.auth.LogoutHandler'),
]

cache_opts = {
     'cache.type': 'memory',
 }

app_settings = dict(
    debug = True,
    static_path = os.path.join(os.path.dirname(__file__), "static"),
    blog_title = u"Peduli",
    template_path = os.path.join(os.path.dirname(__file__), "templates"),
    xsrf_cookies = True,
    cookie_secret = "11oETzKXQAGxYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
    login_url = "/login"
)


