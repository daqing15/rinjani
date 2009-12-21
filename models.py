import datetime
import logging
import markdown2
import re
import simplejson
import time

import tornado.web
from mongokit import DBRef, MongoDocument, IS, SchemaTypeError
from settings import DB, USERTYPE as _USER_TYPE
from rinjani.string import force_unicode, listify, sanitize, slugify
from rinjani.inline import processor, AttachmentInline, SlideshowInline
from rinjani.json import JSONEncoder

USER_TYPE = dict(_USER_TYPE).keys()

class CONTENT_TYPE:
    GENERIC = 1
    ARTICLE = 2
    ACTIVITY = 3
    PAGE = 4
    POST = 5
    USER = 6
    BLOG = 7

CONTENT_MAP = [None, 'content', 'article', 'activity', 'page', 'post', 'user']

class EditDisallowedError(Exception): pass

class Simpledoc(MongoDocument):
    db_host, db_port, db_name = DB
    use_dot_notation = True
    skip_validation = True
    structure = {}
    
class Queue(Simpledoc):
    collection_name = 'queues'
    structure = {'payload': dict, 'locked': bool}
    default_fields = { 'locked': False}
        
class BaseDocument(Simpledoc):
    use_autorefs = True
    sanitized_fields = []
    
    def check_edit_permission(self, user):
        if user['_id'] == self['author']['_id'] or user['is_admin']:
            return True
        raise EditDisallowedError()

    def formify(self):
        for k, t in self.structure.iteritems():
            if t is list and self[k]:
                self[k] = ', '.join(self[k])
            elif t is datetime.datetime:
                if self.has_key(k) and type(self[k]) is datetime.datetime:
                    self[k] = self[k].strftime('%d/%m/%Y')

            if self.has_key(k) and self[k] is None:
                self[k] = ""

    def populate(self, data):
        if not isinstance(data, dict):
            raise SchemaTypeError()

        for k, t in self.structure.iteritems():
            if k in data:
                if t is unicode:
                    if data[k]:
                        self[k] = force_unicode(data[k])
                        if k in self.sanitized_fields:
                            self[k] = sanitize(self[k])
                elif t is list:
                    self[k] = listify(data[k], ',')
                elif t is datetime.datetime and data[k]:
                    self[k] = datetime.datetime.strptime(data[k], '%d/%m/%Y')
                elif t is bool:
                    if data[k] == 'False':
                        self[k] = False
                    else:
                        self[k] = False if not k in data  else bool(int(data[k]))
                elif t is int:
                    self[k] = int(re.sub('[.,]*', '', data[k]))
                else:
                    self[k] = data[k]
            else:
                if t is bool and not k in data:
                    # self.__generate_skeleton None-ing bool field. change to bool
                    self[k] = False
        self.update_html(data)

    def update_html(self, data=None):
        for k, t in self.structure.iteritems():
            if t is unicode and k.endswith('_html'):
                src = k.replace('_html', '')
                if self[src] and (not data or (data and src in data)):
                    s = self.process_inline(src, self[src])
                    self[k] = markdown2.markdown(s)

    # override this
    def process_inline(self, field, src):
        return src

    def process_inline_attachments(self, src):
        if self.attachments:
            pip = AttachmentInline(self.attachments)
            processor.register('attachment', pip)
            pis = SlideshowInline(self.attachments)
            processor.register('slideshow', pis)
        return processor.process(src)

