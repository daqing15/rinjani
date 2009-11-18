import os.path

BASEPATH = os.path.dirname(__file__)
PIC_SIZES = [((50,50), True, 's'), ((110,90), True, 'm'), ((550, 700), False, '')]
IMAGE_CONTENT_TYPES = ['image/jpeg', 'image/png', 'image/gif']
ALLOWED_CONTENT_TYPES = IMAGE_CONTENT_TYPES +  \
        ['application/msword', 'application/msexcel', 'application/pdf']

BANKS = [('bca', 'BCA'), ('mandiri','Bank Mandiri'), ('muamalat', 'Bank Muamalat')]
USERTYPE = [('public', 'Individu/Public'), ('agent','Representative of NGO/Social Organization'), ('sponsor', 'Representative of Corporate/Donor Entity')]

CONTENT_TAGS = ['disaster', 'media', 'CSR', 'news', ]
USER_TAGS = ['IT', 'PR', 'CSR', 'Finance']
FIELD_TAGS = ['education', 'media', 'blah']
MY_FLAGS = [(1,'penting'), (2,'menarik'), (3,'membosankan'), (4,'gak relevan')]

TIMEZONE = [('Asia/Jakarta', 'WIB - Jakarta'), ('Asia/Makassar', 'WITA - Makassar'), ('Asia/Jayapura', 'WIT - Maluku/Irian Jaya')]

app_settings = dict(
    debug_ip = ['127.0.0.1'],
    debug = True,
    live = False,

    blog_title = u"Peduli",
    port = 9999,
    mobile = False,
    timezone = "Asia/Jakarta",
    xsrf_cookies = True,

    facebook_api_key = '',
    facebook_secret = '',
    cookie_secret = "23oETzKXQAGxYdkL5gEmGeJJFuYh7EQnp2XdTP1o/xo=",
    disqus_user = '',
    disqus_user_api = '',
    
    db_host = 'localhost',
    db_port = 27017,
    db_name = 'peduli',
    
    context = '',
    base_path = BASEPATH,
    template_path = os.path.join(BASEPATH, "templates"),
    upload_path = os.path.join(BASEPATH, "static", "uploads"),
    static_url = "http://static.peduli.dev",
    static_path = os.path.join(BASEPATH, "static"),
    upload_url = "/static/uploads",
    avatar = 'avatar.png',
    login_url = "/login-form"
)


