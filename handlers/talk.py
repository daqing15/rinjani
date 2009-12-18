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
import time
import logging

from main import BaseHandler
from models import Chat, Activity

class MainHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, ch):
        activity = Activity.one({'slug': ch})
        if not activity:
            raise tornado.web.HTTPError(404)
        channel = Chat.one({'_id': ch})
        messages = channel['messages'] if channel else []
        messages = messages[-MessageMixin.recent_size:]
        self.render("talk", activity=activity, messages=messages, ch=ch)

class MessageMixin(object):
    waiters = {}
    recent_size = 100
    
    @classmethod
    def _waiters(cls, ch, w=None):
        """ get or append ;)"""
        if ch not in cls.waiters:
            cls.waiters[ch] = [w] if w is not None else []
        elif w is not None:
            cls.waiters[ch].append(w)
        return cls.waiters[ch]
    
    def wait_for_messages(self, ch, callback, cursor=None):
        cls = MessageMixin
        if cursor:
            channel = Chat.one({'_id': ch})
            recent = channel['messages'][(int(cursor)-1):]
            if recent:
                callback(recent)
                return
        cls._waiters(ch, callback)

    def new_messages(self, ch, messages, saved=False):
        cls = MessageMixin
        logging.info("Sending new message to %r listeners", \
                     len(cls._waiters(ch)))
        for callback in cls._waiters(ch):
            try:
                callback(messages)
            except:
                logging.error("Error in waiter callback", exc_info=True)
        cls.waiters[ch] = []
        
class NewHandler(BaseHandler, MessageMixin):
    @tornado.web.authenticated
    def post(self, ch):
        spec = {'_id': ch}
        
        insert_func = """
function insertNewMessage(ch, newMsg) {
    c = db.chats.findOne({_id:ch});
    id = c? (c['messages'].length + 1) : 1;
    newMsg['id'] = id; 
    db.chats.update({_id:ch}, {$push: {messages:newMsg}}, true);
    return id;
}        
        """
        message = {
            "from": self.current_user["username"],
            "avatar": self.current_user["avatar"],
            "body": self.get_argument("body"),
            "ts": time.time()
        }
        
        id = Chat.collection.database.eval(insert_func, ch, message)
        message["id"] = id
        self.new_messages(ch, [message])
        self.write(message)

class UpdatesHandler(BaseHandler, MessageMixin):
    @tornado.web.authenticated
    @tornado.web.asynchronous
    def post(self, ch):
        cursor = self.get_argument("cursor", None)
        self.wait_for_messages(ch, self.async_callback(self.on_new_messages),
                               cursor=cursor)

    def on_new_messages(self, messages):
        # Closed client connection
        if self.request.connection.stream.closed():
            return
        self.finish(dict(messages=messages))


