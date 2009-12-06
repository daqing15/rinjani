import os.path

BLOG_TITLE = "Peduli"

PIC_SIZES = [((50,50), True, 's'), ((110,90), True, 'm'), ((550, 700), False, '')]
IMAGE_CONTENT_TYPES = ['image/jpeg', 'image/png', 'image/gif']
ALLOWED_CONTENT_TYPES = IMAGE_CONTENT_TYPES +  \
        ['application/msword', 'application/msexcel', 'application/pdf']

BANKS = [('bca', 'BCA'), ('mandiri','Bank Mandiri'), ('muamalat', 'Bank Muamalat')]
USERTYPE = [(u'public', 'Individu/Public'), (u'agent','Representative of NGO/Social Organization'), (u'sponsor', 'Representative of Corporate/Donor Entity')]

CONTENT_TAGS = ['disaster', 'media', 'CSR', 'news', ]
USER_TAGS = ['IT', 'PR', 'CSR', 'Finance']
FIELD_TAGS = ['education', 'media', 'blah']
MY_FLAGS = [(1,'penting'), (2,'menarik'), (3,'membosankan'), (4,'gak relevan')]

TIMEZONES = [('Asia/Jakarta', 'WIB - Jakarta'), ('Asia/Makassar', 'WITA - Makassar'), ('Asia/Jayapura', 'WIT - Maluku/Irian Jaya')]

TWITTER_USER = ''
TWITTER_PASSWORD = ''
TWITTER_CONSUMER_KEY = ''
TWITTER_CONSUMER_SECRET = ''
FACEBOOK_API_KEY = ''
FACEBOOK_SECRET = ''
DISQUS_USER = ''
DISQUS_USER_API = ''
GOOGLE_ANALYTIC_CODE = ''
YAHOO_API_KEY = ''
YAHOO_SECRET = ''
YAHOO_APPLICATION_ID = ''
PLURK_API_KEY = ''
PLURK_USERNAME = ''
PLURK_PASSWORD = ''

DEBUG_IP = ['127.0.0.1']
LIVE = False
LIVE_URL = 'http://obscurite.ind.ws'
TIMEZONE = "Asia/Jakarta"
XSRF_COOKIES = True
DB = ('localhost', 27017, 'peduli')
BASE_PATH = os.path.dirname(__file__)
BASE_URL = ''

# required by tornado
debug = True
cookie_secret = "x8oETzKXQAGxYdkL5gcmGeJJFuYh7EQnp2XdTP1o/Vo="
template_path = os.path.join(BASE_PATH, "templates")
upload_path = os.path.join(BASE_PATH, "static", "uploads")
static_url = "http://static.obscurite.ind.ws" if  LIVE else 'http://peduli.dev'
static_path = os.path.join(BASE_PATH, "static")
upload_url = "/static/uploads"
avatar = 'avatar.png'
login_url = "/login"
facebook_api_key = FACEBOOK_API_KEY
facebook_secret = FACEBOOK_SECRET
twitter_consumer_key = TWITTER_CONSUMER_KEY
twitter_consumer_secret = TWITTER_CONSUMER_SECRET


