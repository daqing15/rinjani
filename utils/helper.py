import logging
import re
from datetime import datetime
import markdown2
import hashlib

def attrs_to_str(attrs):
    if not isinstance(attrs, dict):
        return ''
    
    attrs = ["%s='%s'" % (k.lstrip('_'),v) for k, v in attrs.iteritems()]
    return ' '.join(attrs)

def timesince(time=False, now=False):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    
    http://evaisse.com/post/93417709/python-pretty-date-function
    """
    if not now:
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

def timeuntil(dt, now=None):
    """
    Returns a string measuring the time until the given time.
    """
    now = datetime.datetime.now()
    return timesince(now, dt)

def unique_filename(parts):
    uf = "-".join(parts)
    return hashlib.sha1(uf).hexdigest()

def save_user_upload(dir, filename, file_content):
    import os.path
    path =  os.path.join(dir, filename)
    with open(path, mode="wb") as f:
        f.write(file_content)
        logging.warning("done writing %s" % path)
        return True
    return False
        
class DefaultHelper:
    """
    Functions to help creating/altering template's output
    """
    
    def __init__(self, req):
        self.req = req
        
    #### misc
    alt = {}
    def alternate(self, items):
        k = id(items)
        if not self.alt.has_key(k):
            self.alt[k] = 0
        self.alt[k]  = 0 if self.alt[k] >= len(items) - 1 else self.alt[k] + 1
        return items[self.alt[k]]
    
    def get(self, val, default):
        return val if val else default
    
    def avatar(self, user):
        return self.get(user.avatar, self.req.settings['default_avatar'])
    
                             
    #### string helpers
    def markdown(self, s):
        return markdown2.markdown(s)
    
    # django.template.defaultfilters
    def capfirst(self, value):
        """Capitalizes the first character of the value."""
        return value and value[0].upper() + value[1:]
    
    # django.template.defaultfilters
    def truncate_words(self, s, num):
        "Truncates a string after a certain number of words."
        length = int(num)
        words = s.split()
        if len(words) > length:
            words = words[:length]
            if not words[-1].endswith('...'):
                words.append('...')
        return u' '.join(words)
    
    # django.template.defaultfilters
    def truncate_html_words(self, s, num):
        """
        Truncates html to a certain number of words (not counting tags and
        comments). Closes opened tags if they were correctly closed in the given
        html.
        """
        length = int(num)
        if length <= 0:
            return u''
        html4_singlets = ('br', 'col', 'link', 'base', 'img', 'param', 'area', 'hr', 'input')
        # Set up regular expressions
        re_words = re.compile(r'&.*?;|<.*?>|(\w[\w-]*)', re.U)
        re_tag = re.compile(r'<(/)?([^ ]+?)(?: (/)| .*?)?>')
        # Count non-HTML words and keep note of open tags
        pos = 0
        ellipsis_pos = 0
        words = 0
        open_tags = []
        while words <= length:
            m = re_words.search(s, pos)
            if not m:
                # Checked through whole string
                break
            pos = m.end(0)
            if m.group(1):
                # It's an actual non-HTML word
                words += 1
                if words == length:
                    ellipsis_pos = pos
                continue
            # Check for tag
            tag = re_tag.match(m.group(0))
            if not tag or ellipsis_pos:
                # Don't worry about non tags or tags after our truncate point
                continue
            closing_tag, tagname, self_closing = tag.groups()
            tagname = tagname.lower()  # Element names are always case-insensitive
            if self_closing or tagname in html4_singlets:
                pass
            elif closing_tag:
                # Check for match in open tags list
                try:
                    i = open_tags.index(tagname)
                except ValueError:
                    pass
                else:
                    # SGML: An end tag closes, back to the matching start tag, all unclosed intervening start tags with omitted end tags
                    open_tags = open_tags[i+1:]
            else:
                # Add it to the start of the open tags list
                open_tags.insert(0, tagname)
        if words <= length:
            # Don't try to close tags if we don't need to truncate
            return s
        out = s[:ellipsis_pos] + ' ...'
        # Close any tags still open
        for tag in open_tags:
            out += '</%s>' % tag
        # Return string
        return out
    
    ### date helpers
    def timesince(self, time):
        return timesince(time)
    
    # django.template.defaultfilters
    def timeuntil(self, value, arg=None):
        """Formats a date as the time until that date (i.e. "4 days, 6 hours")."""
        if not value:
            return u''
        try:
            return timeuntil(value, arg)
        except (ValueError, TypeError):
            return u''
    
    def title(self, value):
        """Converts a string into titlecase."""
        return re.sub("([a-z])'([A-Z])", lambda m: m.group(0).lower(), value.title())

    def utc_to_local(self, dt):
        return dt.replace(tzinfo=None)
    
    def getarr(self, arr, idx, default=None):
        try:
            return arr[idx]
        except: pass
        return default
    
    ### html tag helpers
    def link_to(self, to, label=None, **attrs):
        attrs = attrs_to_str(attrs)
        if not label:
            label = to
        return "<a href='%s' %s>%s</a>" % (to, attrs, label)
    
    def link_if_auth(self, user, to, label, usertype_needed='all', **attrs):
        if user:
            if (isinstance(usertype_needed, list) and usertype_needed.count(user['type'])) \
                or user['type'] == usertype_needed \
                or usertype_needed == 'all' \
                or user['is_admin']:
                return self.link_to(to, label, **attrs)
        return ''
    
    def link_if_editor(self, user, author, to, label, **attrs):
        if user and (user['is_admin'] or user == author):
            return self.link_to(to, label, **attrs)
        return ''
    
    def link_button_if_editor(self, user, author, to, label, token):
        attrs = {
                    '_class':'button', 
                    'onclick': 'if (confirm("Are you sure?")) { var f = $("<form method=post ><input type=hidden name=_xsrf value=%s /></form>").get(0); this.parentNode.appendChild(f); f.action = this.href;f.submit(); };return false;' % token
                }
        return self.link_if_editor(user, author, to, label, **attrs)
    
    def select(self, name, args, *validators, **attrs):
        from forms import Dropdown
        dropdown = Dropdown(name, args, *validators, **attrs)
        return dropdown.render()
    

    