class User(BaseDocument):
    collection_name = 'users'
    structure = {
        # account info
        'username': unicode,
        'password_hashed': unicode,
        'uid': unicode,
        'avatar': unicode,
        'access_token': unicode, #fb=session_key
        'auth_provider': IS(u'facebook', u'google', u'twitter', u'form'),
        'status': IS(u'active', u'disabled', u'deleted'),
        'type': IS(*USER_TYPE),
        'is_admin': bool,
        'is_verified': bool,
        'last_login': datetime.datetime,
        'created_at': datetime.datetime,
        'updated_at': datetime.datetime,

        # information
        'sex': unicode,
        'fullname': unicode,
        'birthday_date': datetime.datetime,
        'location': list,
        'contact_person': unicode,
        'phones': list,
        'fax': list,
        'address': unicode,
        'email': unicode,
        'website': unicode,
        'document_scan': unicode,
        'timezone': unicode,
        'locale': unicode,

        'tags': list,

        'about': unicode,
        'profile_content': unicode,
        'profile_content_html': unicode,

        'attachments': [{'type':unicode, 'src':unicode, 'thumb_src':unicode, 'filename': unicode}],

        # site-related
        'following': list,
        'followers': list,
        'preferences': {
                        'enable_location': bool,
                        'send_email_on_writing': bool 
                        },
        'badges': list,
        'points': int,
        'article_count': int,
        'activity_count': int,
        'donation_count': int,

    }
    indexed_field = 'profile_content'
    required_fields = ['username']
    sanitized_fields = ['address', 'email', 'website', 'about']
    default_values = {
        'status': u'active',
        'timezone': u'Asia/Jakarta',
        'is_admin': False,
        'article_count': 0, 'activity_count': 0, 'donation_count': 0, 'points': 0,
        'created_at':datetime.datetime.utcnow,
        'type': u'public'
    }

    indexes = [ { 'fields': 'username', 'unique': True} ]

    def save(self, data=None, user=None, safe=True):
        if not data:
            super(User,self).save()
            return
        
        self.populate(data)
        self['updated_at'] = datetime.datetime.utcnow()
        
        if user and data.has_key('bank_accounts'):
            self.update_bank_accounts(user, data['bank_accounts'])
        
        new_doc = '_id' not in self
        super(User, self).save(safe=safe)
        self.post_save(data, new_doc)
    
    def post_save(self, data, new_doc): 
        if self.indexed_field:
            payload = {
                       'id': self['_id'],
                       'title': self['username'],
                       'content': self[self.indexed_field],
                       'path': self.get_url(),
                       'type': CONTENT_TYPE.USER,
                       'tags': self['tags'],
                       'created_at': self['created_at'],
                       'updated_at': self['updated_at']
                       }
        Queue.collection.update({'_id': 'indexing'}, 
                                {'$push': {'payload': payload, 'locked':False}},
                                upsert=True)
        
    def remove(self): 
        payload = {'id': self['_id']}
        Queue.collection.update({'_id': 'indexremoval'},
                                 {'$push': {'payload': payload, 'locked':False}},
                                 upsert=True)
        super(User, self).remove()

    def update_bank_accounts(self, user, accounts):
        _accounts = list(user.get_bank_accounts())
        prev_accounts = [acc['_id'] for acc in _accounts]
        updated_accounts = []

        for acc in accounts:
            try:
                if acc[4] == "0":
                    logging.warning("Adding account %s" % acc[0])
                    BankAccount.add_account(user, acc)
                elif acc[4] in prev_accounts:
                    i = prev_accounts.index(acc[4])
                    #del(prev_accounts[i])
                    updated_accounts.append(acc[4])
                    if self.is_bank_data_dirty(acc, _accounts[i]):
                        logging.warning("%s is dirty. Updating..." % acc[4])
                        BankAccount.update_account(acc)
            except: pass

        removed_accounts = set(prev_accounts).difference(set(updated_accounts))
        for accid in list(removed_accounts):
            logging.warning("Removing %s" % accid)
            BankAccount.remove({'_id': accid})

    def is_bank_data_dirty(self, current, _prev):
        prev = []
        fields = BankAccount.fields[:]
        fields.append('_id')
        for field in fields:
            prev.append(_prev[field])
        return prev != current

    @classmethod
    def filter_valid_accounts(cls, accounts):
        return [account for account in accounts if len(account) > 4]

    def get_bank_accounts(self):
        """
        not using self.related.bank_accounts since spec produced includes
        checking index field ($exists: true) that somehow skewing result
        """
        spec = {'owner': DBRef(self.collection_name, self._id)}
        return BankAccount.collection.find(spec)

    def process_inline(self, field, src):
        if field not in ['profile_content']:
            return src
        return self.process_inline_attachments(src)

    def get_url(self):
        return "/profile/" + self['username']

class Org(User):
    collection_name = 'users'

class Sponsor(User):
    collection_name = 'users'
        
class Volunteer(User):
    collection_name = 'users'
    
class Group(BaseDocument):
    collection_name = 'groups'
    structure = {
        'admin': User,
        'description': unicode,
        'members': list
    }

