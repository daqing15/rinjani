import datetime
import logging
import markdown2
from mongokit import DBRef, MongoDocument, IS, ObjectId, SchemaTypeError
from settings import app_settings
from utils.string import force_unicode, listify, sanitize
from utils.time import date_to_striso, striso_to_date

class EditDisallowedError(Exception): pass

class BaseDocument(MongoDocument):
    db_host = app_settings['db_host']
    db_port = app_settings['db_port']
    db_name = app_settings['db_name']
    #skip_validation = True
    use_dot_notation = True
    use_autorefs = True
    structure = {}
    sanitized_fields = []
    
    def authored_by(self, user):
        return self['author'] is user
    
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
    
    def save(self, uuid=True, validate=None, safe=True, *args, **kwargs):
        super(BaseDocument, self).save(uuid, validate, safe, *args, **kwargs)
    
    def check_edit_permission(self, user):
        if user['_id'] == self['author']['_id'] or user['is_admin']:
            return True
        raise EditDisallowedError()
    
    def formify(self):
        for k, t in self.structure.iteritems():
            if t is bool:
                #self[k] = "0" if self[k] is None else str(int(self[k]))
                self[k] = "1"
            elif t is list and self[k]:
                self[k] = ', '.join(self[k])
            elif t is datetime.datetime:
                if self[k] and type(self[k]) is datetime.datetime:
                    self[k] = self[k].strftime('%d/%m/%Y')
            
            if self[k] is None:
                self[k] = ""
    
    def populate(self, data):
        if not isinstance(data, dict):
            raise SchemaTypeError()
        
        #logging.error(data)
        for k, t in self.structure.iteritems():
            if k in data:
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
                        self[k] = False if not k in data  else bool(int(data[k]))
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
        'location': list,
        'proxied_email': unicode,
        'contact_person': unicode,
        'phones': list,
        'fax': list,
        'address': unicode,
        'email': unicode,
        'website': unicode,
        'document_scan': unicode,
        'tags': list,
        
        'about': unicode,
        'profile_content': unicode, 
        'profile_content_html': unicode,
        
        'attachments': [{'type':unicode, 'src':unicode, 'thumb_src':unicode, 'filename': unicode}],
        
        # site-related
        'followed_users': list,
        'followedby_users': list,
        'preferences': list,
        'badges': list,
        'reputation': int,
        'up_votes': int,
        'down_votes': int,
        'article_count': int,
        'activity_count': int,
        'donation_count': int,
        
    }
    required_fields = ['username']
    sanitized_fields = ['address', 'email', 'website', 'about']
    default_values = {
        'status': u'active',
        'is_admin': False,
        'article_count': 0, 'activity_count': 0, 'donation_count': 0,  
        'created_at':datetime.datetime.utcnow, 
        'type': u'public'
    }

    indexes = [ { 'fields': 'username', 'unique': True} ]
    
    def save(self, data=None, user=None):
        if not data:
            super(User,self).save(True, True)
            return
        
        self.populate(data)
        logging.error(data)
        if user and data.has_key('bank_accounts'):
            self.update_bank_accounts(user, data['bank_accounts'])
        super(User, self).save(True, True)
    
    def update_bank_accounts(self, user, accounts):
        _accounts = list(user.related.bank_accounts())
        prev_accounts = [acc['_id'] for acc in _accounts]
        updated_accounts = []
        
        for acc in accounts:
            try:
                if acc[4] == "0":
                    logging.warning("Adding account %s" % acc[0])
                    BankAccount.add_account(user, acc)
                elif acc[4] in prev_accounts:
                    i = prev_accounts.index(acc[4])
                    del(prev_accounts[i])
                    if self.is_bank_data_dirty(acc, _accounts[i]):
                        logging.warning("%s is dirty. Updating..." % acc[4])
                        updated_accounts.append(acc[4])
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
        
        from utils.inline import processor, AttachmentInline
        
        if self.attachments:
            pip = AttachmentInline(self.attachments)
            processor.register('attachment', pip)
        return processor.process(src)
    
    def get_url(self):
        return "/profile/" + self['username']

