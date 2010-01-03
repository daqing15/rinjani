import datetime
import logging
import markdown2
import re
import simplejson
import time
from uuid import uuid4

import tornado.web
from mongokit import DBRef, MongoDocumentCursor, MongoDocument, IS, SchemaTypeError
from settings import DB, USERTYPE as _USER_TYPE
from rinjani.string import force_unicode, listify, sanitize, slugify
from rinjani.inline import processor, AttachmentInline, SlideshowInline
from rinjani.json import JSONEncoder

USER_TYPE = dict(_USER_TYPE).keys()

# change *-edit.html if you change this :p
class CONTENT_TYPE:
    GENERIC = 1
    ARTICLE = 2
    PROJECT = 3
    PAGE = 4
    POST = 5
    USER = 6
    BLOG = 7

CONTENT_MAP = [None, 'content', 'article', 'project', 'page', 'post', 'user']

class EditDisallowedError(Exception): pass

class Simpledoc(MongoDocument):
    db_host, db_port, db_name = DB
    use_dot_notation = True
    skip_validation = True
    structure = {}
    
class Queue(Simpledoc):
    collection_name = 'queues'
    structure = {'key': unicode, 'payload': dict, 'locked': bool}
    indexes = [ { 'fields': 'key'} ]
    
    @classmethod
    def publish(cls, key, payload):
        message = {'_id': unicode(uuid4()), 
                   'locked':False, 
                   'key': key, 
                   'payload': payload}
        cls.collection.save(message)
        
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
            # from form which all val are unicode
            if k in data and type(data[k]) is unicode and data[k]:
                if t is unicode:
                    self[k] = force_unicode(data[k])
                    if k in self.sanitized_fields:
                        self[k] = sanitize(self[k])
                elif t is list:
                    self[k] = listify(data[k], ',')
                elif t is datetime.datetime:
                    self[k] = datetime.datetime.strptime(data[k], '%d/%m/%Y')
                elif t is bool:
                    if data[k] == 'False':
                        self[k] = False
                    else:
                        self[k] = bool(int(data[k]))
                elif t is int:
                    self[k] = int(re.sub('[.,]*', '', data[k]))
                else:
                    self[k] = data[k]
            #elif self[k]:
            #    if t is int:
            #        self[k] = int(self[k])
            #    elif t is bool:
            #        # self.__generate_skeleton None-ing bool field. change to bool
            #        self[k] = bool(self[k])
            elif k in data:
                self[k] = data[k]
                
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
        'logo': unicode,
        'access_token': unicode, #fb=session_key
        'auth_provider': IS(u'facebook', u'google', u'twitter', u'form'),
        'status': IS(u'active', u'disabled', u'deleted'),
        'reg_status': IS(u'verified', u'await'),
        'type': IS(*USER_TYPE),
        'is_admin': bool,
        'is_verified': bool,
        'featured': bool,  
        'last_login': datetime.datetime,

        # information
        'sex': unicode,
        'fullname': unicode,
        'birthday_date': datetime.datetime,
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
                        'send_email_on_writing': bool,
                        },
        'badges': list,
        'points': int,
        'article_count': int,
        'project_count': int,
        'comment_count': int,
        'donation_count': int,
        'vote_up': int,
        'vote_down': int,
        
        'lat': unicode,
        'lng': unicode,
        'created_at': datetime.datetime,
        'updated_at': datetime.datetime,
    }
    
    indexed_field = 'profile_content'
    required_fields = ['username']
    sanitized_fields = ['address', 'email', 'website', 'about']
    default_values = {
        'status': u'active',
        'timezone': u'Asia/Jakarta',
        'is_admin': False,
        'is_verified': False,
        'featured': False,  
        'article_count': 0, 'project_count': 0, 'donation_count': 0, 'points': 0,
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
                       'type': self['type'],
                       'tags': self['tags'],
                       'created_at': self['created_at'],
                       'updated_at': self['updated_at']
                       }
            
            Queue.publish('index.user', payload)
        
    def remove(self): 
        payload = {'id': self['_id']}
        Queue.publish('remove.user', payload)
        self['status'] = u'deleted'
        self.save()

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
    
    @classmethod
    def get_most_active(self):
        js_update_points = """
function update_points() {
     db.users.find().forEach(function(u) { 
         u.points = 10*u.project_count+5*u.article_count;
         db.users.save(u);})
}
"""
        User.collection.database.eval(js_update_points)
        return User.all({},['username','avatar','fullname','points','article_count','project_count'])\
                .sort("points", -1).limit(5)
                                        
    def process_inline(self, field, src):
        if field not in ['profile_content']:
            return src
        return self.process_inline_attachments(src)

    def get_url(self):
        return "/profile/" + self['username']
    
    def increment_karma(self, kind, amount):
        pass

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

