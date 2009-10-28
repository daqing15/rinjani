import os.path

app_settings = dict(
    base_path = '',
    port = 9999,
    mobile = False,
    timezone = "Asia/Jakarta",
    
    db_host = 'localhost',
    db_port = 27017,
    db_name = 'peduli',
    
    disqus_user = 'peduli',
    disqus_user_api = 's75p7T8lNJuE0JMiW1E40yPHTxbuP66lqPtyCConY7lwA2G8bEyitiH5AnZtHdwk',
    
    cache_opts = {
         'cache.type': 'memory',
    },
    
    debug = True,
    live = False,
    static_path = os.path.join(os.path.dirname(__file__), "static"),
    blog_title = u"Peduli",
    template_path = os.path.join(os.path.dirname(__file__), "templates"),
    xsrf_cookies = True,
    facebook_api_key = '',
    facebook_secret = '',
    cookie_secret = "Z9oETzKXQAGxYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
    login_url = "/login"
)


