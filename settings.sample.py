import os.path

base_path = '' # no trailing slash
port = 9999
mobile = False

db_host = 'localhost'
db_port = 27017
db_name = 'peduli'

disqus_user = ''
disqus_user_api = ''

cache_opts = {
     'cache.type': 'memory',
 }

app_settings = dict(
    debug = True,
    live = False,
    static_path = os.path.join(os.path.dirname(__file__), "static"),
    blog_title = u"Peduli",
    template_path = os.path.join(os.path.dirname(__file__), "templates"),
    xsrf_cookies = True,
    facebook_api_key = '',
    facebook_secret = '',
    cookie_secret = "44oETzKXQAGxYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
    login_url = "/login"
)


