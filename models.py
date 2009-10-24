from mongokit import *
from mongokit.mongo_exceptions import *
from pymongo.objectid import ObjectId
import datetime
import settings
import markdown2
import web
import logging
from utils.string import force_unicode

class EditDisallowedError(Exception): pass

class BaseDocument(MongoDocument):
    db_host = settings.db_host
    db_port = settings.db_port
    db_name = settings.db_name
    #skip_validation = True
    use_dot_notation = True
    use_autorefs = True
    structure = {}
    
    def authored_by(self, user):
        return self['author'] is user
    
    def populate(self, doc):
        if not isinstance(doc, dict):
            raise SchemaTypeError()
        
        doc_in_struct = set(doc).intersection(set(self.structure))
        for field in doc_in_struct:
            self[field] = force_unicode(web.net.websafe(doc[field]))
    
    def fill_slug_field(self, s):
        from utils.string import slugify
        s = slugify(s)
        _s = s
        i = 2
        while True:
            if not self.__class__.one({"slug": s}):
                break
            s = "%s-%d" % (_s, i)
            i += 1
        self['slug'] = unicode(s)
    
    def set_slugs(self, s):
        if tags:
            tags = [tag.strip() for tag in s.split(',')]
            self['tags'] = tags
    
    def save(self, uuid=True, validate=None, safe=True, *args, **kwargs):
        super(BaseDocument, self).save(uuid, validate, safe, *args, **kwargs)
    
    def check_edit_permission(self, user):
        if user['_id'] == self['author']['_id'] or user['is_admin']:
            return True
        raise EditDisallowedError()
    
class Stream(BaseDocument):
    collection_name = 'streams'
    structure = {
        'username': unicode,
        'type': unicode,
        'visibility': IS(u'pub', u'pri'),
        'message': unicode,
        'created_at': datetime.datetime
    }        
    
class User(BaseDocument):
    collection_name = 'users'
    structure = {
        # account info
        'username': unicode,
        'password_hashed': unicode,
        'uid': unicode,
        'avatar': unicode,
        'fb_session_key': unicode,
        'auth_provider': IS(u'facebook', u'google', u'form'),
        'status': IS(u'active', u'disabled', u'deleted'), 
        'type': IS(u'agent', u'sponsor', u'public'), 
        'is_admin': bool,
        'is_verified': bool,
        'last_login': datetime.datetime,
        'created_at': datetime.datetime,
        
        # information
        'sex': unicode,
        'last_name': unicode,
        'first_name': unicode,
        'birthday_date': datetime.datetime,
        'timezone': unicode,
        'location': list,
        'website': unicode,
        'proxied_email': unicode,
        
        'about': unicode,
        'profile_content': unicode, 
        'profile_content_html': unicode,
        'phones': list,
        'contact_person': unicode,
        'document_scan': unicode,
        'address': unicode,
        'bank_accounts': [ {'label': unicode, 'bank': unicode, 'number': unicode, 'name': unicode}],
        'tags': list,
        
        # site-related
        'followed_users': list,
        'followedby_users': list,
        'preferences': list,
        'badges': list,
        'reputation': int,
        'up_votes': int,
        'down_votes': int
    }
    required_fields = ['username']
    default_values = {
        'status': u'active',
        'is_admin': False,
        'created_at':datetime.datetime.utcnow, 
        'type': u'public'
    }
    
    indexes = [ { 'fields': 'username', 'unique': True} ]
    
class Article(BaseDocument):
    collection_name = 'articles'
    structure = {
        'author': User,
        'status': IS(u'published', u'draft'), 
        'title': unicode,
        'slug': unicode, 
        'excerpt': unicode,
        'content': unicode,
        'content_html': unicode,
        'enable_comment': bool,
        'comment_count': int,
        'tags': list,
        'created_at': datetime.datetime,
        'updated_at': datetime.datetime
    }
    required_fields = ['author', 'title', 'content']
    default_values = {'enable_comment': True, 'comment_count': 0, 'status': u'published', 'created_at':datetime.datetime.utcnow}
    indexes = [ { 'fields': 'slug', 'unique': True}, { 'fields': 'created_at'} ]
    
    def save(self, data, user):
        self.populate(data)
        
        if '_id' in self:
            self['author'] = User.one({'username':self['author']['username']})
            self.check_edit_permission(user)
        else:
            self['author'] = user
            self.fill_slug_field(self['title'])
        tags = data.get('tags', None)
        if tags:
            tags = list(set([tag.strip() for tag in tags.split(',') if tag]))
            self['tags'] = tags
        self['content_html'] = markdown2.markdown(data['content'])
        super(Article, self).save(True, True)
        
    def get_url(self):
        return "/article/" + self['slug']

