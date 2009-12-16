
import urllib
import re
import tornado.web
from main import BaseHandler
from tornado.auth import TwitterMixin
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from utils.pagination import SearchPagination

class SearchHandler(BaseHandler):
    def get(self):
        from utils.indexing import index
        q = self.get_argument('q', None)
        if q:
            params = {}
            args = self.request.arguments
            params.update({'facet': 'true', 'facet.field': ['type','tags']})
            if 'fq' in args:
                params.update({'fq': args['fq']})
            try:
                pagination = SearchPagination(self, index, q, params)
                self.render("search", pagination=pagination, q=q, error="")
            except:
                raise
                self.render("search", pagination=[], q=q, error="Search facility is down")
        else: 
            self.render("search", pagination=[], q=q, error="Not Found")

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
        http = tornado.httpclient.AsyncHTTPClient()
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