class Content(BaseDocument):
    collection_name = 'contents'
    structure = {
        'author': User
    }
    type = CONTENT_TYPE.GENERIC
    required_fields = ['author', 'title', 'content']
    sanitized_fields = ['excerpt', 'content']
    indexed_field = 'content'
    inline_fields = ['content']
    
    @property
    def class_doc(self):
        return CONTENT_MAP[int(self['type'])]
    
    def authored_by(self, user):
        return self['author'] is user

    # is this atomic op?
    def set_slug(self, doc, s):
        if s.strip() in ['new', 'edit']:
            raise Exception("Title cant be '%s'" % s.strip())
        s = slugify(s)
        spec = {'type': self.type, 'slug': s}
        if '_id' in doc:
            spec.update({'_id': {'$ne': doc['_id']}})

        _s = s
        i = 1
        while True:
            i += 1
            if not self.__class__.one(spec):
                break
            _s = "%s-%d" % (s, i)
            spec.update({'slug': _s})

        doc['slug'] = _s
        #self.__class__.collection.update({'_id': self._id}, {'$set': {'slug': unicode(s)}})

    def process_inline(self, field, src):
        if field not in self.inline_fields:
            return src

        if self.attachments:
            pip = AttachmentInline(self.attachments)
            processor.register('attachment', pip)
            pis = SlideshowInline(self.attachments)
            processor.register('slideshow', pis)
        return processor.process(src)

    def save(self, data=None, user=None, safe=True):
        if not data:
            super(Content,self).save()
            return

        if 'featured' in data and user['type'] != 'admin':
            del(data['featured'])

        self.populate(data)
        self.updated_at = datetime.datetime.utcnow()

        new_doc = False
        if '_id' in self:
            self.check_edit_permission(user)
        else:
            self['author'] = user
            new_doc = True

        self['type'] = self.__class__.type
        self.pre_save(data, new_doc)
        self.set_slug(self, self['title'])
        super(Content, self).save(safe=safe)
        self.post_save(data, new_doc)

    def remove(self, force=False):
        self.pre_remove()
        if force:
            self.remove()
        else:
            self.status = u'deleted'
            self.save()
        self.post_remove()

    def pre_save(self, data, new_doc): pass
    def post_save(self, data, new_doc): 
        if self.indexed_field:
            payload = {
                       'id': self['_id'],
                       'title': self['title'],
                       'content': self[self.indexed_field],
                       'path': self.get_url(),
                       'type': self['type'],
                       'tags': self['tags'],
                       'created_at': self['created_at'],
                       'updated_at': self['updated_at']
                       }
        Queue.collection.update({'_id': 'indexing'}, 
                                {'$push': {'payload': payload, 'locked':False}},
                                upsert=True)
        
    def pre_remove(self): 
        payload = {'id': self['_id']}
        Queue.collection.update({'_id': 'indexremoval'},
                                 {'$push': {'payload': payload, 'locked':False}},
                                 upsert=True)
        
    def post_remove(self): 
        pass
    
    @property
    def base_url(self):
        return "/" + CONTENT_MAP[int(self['type'])]

    def get_url(self):
        return "%s/%s" % (self.base_url, self.slug)

    def get_edit_url(self):
        return self.base_url + '/edit/' + self.slug

    def get_remove_url(self):
        return self.base_url + '/remove/' + self.slug

class Article(Content):
    type = CONTENT_TYPE.ARTICLE
    structure = {
        'type': int,
        'author': User,
        'status': IS(u'published', u'draft', u'deleted'),
        'featured': bool,
        'title': unicode,
        'slug': unicode,
        'excerpt': unicode,
        'content': unicode,
        'content_html': unicode,
        'enable_comment': bool,
        'comment_count': int,
        'view_count': int,
        'tags': list,
        'votes': dict,
        'attachments': [{'type':unicode, 'src':unicode, 'thumb_src':unicode, 'filename': unicode}],
        'created_at': datetime.datetime,
        'updated_at': datetime.datetime
    }
    api_fields = ['title', 'slug', 'excerpt', 'content', 
                    'view_count', 'tags', 'created_at'] 
    
    default_values = {'enable_comment': True, 'view_count': 0, 'comment_count': 0,
                      'status': u'published',
                      'featured': False,
                      'created_at':datetime.datetime.utcnow,
                      'updated_at':datetime.datetime.utcnow
                      }
    indexes = [ { 'fields': ['type', 'slug'], 'unique': True}]

    def post_save(self, data, new_doc):
        if new_doc:
            User.collection.update({'username': self.author.username}, {'$inc': { 'article_count': 1}})
        super(Article, self).post_save(data, new_doc)

    def post_remove(self):
        User.collection.update({'username': self.author.username}, {'$inc': { 'article_count': -1}})