class ArticleVote(BaseDocument):
    pass    

class Activity(BaseDocument):
    collection_name = 'activities'
    structure = {
        'author': User,
        'status': IS(u'published', u'draft'), 
        'title': unicode,
        'slug': unicode,
        'excerpt': unicode,
        'date_start': datetime.datetime,
        'date_end': datetime.datetime, 
        'content': unicode,
        'content_html': unicode,
        'deliverable': unicode,
        'deliverable_html': unicode,
        'location': {'lat': float, 'lang': float},
        'state': IS(u'planning', u'running', u'completed', u'cancelled', u'unknown'),
        'tags': list,
        'checked_by': list,
        'links': list,
        'need_volunteer': unicode,
        'need_donation': unicode,
        'donation_amount_needed': int,
        'donation_amount': float,
        'enable_comment': unicode,
        'comment_count': int,
        'created_at': datetime.datetime
    }
    required_fields = ['author', 'status', 'title', 'content']
    default_values = {'enable_comment': u"1", 'comment_count': 0, 'status': u'published', 'created_at':datetime.datetime.utcnow}
    indexes = [ { 'fields': 'slug', 'unique': True}, { 'fields': 'created_at'} ]
    
    def get_url(self):
        return "/activity/" + self['slug']
    
    def save(self, data, user):
        self.populate(data)
        #logging.error(data)
        if not data.has_key('need_donation'):
            self['need_donation'] = None
        if not data.has_key('need_volunteer'):
            self['need_volunteer'] = None
            
        if '_id' in self:
            self['author'] = User.one({'username':self['author']['username']})
            self.check_edit_permission(user)
        else:
            self['author'] = user
            self.fill_slug_field(self['title'])
        
        tags = data.get('tags', None)
        if tags:
            tags = list(set([tag.strip() for tag in tags.split(',') if tag]))
            self['tags'] = tags
        
        if data.get('date_start', None):
            self['date_start'] = datetime.datetime.strptime(data['date_start'], '%d/%m/%Y')
        
        if data.get('date_end', None):
            self['date_end'] = datetime.datetime.strptime(data['date_end'], '%d/%m/%Y')
            
        self['content_html'] = markdown2.markdown(data['content'])
        super(Activity, self).save(True, True)

class Comment(BaseDocument):
    collection_name = 'comments'
    structure = {
       'author': User,
       'parent_type': IS(u'art', u'act', u'usr'), 
       'parent_id': ObjectId, 
       'text': unicode, 
       'html': unicode,
       'created_at': datetime.datetime,
       'updated_at': datetime.datetime
    }
    required_fields = ['author', 'text']
    default_values = {'created_at':datetime.datetime.utcnow}
    
class Volunteer(BaseDocument):
    collection_name = 'volunteers'
    structure = {
        'user': User,
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
        'user': User,
        'identifier': unicode,
        'bank': unicode,
        'number': unicode,
        'holder': unicode,
        'created_at': datetime.datetime
    }  
    required_fields = ['user', 'identifier', 'bank', 'number', 'holder']
    default_values = {'created_at':datetime.datetime.utcnow}
    
class Donation(BaseDocument):
    collection_name = 'donations'
    structure =  {
        'from': BankAccount,
        'to': BankAccount,
        'transfer_no': unicode,
        'transferred_at': datetime.datetime,
        'amount': float,
        'activity': Activity, # optional
        'is_validated': bool,
        'created_at': datetime.datetime
    }  
    required_fields = ['from', 'to', 'transfer_no', 'amount']
    default_values = {'is_validated': False, 'created_at':datetime.datetime.utcnow}
    validators = { "amount": lambda x: x > 0}

class Page(BaseDocument):
    collection_name = 'pages'
    structure = {
        'author': User,
        'title': unicode,
        'slug': unicode,
        'content': unicode,
        'content_html': unicode,
        'created_at': datetime.datetime,
        'updated_at': datetime.datetime
    }
    required_fields = ['title', 'content']
    default_values = {'created_at':datetime.datetime.utcnow}
    
    def get_url(self):
        return "/page/" + self['slug']


"""
u = User()
u.populate(dict(password=u'apit', username=u'apit', is_admin=True, about=u'si admin'))
u.validate()
u.save()

u = User()
u.populate(dict(password=u'act', username=u'act', is_admin=False, type=u'agent', about=u'aksi cepat tanggap DD'))
u.validate()
u.save()

u = User()
u.populate(dict(password=u'sampoerna', username=u'sampoerna', is_admin=False, type=u'sponsor', about=u'sampoerna foundation'))
u.validate()
u.save()

a = Article()
a.populate(dict(author=u, title=u'artikel pertama', slug=u'artikel-pertama', content=u'ini isinya'))
a.validate()
a.save()
"""
           