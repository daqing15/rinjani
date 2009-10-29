import logging
from datetime import datetime
import markdown2
from tornado.escape import url_escape 

def attrs_to_str(attrs):
    if not isinstance(attrs, dict):
        return ''
    
    attrs = ["%s='%s'" % (k.lstrip('_'),v) for k, v in attrs.iteritems()]
    return ' '.join(attrs)

def pretty_date(time=False):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    
    http://evaisse.com/post/93417709/python-pretty-date-function
    """
    now = datetime.now()
    if type(time) is int:
        diff = now - datetime.fromtimestamp(time)
    elif type(time) is str:
        diff = now - datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
    elif time is False:
        diff = now - now
    else:
        diff = now - time
        
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(second_diff) + " seconds ago"
        if second_diff < 120:
            return  "a minute ago"
        if second_diff < 3600:
            return str( second_diff / 60 ) + " minutes ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str( second_diff / 3600 ) + " hours ago"
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(day_diff) + " days ago"
    if day_diff < 31:
        return str(day_diff/7) + " weeks ago"
    if day_diff < 365:
        return str(day_diff/30) + " months ago"
    return str(day_diff/365) + " years ago"

def _utc_to_local(dt, tz="Asia/Jakarta"):
    import pytz
    local = pytz.timezone(tz)
    if type(dt) is str:
        dt = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
    return dt.replace(tzinfo=local)

class HtmlHelper:
    @classmethod
    def markdown(cls, s):
        return markdown2.markdown(s)
    
    @classmethod
    def pretty_date(cls, time):
        return pretty_date(time)
    
    @classmethod
    def utc_to_local(cls, dt):
        return dt.replace(tzinfo=None)
    
    @classmethod
    def getarr(cls, arr, idx, default=None):
        try:
            return arr[idx]
        except: pass
        return default
    
    @classmethod
    def link_to(cls, to, label=None, **attrs):
        attrs = attrs_to_str(attrs)
        if not label:
            label = to
        return "<a href='%s' %s>%s</a>" % (to, attrs, label)
    
    @classmethod
    def link_if_auth(cls, user, to, label, usertype_needed='all', **attrs):
        if user:
            if (isinstance(usertype_needed, list) and usertype_needed.count(user['type'])) \
                or user['type'] == usertype_needed \
                or usertype_needed == 'all' \
                or user['is_admin']:
                return cls.link_to(to, label, **attrs)
        return ''
    
    @classmethod
    def link_if_editor(cls, user, author, to, label, **attrs):
        if user and (user['is_admin'] or user == author):
            return cls.link_to(to, label, **attrs)
        return ''
    
    @classmethod
    def link_button_if_editor(cls, user, author, to, label, token):
        attrs = {
                    '_class':'button', 
                    'onclick': 'if (confirm("Are you sure?")) { var f = $("<form method=post ><input type=hidden name=_xsrf value=%s /></form>").get(0); this.parentNode.appendChild(f); f.action = this.href;f.submit(); };return false;' % token
                }
        return cls.link_if_editor(user, author, to, label, **attrs)
    
    @classmethod
    def select(cls, name, args, *validators, **attrs):
        from forms import Dropdown
        dropdown = Dropdown(name, args, *validators, **attrs)
        return dropdown.render()
    

    