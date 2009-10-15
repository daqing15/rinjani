
stream = {
    'username': unicode,
    'type': unicode,
    'visibility': IS(u'pub', u'pri'),
    'message': unicode,
    'created_at': datetime.datetime
}        


user = {
    'username': unicode,
    'facebook_uid': unicode,
    'status': IS(u'active', u'disabled', u'deleted'), 
    'type': IS(u'agent', u'sponsor', u'public'), 
    'is_admin': bool,
    'about': unicode,
    'extended_info': {
        'profile_content': unicode, 
        'contacts': list, 
        'is_verified': bool, 
        'scan_image': unicode
    }, #
    'address': unicode,
    'location': list,
    'website': unicode,
    'bank_accounts': [ {'label': unicode, 'bank': unicode, 'number': unicode}],
    'followed_users': list,
    'followedby_users': list,
    'preferences': list,
    'badges': list,
    'tags': list,
    'hashed_password': unicode,
    'hashed_salt': unicode,
    'reputation': int,
    'up_votes': int,
    'down_votes': int,
    'comment_count': int, # comment created, not comment on this user
    'last_login': datetime.datetime,
    'created_at': datetime.datetime,
}

article = {
    'author': User,
    'status': IS(u'published', u'draft'), 
    'title': unicode,
    'slug': unicode, 
    'excerpt': unicode,
    'content': unicode,
    'comment_count': int,
    'created_at': datetime.datetime,
    'updated_at': datetime.datetime
}

structure = {
    'author': User,
    'status': IS(u'published', u'draft'), 
    'title': unicode,
    'slug': unicode,
    'excerpt': unicode,
    'content': unicode,
    'delivery': unicode,
    'location': {'lat': float, 'lang': float},
    'state': IS(u'planning', u'running', u'completed', u'cancelled', u'unknown'),
    'tags': list,
    'checked_by': list,
    'links': list,
    'need_volunteer': bool,
    'need_donation': bool,
    'donation_amount_needed': int,
    'donation_amount': float,
    'comment_count': int,
    'created_at': datetime.datetime
}
comment = {
   'user': User,
   'parent_type': IS(u'art', u'act', u'usr'), 
   'parent_id': ObjectId, 
   'text': unicode, 
   'html': unicode,
   'created_at': datetime.datetime,
   'updated_at': datetime.datetime
}

volunteer = {
    'user': User,
    'activity': Activity,
    'status': IS(u'approved', u'pending', u'rejected'),
    'asked_at': datetime.datetime,
    'status_updated_at': datetime.datetime 
} 

bank_account = {
    'user': User,
    'identifier': unicode,
    'bank': unicode,
    'number': unicode,
    'holder': unicode,
    'created_at': datetime.datetime
}  

donation =  {
    'from': BankAccount,
    'to': BankAccount,
    'transfer_no': unicode,
    'transferred_at': datetime.datetime,
    'amount': float,
    'activity': Activity, # optional
    'is_validated': bool,
    'created_at': datetime.datetime
}  
