import os.path

SITE_TITLE = "Peduli"

PIC_SIZES = [((50,50), True, 's'), ((110,90), True, 'm'), ((550, 700), False, '')]
IMAGE_CONTENT_TYPES = ['image/jpeg', 'image/png', 'image/gif']
ALLOWED_CONTENT_TYPES = IMAGE_CONTENT_TYPES +  \
        ['application/msword', 'application/msexcel', 'application/pdf']

BANKS = [('bca', 'BCA'), ('mandiri','Bank Mandiri'), ('muamalat', 'Bank Muamalat')]
USERTYPE = [(u'public', 'Individual'), 
            (u'agent','Social/Nonprofit Organization'), 
            (u'sponsor', 'Corporate/Donor Entity')
            ]

ACTIVITY_STAGES = [(u'planning', 'Planning'), (u'running', 'Running'), 
                   (u'accomplished', 'Finished. Goal Accomplished.'), 
                   (u'cancelled', 'Canceled')
                   ]

CONTENT_TAGS = {
    'mandatory': ['arts', 'business', 'culture', 'design', 'environment', 'education', 
                  'health', 'philantrophic', 'poverty', 'social', 'sports', 'technology' ],
    'facet2': ['important', 'sensitive', 'ideas'],
}
USER_TAGS = {
    'mandatory': ['education', 'finance', 'nonprofits', 'media', 'pns', 'technology', 'trade'],
    'facet2': ['blah2a', 'blah2b', 'cat3b', 'cat3c'],
}

FIELD_TAGS = {
    '_': ['public advocacy', 'health', 'education', ],
}

MY_FLAGS = [(1,'penting'), (2,'menarik'), (3,'membosankan'), (4,'gak relevan')]

TIMEZONES = [('Asia/Jakarta', 'WIB - Jakarta'), ('Asia/Makassar', 'WITA - Makassar'), \
             ('Asia/Jayapura', 'WIT - Maluku/Irian Jaya')]
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
CAPTCHA_PUBLIC_KEY = ''
CAPTCHA_PRIVATE_KEY = ''

DEBUG = os.environ.get("USER","") == 'ron'
LIVE = False
BASE_URL = ''
TIMEZONE = "Asia/Jakarta"
DB = ('localhost', 27017, 'peduli')
BASE_DIR = os.path.dirname(__file__)
PARENT_DIR = os.path.dirname(BASE_DIR)
SOLR_URL = 'http://127.0.0.1:8983/solr'

# required by tornado
debug = DEBUG
xsrf_cookies = True,
cookie_secret = "11oETzKXQAGxYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo="
template_path = os.path.join(BASE_DIR, "templates")
upload_path = os.path.join(BASE_DIR, "static", "uploads")
static_url = "http://static.obscurite.ind.ws" if  LIVE else 'http://peduli.dev'
static_path = os.path.join(BASE_DIR, "static")
upload_url = "/static/uploads"
avatar = 'avatar.png'
login_url = "/login"
facebook_api_key = FACEBOOK_API_KEY
facebook_secret = FACEBOOK_SECRET
twitter_consumer_key = TWITTER_CONSUMER_KEY
twitter_consumer_secret = TWITTER_CONSUMER_SECRET