class MultiDocsInCollection(BaseDocument):
    @classmethod
    def one(cls, spec, *args, **kwargs):
        spec.update({'type': cls.type})
        bson_obj = cls.collection.find(spec, *args, **kwargs)
        count = bson_obj.count()
        if count > 1:
            raise MultipleResultsFound("%s results found" % count)
        elif count == 1:
            return cls(bson_obj.next(), collection=cls.collection)
    
    @classmethod
    def all(cls, _spec, *args, **kwargs):
        wrap = kwargs.pop('wrap',True)
        spec = {'type': cls.type}
        spec.update(_spec)
        collection = kwargs.pop('collection', None)
        collection = cls.collection
        return MongoDocumentCursor(
          collection.find(spec, *args, **kwargs), cls=cls, wrap=wrap)
    
    @property
    def class_doc(self):
        return CONTENT_MAP[int(self['type'])]
    
class Content(MultiDocsInCollection):
    collection_name = 'contents'
    structure = {
        'author': User,
        'title': unicode,
        'content': unicode,
        'slug': unicode,
        'tags': list,
    }
    type = CONTENT_TYPE.GENERIC
    required_fields = ['author', 'title', 'content']
    sanitized_fields = ['excerpt', 'content']
    indexed_field = 'content'
    inline_fields = ['content']
    indexes = [ { 'fields': 'slug'} ]
    
    def authored_by(self, user):
        return self['author'] is user

    # is this atomic op?
    def set_slug(self, doc, s):
        if s.strip().lower() in ['new', 'edit', 'remove']:
            raise Exception("Title cant be '%s'" % s.strip())
        s = slugify(s)
        spec = {'type': self['type'], 'slug': s}
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
    
    def increment_view_count(self):
        Content.collection.update({'_id':self['_id']}, {'$inc': { 'view_count': 1}})

    def save(self, data=None, user=None, safe=True):
        if not data:
            super(Content,self).save()
            return

        #if 'featured' in data and user['type'] != 'admin':
        #    del(data['featured'])

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
            super(Content, self).remove()
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
        Queue.publish('index.content', payload)
        
    def pre_remove(self): 
        pass
        
    def post_remove(self): 
        payload = {'id': self['_id']}
        Queue.publish('removal.content', payload)
    
    @property
    def base_url(self):
        return "/" + CONTENT_MAP[int(self['type'])]

    def get_url(self):
        return "%s/%s" % (self.base_url, self.slug)

    def get_edit_url(self):
        return self.base_url + '/edit/' + self.slug

    def get_remove_url(self):
        return self.base_url + '/remove/' + self.slug
    
    def get_commenters(self):
        """ must do this. we have DBRef that need to be resolved"""
        def get_user(comment, commenters):
            if type(comment) is dict:
                commenters.add(comment['user'].id)
                if comment.has_key('responses'):
                    [get_user(c, commenters) for c in comment['responses']]
            elif type(comment) is list:
                [get_user(c, commenters) for c in comment]
        commenters_ids = set()
        get_user(self['comments'], commenters_ids)
        commenters = User.all({"_id": {"$in": list(commenters_ids)}})
        commenters = dict([(c['_id'], c) for c in commenters])
        return commenters

