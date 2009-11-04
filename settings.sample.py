import os.path
BASEPATH = os.path.dirname(__file__)
                       
app_settings = dict(
    debug_ip = ['127.0.0.1'],
    debug = True,
    live = False,

    blog_title = u"Peduli",
    port = 9999,
    mobile = False,
    timezone = "Asia/Jakarta",
    xsrf_cookies = True,

    facebook_api_key = 'x',
    facebook_secret = 'x',
    cookie_secret = "22oETzKXQAGxYdkL5gEmGeJJFuYh7EQnp2XdTP1o/xo=",
    disqus_user = 'peduli',
    disqus_user_api = 'x',
    
    db_host = 'localhost',
    db_port = 27017,
    db_name = 'peduli',
    cache_opts = {
         'cache.type': 'memory',
    },
    
    context = '',
    base_path = BASEPATH,
    template_path = os.path.join(BASEPATH, "templates"),
    static_path = os.path.join(BASEPATH, "static"),
    upload_path = os.path.join(BASEPATH, "static", "uploads"),
    static_url = "/static",
    upload_url = "/static/uploads",
    avatar = 'avatar3.jpg',
    login_url = "/login-form"
)


