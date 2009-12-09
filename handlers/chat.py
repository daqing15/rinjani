#!/usr/bin/env python
#
# Copyright 2009 Facebook
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
import redis
import time

from main import BaseHandler
from models import User

class MessageMixin(object):
    conn = redis.Redis()
    local_cursor = 0
    waiters = []
    cache = []
    cache_size = 100

    def get_avatars(self, messages=None):
        messages = messages if messages else MessageMixin.cache
        users = User.collection.find({'username':{'$in': [m['from'] for m in messages] }})
        avatars = dict([(u['username'],u['avatar']) for u in users])
        return avatars

    def wait_for_messages(self, callback, cursor=None):
        cls = MessageMixin
        if cursor:
            index = int(cls.local_cursor) - int(cursor)
            if index:
                recent = cls.cache[-index:]
                callback(recent)
                return
        cls.waiters.append(callback)

    def new_messages(self, messages, saved=False):
        cls = MessageMixin
        self.log("Sending new message to %r listeners", len(cls.waiters))
        for callback in cls.waiters:
            try:
                callback(messages)
            except:
                self.log("Error in waiter callback", exc_info=True)
        cls.waiters = []
        if not saved:
            cls.conn.push('chat:messages',messages)
        if cls.conn.llen('chat:messages') > self.cache_size:
            cls.conn.ltrim('chat:messages',-self.cache_size,-1)
        cls.local_cursor = cls.conn.get('chat:cursor')
        cls.cache = cls.conn.lrange('chat:messages',0,-1)

class MainHandler(BaseHandler, MessageMixin):
    @tornado.web.authenticated
    def get(self, channel=None):
        #conn = redis.Redis()
        channel = channel if channel else 'SITE'
        self.render("chat", messages=MessageMixin.cache, avatars=self.get_avatars())

class MessageNewHandler(BaseHandler, MessageMixin):
    @tornado.web.authenticated
    def post(self):
        MessageMixin.local_cursor = this_cursor = MessageMixin.conn.incr('chat:cursor')
        message = {
            "id": str(this_cursor),
            "from": self.current_user["username"],
            "body": self.get_argument("body"),
            "ts": time.time()
        }
        avatars = self.get_avatars([message])
        message["html"] = self.render_string("chat-message", message=message, avatars=avatars)
        if self.get_argument("next", None):
            self.redirect(self.get_argument("next"))
        else:
            self.write(message)
        self.new_messages([message])


class MessageUpdatesHandler(BaseHandler, MessageMixin):
    @tornado.web.authenticated
    @tornado.web.asynchronous
    def post(self):
        cursor = self.get_argument("cursor", None)
        self.wait_for_messages(self.async_callback(self.on_new_messages),
                               cursor=cursor)

    def on_new_messages(self, messages):
        # Closed client connection
        if self.request.connection.stream.closed():
            return
        self.finish(dict(messages=messages))

class QueryRedis(BaseHandler, MessageMixin):
    def __init__(self):
        cls = MessageMixin
        redis_cursor = cls.conn.get('chat:cursor')
        difference = int(redis_cursor) - int(cls.local_cursor)
        if difference:
            redis_msgs = cls.conn.lrange('chat:messages',-difference,-1)
            self.new_messages(redis_msgs, True)