class Article(BaseDocument):
    collection_name = 'articles'
    structure = {
        'author': User,
        'status': IS(u'published', u'draft', u'deleted'), 
        'title': unicode,
        'slug': unicode, 
        'excerpt': unicode,
        'content': unicode,
        'content_html': unicode,
        'enable_comment': bool,
        'comment_count': int,
        'view_count': int,
        'tags': list,
        'attachments': [{'type':unicode, 'src':unicode, 'thumb_src':unicode, 'filename': unicode}], 
        'created_at': datetime.datetime,
        'updated_at': datetime.datetime
    }
    required_fields = ['author', 'title', 'content']
    sanitized_fields = ['excerpt', 'content']
    default_values = {'enable_comment': True, 'view_count': 0, 'comment_count': 0, 'status': u'published', 'created_at':datetime.datetime.now}
    indexes = [ { 'fields': 'slug', 'unique': True}, { 'fields': 'created_at'} ]
    
    def save(self, data=None, user=None):
        if not data:
            super(Article,self).save(True, True)
            return
        
        self.populate(data)
        
        new = False
        if '_id' in self:
            self.check_edit_permission(user)
        else:
            self['author'] = user
            new = True
            self.fill_slug_field(self['title'])
        
        super(Article, self).save(True, True)
        if new:
            User.collection.update({'username': user.username}, {'$inc': { 'article_count': 1}})
    
    def remove(self):
        self.status = u'deleted'
        self.save()
        User.collection.update({'username': self.author.username}, {'$inc': { 'article_count': -1}})
        
    def process_inline(self, field, src):
        if field not in ['content']:
            return src
        
        from utils.inline import processor, AttachmentInline
        
        if self.attachments:
            pip = AttachmentInline(self.attachments)
            processor.register('attachment', pip)
        return processor.process(src)
    
    def get_url(self):
        return "/article/" + date_to_striso(self.created_at) + "/" + self.slug
    
class ArticleVote(BaseDocument):
    pass    

class Activity(BaseDocument):
    collection_name = 'activities'
    structure = {
        'author': User,
        'status': IS(u'published', u'draft', u'deleted'), 
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
        'attachments': [{'type':unicode, 'src':unicode, 'thumb_src':unicode, 'filename': unicode}],
        'checked_by': list,
        'links': list,
        'enable_comment': bool,
        'need_volunteer': bool,
        'need_donation': bool,
        'donation_amount_needed': int,
        'donation_amount': float,
        'comment_count': int,
        'view_count': int,
        'created_at': datetime.datetime
    }
    required_fields = ['author', 'status', 'title', 'content']
    sanitized_fields = ['excerpt', 'content', 'deliverable']
    default_values = {'view_count': 0, 'comment_count': 0, 'status': u'published', 'created_at':datetime.datetime.now}
    indexes = [ { 'fields': 'slug', 'unique': True}, { 'fields': 'created_at'} ]
    
    def get_url(self):
        return "/activity/" + date_to_striso(self.created_at) + "/" + self.slug
    
    def save(self, data=None, user=None):
        if not data:
            super(Activity,self).save(True, True)
            return
        
        self.populate(data)
        
        new = False
        if '_id' in self:
            self.check_edit_permission(user)
        else:
            self['author'] = user
            new = True
            self.fill_slug_field(self['title'])
        
        super(Activity, self).save(True, True)
        if new:
            User.collection.update({'username': user.username}, {'$inc': { 'activity_count': 1}})
    
    def remove(self):
        self.status = u'deleted'
        self.save()
        User.collection.update({'username': self.author.username}, {'$inc': { 'activity_count': -1}})
    
    def process_inline(self, field, src):
        if field not in ['content']:
            return src
        
        from utils.inline import processor, AttachmentInline
        
        if self.attachments:
            pip = AttachmentInline(self.attachments)
            processor.register('attachment', pip)
        return processor.process(src)


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
    sanitized_fields = ['content']
    default_values = {'created_at':datetime.datetime.utcnow}
    
    def get_url(self):
        return "/page/" + self['slug']



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
        'from_account': list,
        'for_account': list,
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