class Article(Content):
    type = CONTENT_TYPE.ARTICLE
    structure = {
        'type': int,
        'author': User,
        'status': IS(u'published', u'draft', u'deleted'),
        'featured': bool,
        'title': unicode,
        'slug': unicode,
        'tags': list,
        'excerpt': unicode,
        'content': unicode,
        'content_html': unicode,
        'enable_comment': bool,
        'comments': [ { 'id': int, 
                       'user': User, 
                       'text': unicode, 
                       'created_at': datetime.datetime,
                       'responses': [{ 'id': int, 'user': User, 'text': unicode,
                                      'created_at': datetime.datetime}]
                       }],
                       
        'attachments': [{'type':unicode, 'src':unicode, 'thumb_src':unicode, 
                         'filename': unicode}],
        
        'view_count': int,
        'vote_up': int,
        'vote_down': int,
        
        'lat': unicode,
        'lng': unicode,
        'created_at': datetime.datetime,
        'updated_at': datetime.datetime
    }
    api_fields = ['title', 'slug', 'excerpt', 'content', 
                    'view_count', 'tags', 'created_at'] 
    
    default_values = {
                      'enable_comment': True,
                      'featured': False, 
                      'view_count': 0, 'vote_up': 0, 'vote_down': 0,
                      'status': u'published',
                      'comments': [],
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

class Comment(Simpledoc):
    collection_name = 'comments'
    structure = {'for': User, 'from': User, 'text': unicode, 'created_at': datetime.datetime}
    
class Project(Content):
    type = CONTENT_TYPE.PROJECT
    structure = {
        'type': int,
        'author': User,
        'status': IS(u'published', u'draft', u'deleted'),
        'featured': bool,
        'title': unicode,
        'slug': unicode,
        'tags': list,
        'enable_comment': bool,
        'comments': [ { 'id': unicode, 
                       'user': User, 
                       'text': unicode, 
                       'created_at': datetime.datetime,
                       'responses': [{ 'id': int, 'user': User, 'text': unicode,
                                      'created_at': datetime.datetime}]
                       }],
        'attachments': [{'type':unicode, 'src':unicode, 'thumb_src':unicode, 
                         'filename': unicode}],
        
        'goal': unicode,
        'content': unicode,
        'content_html': unicode,
        'state': IS(u'planning', u'running', u'completed', u'cancelled', u'unknown'),
        'need_volunteer': bool,
        'volunteer_tags': list,
        'need_donation': bool,
        'donation_amount_needed': int,
        'donation_amount': float,
        'validators': [{'user':User, 'comment':unicode}],
        'volunteers': list,
        'supporters': list,
        'donaters': list,
        'events': [{'date': datetime.datetime, 
                    'description': unicode}
                    ],
        
        'view_count': int,
        'vote_up': int,
        'vote_down': int,
        
        'lat': unicode,
        'lng': unicode,
        'created_at': datetime.datetime,
        'updated_at': datetime.datetime
    }
    required_fields = ['author', 'title', 'content', 'goal']
    api_fields = ['title', 'slug', 'excerpt', 'content', 
                    'view_count', 'tags', 'created_at']
    
    default_values = {
                      'enable_comment': True,
                      'need_donation': False,
                      'need_volunteer': False,
                      'featured': False,  
                      'status': u'published',
                      'state': u'planning',
                      'comments': [],
                      'view_count': 0, 'vote_up': 0, 'vote_down': 0,
                      'donation_amount_needed': 0,
                      'created_at':datetime.datetime.utcnow,
                      'updated_at':datetime.datetime.utcnow
                      }
    indexes = [ { 'fields': 'slug', 'unique': True}]
    
    def post_save(self, data, new_doc):
        if new_doc:
            User.collection.update({'username': self.author.username}, {'$inc': { 'project_count': 1}})
        super(Project, self).post_save(data, new_doc)
        
    def post_remove(self):
        User.collection.update({'username': self.author.username}, {'$inc': { 'project_count': -1}})
        

class Page(Content):
    type = CONTENT_TYPE.PAGE
    structure = {
        'author': User,
        'type': int,
        'title': unicode,
        'slug': unicode,
        'tags': list,
        'status': IS(u'published', u'draft', u'deleted'),
        'content': unicode,
        'content_html': unicode,
        
        'enable_comment': bool,
        'comments': [ { 'id': int, 
                       'user': User, 
                       'text': unicode, 
                       'created_at': datetime.datetime,
                       'responses': [{ 'id': int, 'user': User, 'text': unicode,
                                      'created_at': datetime.datetime}]
                       }],
        'attachments': [{'type':unicode, 'src':unicode, \
                         'thumb_src':unicode, 'filename': unicode}],
        'created_at': datetime.datetime,
        'updated_at': datetime.datetime
    }
    default_values = {
                      'enable_comment': False,
                      'comments': [],
                      'created_at':datetime.datetime.utcnow
                      }

class Post(Page):
    type = CONTENT_TYPE.POST

class Blog(Page):
    type = CONTENT_TYPE.BLOG
    

class Activity(BaseDocument):
    collection_name = 'activities'
    structure = {
        'user': User,
        'type': int,
        'object': IS(Article, Project, Post, Blog),
        'points': int,
        'created_at': datetime.datetime
    }
    
    def score(self, user, object, activity):
        User.collection.update({'username': user.username}, \
                               {'$inc': { 'points': 1}})
        
class Vote(BaseDocument):
    collection_name = 'votes'
    structure = {'uid': unicode, 'cid': unicode, 'vote': int}
        

class Volunteer(BaseDocument):
    collection_name = 'volunteers'
    structure = {
        'user': User,
        'approved_by': User,
        'project': Project,
        'status': IS(u'approved', u'pending', u'rejected'),
        'asked_at': datetime.datetime,
        'status_updated_at': datetime.datetime
    }
    required_fields = ['user', 'project']
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
    indexes = [ { 'fields': ['owner','bank', 'number'], 'unique': True} ]

    @classmethod
    def add_account(cls, user, acc):
        account = cls()
        data = dict([(field, unicode(acc[idx])) for idx, field in enumerate(cls.fields)])
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
        'project': Project, # optional
        'is_validated': bool,
        'transferred_at': datetime.datetime,
        'created_at': datetime.datetime
    }
    required_fields = ['from', 'to', 'transfer_no', 'amount']
    default_values = {'is_validated': False, 'created_at':datetime.datetime.utcnow}
    validators = { "amount": lambda x: x > 0}

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
        return self['value']['tags']
    
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