class Activity(Content):
    type = CONTENT_TYPE.ACTIVITY
    structure = {
        'type': int,
        'author': User,
        'status': IS(u'published', u'draft', u'deleted'),
        'featured': bool,
        'title': unicode,
        'slug': unicode,
        'excerpt': unicode,
        'content': unicode,
        'content_html': unicode,
        'lat': float,
        'lang': float,
        'date_start': datetime.datetime,
        'date_end': datetime.datetime,
        'state': IS(u'planning', u'running', u'completed', u'cancelled', u'unknown'),
        'validated_by': list,
        'need_volunteer': bool,
        'volunteer_tags': list,
        'need_donation': bool,
        'donation_amount_needed': int,
        'donation_amount': float,

        'tags': list,
        'enable_comment': bool,
        'comment_count': int,
        'view_count': int,
        'votes': dict,
        'attachments': [{'type':unicode, 'src':unicode, 'thumb_src':unicode, 'filename': unicode}],
        'created_at': datetime.datetime,
        'updated_at': datetime.datetime
    }
    api_fields = ['title', 'slug', 'excerpt', 'content', 
                    'location', 'date_start', 'date_end', 
                    'view_count', 'tags', 'created_at']
    
    default_values = {'enable_comment': True, 'view_count': 0, 'comment_count': 0,
                      'status': u'published',
                      'state': u'planning',
                      'featured': False,
                      'created_at':datetime.datetime.utcnow,
                      'updated_at':datetime.datetime.utcnow
                      }
    indexes = [ { 'fields': 'slug', 'unique': True}]
    
    def post_save(self, data, new_doc):
        if new_doc:
            User.collection.update({'username': self.author.username}, {'$inc': { 'activity_count': 1}})
        super(Activity, self).post_save(data, new_doc)
        
    def post_remove(self):
        User.collection.update({'username': self.author.username}, {'$inc': { 'activity_count': -1}})

class Page(Content):
    type = CONTENT_TYPE.PAGE
    structure = {
        'author': User,
        'type': int,
        'title': unicode,
        'slug': unicode,
        'status': IS(u'published', u'draft'),
        'content': unicode,
        'content_html': unicode,
        'enable_comment': bool,
        'attachments': [{'type':unicode, 'src':unicode, \
                         'thumb_src':unicode, 'filename': unicode}],
        'created_at': datetime.datetime,
        'updated_at': datetime.datetime
    }
    default_values = {'enable_comment': False,
                      'created_at':datetime.datetime.utcnow
                      }

class Post(Page):
    type = CONTENT_TYPE.POST

class Blog(Page):
    type = CONTENT_TYPE.BLOG
    
class Comment(BaseDocument):
    collection_name = 'comments'
    structure = {
       'from': User,
       'for': User,
       'comment': unicode,
       'replies': [{'from': User, 'comment': unicode, 'created_at': datetime.datetime}],
       'created_at': datetime.datetime,
    }
    sanitized_fields = ['comment', 'replies.comment']
    required_fields = ['from', 'for', 'comment']
    default_values = {'created_at':datetime.datetime.utcnow, \
                      'replies.created_at': datetime.datetime.utcnow}
    
    def save(self, data=None, user=None):
        if not data:
            super(Comment,self).save()
            return
        self.populate(data)
        super(Comment, self).save()

class UserActivity(BaseDocument):
    collection_name = 'points'
    structure = {
        'user': User,
        'type': int,
        'object': IS(Article, Activity, Post, Blog, Comment),
        'points': int,
        'created_at': datetime.datetime
    }
    
    def score(self, user, object, activity):
        User.collection.update({'username': user.username}, \
                               {'$inc': { 'points': 1}})
