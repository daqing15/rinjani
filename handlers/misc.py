import urllib
from tornado.auth import TwitterMixin
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
import tornado.web
from placemaker import placemaker
from main import BaseHandler

class SurveyHandler(BaseHandler):
    GFORM_BASEURL = u'http://spreadsheets.google.com/embeddedform?key='
    GFORM_ACTION = u'http://spreadsheets.google.com/formResponse'

    @tornado.web.asynchronous
    def get(self):
        form_id = self.get_argument('f','').strip()
        if not form_id:
            self.finish("")
            return
        # check regex of id, only allow alpha?
        url = self.GFORM_BASEURL + form_id
        self.form_id = form_id
        http = AsyncHTTPClient()
        http.fetch(HTTPRequest(url, 'GET'),
                   callback=self.async_callback(self.on_response))

    @tornado.web.asynchronous
    def post(self):
        data = urllib.urlencode(self.get_utf_arguments())
        url = self.GFORM_ACTION + u'?' + data
        http = AsyncHTTPClient()
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        http.fetch(
                   HTTPRequest(url, 'POST', headers, body=data),
                   callback=self.async_callback(self.on_response),
                   )

    def on_response(self, response):
        if response:
            html = self.clean_up(response.body)
            self.finish(html)

    def clean_up(self, html):
        html_extra = [
            '<link rel="stylesheet" href="/static/css/embed.css" type="text/css" />',
            ''
        ]
        html = html.replace('</head>', ''.join(html_extra) + '</head>')
        html = html.replace(self.GFORM_ACTION, '/survey/')
        return html

    def get_utf_arguments(self):
        args = self.get_arguments()
        args = [(key, value.encode('utf-8')) for key,value in args.iteritems()]
        return dict(args)

class I18nJsHandler(BaseHandler):
    def get(self, locale):
        from tornado.locale import _translations
        import simplejson
        
        loc = self.locale.code
        messages = {} if loc == 'en_US' else _translations[loc]['unknown']
        translation_catalog = {
                               'locale': loc, 
                               'plural_expr': "(n != 1)",
                               'messages': messages
                               }
        
        translation_catalog = simplejson.dumps(translation_catalog)
        self.render("jslocale", translation_catalog=translation_catalog)
        
class GetLocHandler(BaseHandler, TwitterMixin):
    def on_response(self, response):
        #logging.warn(response.body)
        p = placemaker(self.settings.YAHOO_API_KEY)
        
        places = p.process_response(response.body)
        if places:
            c = places[0].centroid
            self.write({'long':c.longitude, 'lat': c.latitude, 'place': c.longitude})
        else:
            self.write({})
        self.finish()
    
    @tornado.web.asynchronous
    def post(self):
        loc = self.get_argument('loc')
        p = placemaker(self.settings.YAHOO_API_KEY)
        url, data = p.format_request("I live in %s " % loc)
        req = HTTPRequest(url, method="POST", body=data)
        
        http = tornado.httpclient.AsyncHTTPClient()
        http.fetch(req, callback=self.async_callback(self.on_response))
        
class TweetsHandler(BaseHandler, TwitterMixin):
    def tweetime_to_datetime(self, t):
        # Sun Dec 06 17:36:25 +0000 2009
        import time, datetime
        d = time.strptime(t, "%a %b %d %H:%M:%S +0000 %Y")
        return datetime.datetime(*d[0:7])

    def tweets_to_streams(self, tweets):
        tweets = tweets[:5]
        return [{
                 'img': t['user']['profile_image_url'],
                 'name': t['user']['screen_name'],
                 'text': t['text'],
                 'time': self.tweetime_to_datetime(t['created_at'])
                 } for t in tweets ]

    def _on_receive(self, tweets):
        if not tweets:
            self.finish("")
            return
        tweets_html = self.render_string('modules/streams', streams=self.tweets_to_streams(tweets))
        self.cache.set("tweets", tweets_html, 1800)
        self.finish(tweets_html)

    @tornado.web.asynchronous
    def get(self):
        tweets = self.cache.get("tweets")
        if tweets:
            self.render("modules/streams", streams=tweets)
            return

        self.twitter_request(
                '/statuses/user_timeline/%s' % self.settings.TWITTER_USER,
                callback=self.async_callback(self._on_receive)
            )
