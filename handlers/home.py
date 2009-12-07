#
# Copyright 2009 rinjani team
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import tornado.web
from tornado.auth import TwitterMixin
from main import BaseHandler
from models import Article
from utils.string import sanitize

class TweetsHandler(BaseHandler, TwitterMixin):
    def tweetime_to_datetime(self, time):
        # Sun Dec 06 17:36:25 +0000 2009
        import time, datetime
        d = time.strptime('Sun Dec 06 17:36:25 +0000 2009', "%a %b %d %H:%M:%S +0000 %Y")
        return datetime.datetime(*d[0:7])

    def tweets_to_streams(self, tweets):
        import logging; logging.warn(tweets)
        tweets = tweets[:5]
        return [{
                 'img': t['user']['profile_image_url'],
                 'name': t['user']['screen_name'],
                 'text': t['text'],
                 'time': self.tweetime_to_datetime(t['created_at'])
                 } for t in tweets ]

    def _on_receive(self, tweets):
        tweets_html = self.render_string('modules/streams', streams=self.tweets_to_streams(tweets))
        self.cache.set("tweets", tweets_html, 1800)
        self.finish(tweets_html)

    @tornado.web.asynchronous
    def get(self):
        tweets = self.cache.get("tweets", True)
        if tweets:
            self.render("modules/streams", streams=tweets)
            return

        self.twitter_request(
                '/statuses/user_timeline/%s' % self.settings.TWITTER_USER,
                self._on_receive
            )

class HomeHandler(BaseHandler):
    def get(self):
        was_here = self.get_cookie('was_here', False)
        tweets = self.cache.get("tweets", True)

        if not was_here:
            self.set_cookie('was_here', '1')
        articles = Article.all({'slug': 'article-pertama'})
        self.render("home", articles=articles, was_here=was_here, tweets=tweets)