class Vote(BaseDocument):
    collection_name = 'votes'
    structure = {'uid': unicode, 'cid': unicode, 'vote': int}
        
class Response(BaseDocument):
    collection_name = 'responses'
    structure = {
        'for': Content,
        'responses': [{'from': User, 'resp': unicode, 'created_at': datetime.datetime}],
        'responses_count': int,
        'last_response': datetime.datetime
    }
    
class Volunteer(BaseDocument):
    collection_name = 'volunteers'
    structure = {
        'user': User,
        'approved_by': User,
        'activity': Activity,
        'status': IS(u'approved', u'pending', u'rejected'),
        'asked_at': datetime.datetime,
        'status_updated_at': datetime.datetime
    }
    required_fields = ['user', 'activity']
    default_values = {'status': u'pending', 'asked_at':datetime.datetime.utcnow}

class BankAccount(BaseDocument):
    collection_name = 'bank_accounts'
    structure = {
        'owner': User,
        'label': unicode,
        'bank': unicode,
        'number': unicode,
        'holder': unicode,
        'created_at': datetime.datetime
    }
    required_fields = ['owner', 'label', 'bank', 'number', 'holder']
    fields = ['label', 'bank', 'number', 'holder']
    default_values = {'created_at':datetime.datetime.utcnow}
    indexes = [ { 'fields': ['bank', 'number'], 'unique': True} ]

    @classmethod
    def add_account(cls, user, acc):
        account = cls()
        data = dict([(field, acc[idx]) for idx, field in enumerate(cls.fields)])
        account.populate(data)
        account['owner'] = user
        account.save()

    @classmethod
    def update_account(cls, acc):
        account = cls.one({'_id': acc[4]})
        if account:
            for i, field in enumerate(cls.fields):
                account[field] = unicode(acc[i])
        account.save()

    @classmethod
    def listify(cls, accounts):
        _accounts = list(accounts)
        accounts = []
        for acc in _accounts:
            accounts.append([acc['label'], acc['bank'], acc['number'], acc['holder'], acc['_id']])
        return accounts

User.related_to = {
        'bank_accounts':{'class':BankAccount, 'target':'owner', 'autoref': True},
    }

class Donation(BaseDocument):
    collection_name = 'donations'
    structure =  {
        'from': User,
        'for': User,
        'from_account': BankAccount,
        'for_account': BankAccount,
        'transfer_no': unicode,
        'amount': float,
        'activity': Activity, # optional
        'is_validated': bool,
        'transferred_at': datetime.datetime,
        'created_at': datetime.datetime
    }
    required_fields = ['from', 'to', 'transfer_no', 'amount']
    default_values = {'is_validated': False, 'created_at':datetime.datetime.utcnow}
    validators = { "amount": lambda x: x > 0}

class Stream(BaseDocument):
    collection_name = 'streams'
    structure = {
        'user': User,
        'object': IS(Activity, Article, Comment),
        'created_at': datetime.datetime
    }
    default_values = {'created_at':datetime.datetime.utcnow}


class Tag(Simpledoc):
    collection_name = 'content_tags'
    structure = {
        'value': int
    }
    required_fileds = ['value']

class UserTag(Tag):
    collection_name = 'user_tags'

class Cache(Simpledoc):
    collection_name = 'caches'
    structure = {
        'value': IS(dict, bool, unicode, list),
        'expire': float
    }
    default_values = {'expire': 0.0}

class TagCombination(Simpledoc):
    collection_name = 'content_tag_combinations'
    structure = { 'value': { 'tags': list, 'count': int}}
    
    def get_tags(self):
        return self.value['tags']
    
    def get_count(self):
        return self.value['count']

class UserTagCombination(TagCombination):
    collection_name = 'user_tag_combinations'
        
class Chat(Simpledoc):
    collection_name = 'chats'
    structure = {'channel': unicode, 
                 'cursor': int,
                 'settings': dict,
                 'messages': [{
                            'id': int,
                            'from': User,
                            'date': unicode,
                            'body': unicode,
                            'html': unicode
                            }] 
                 }
    default_values = {'cursor': 0, 'messages': []}
    
def get_or_404(cls, query=None):
    query = query if query else {}
    o = cls.one(query)
    if not o:
        raise tornado.web.HTTPError(404)
    return o

