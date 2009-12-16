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

from settings import IMAGE_CONTENT_TYPES
import itertools

_base_js_escapes = (
    ('\\', r'\x5C'),
    ('\'', r'\x27'),
    ('"', r'\x22'),
    ('>', r'\x3E'),
    ('<', r'\x3C'),
    ('&', r'\x26'),
    ('=', r'\x3D'),
    ('-', r'\x2D'),
    (';', r'\x3B'),
    (u'\u2028', r'\u2028'),
    (u'\u2029', r'\u2029')
)

# Escape every ASCII character with a value less than 32.
_js_escapes = (_base_js_escapes +
               tuple([('%c' % z, '\\x%02X' % z) for z in range(32)]))

def attrs_to_str(attrs):
    if not isinstance(attrs, dict):
        return ''
    
    attrs = ["%s='%s'" % (k.lstrip('_'),v) for k, v in attrs.iteritems()]
    return ' '.join(attrs)

def timesince(time=False, now=False):
    from timeutil import timesince
    return timesince(time, now)

def timeuntil(dt):
    from timeutil import timeuntil
    return timeuntil(dt)

def utc_to_local(dt):
    return dt.replace(tzinfo=None)

def time(dt, format=""):
    return dt.strftime("")

def alternate(items):
    return itertools.cycle(items)

def get(val, default):
    return val or default

def groups(seq, size):
    if not hasattr(seq, 'next'):  
            seq = iter(seq)
    while True: 
        yield [seq.next() for _i in range(size)]
        
def group(seq, size): 
    """
    Returns an iterator over a series of lists of length size from iterable.
        >>> list(group([1,2,3,4,5], 2))
        [[1, 2], [3, 4], [5]]
    """
    if not hasattr(seq, 'next'):  
        seq = iter(seq)
    while True: 
        x = []
        for _i in range(size):
            try:
                x.append(seq.next())
            except: pass 
        
        if x:
            yield x
        else:
            raise StopIteration

# web.py utils
def to36(q):
    """
    Converts an integer to base 36 (a useful scheme for human-sayable IDs).
    
        >>> to36(35)
        'z'
        >>> to36(119292)
        '2k1o'
        >>> int(to36(939387374), 36)
        939387374
        >>> to36(0)
        '0'
        >>> to36(-393)
        Traceback (most recent call last):
            ... 
        ValueError: must supply a positive integer
    
    """
    if q < 0: raise ValueError, "must supply a positive integer"
    letters = "0123456789abcdefghijklmnopqrstuvwxyz"
    converted = []
    while q != 0:
        q, r = divmod(q, 36)
        converted.insert(0, letters[r])
    return "".join(converted) or '0'

# http://birdnest.googlecode.com/svn/branches/gae/web/utils.py
def cond(predicate, consequence, alternative=None):
    """
    Function replacement for if-else to use in expressions.
        
        >>> x = 2
        >>> cond(x % 2 == 0, "even", "odd")
        'even'
        >>> cond(x % 2 == 0, "even", "odd") + '_row'
        'even_row'
    """
    if predicate:
        return consequence
    else:
        return alternative

def getarr(arr, idx, default=None):
    try:
        return arr[idx]
    except: pass
    return default

def medium_size(attachments):
    for a in attachments:
        if a['type'] in IMAGE_CONTENT_TYPES:
            return a['thumb_src'].replace('.s.', '.m.')
    return 'default_cover.png'

### html tag helpers
def link_to(to, label=None, **attrs):
    attrs = attrs_to_str(attrs)
    if not label:
        label = to
    return "<a href='%s' %s><span><span>%s</span></span></a>" % (to, attrs, label)

def link_if_auth(user, to, label, usertype_needed='all', **attrs):
    if user:
        if (isinstance(usertype_needed, list) and usertype_needed.count(user['type'])) \
            or user['type'] == usertype_needed \
            or usertype_needed == 'all' \
            or user['is_admin']:
            return link_to(to, label, **attrs)
    return ''

def link_if_editor(user, author, to, label, **attrs):
    if user and (user['is_admin'] or user == author):
        return link_to(to, label, **attrs)
    return ''

def link_button_if_editor(user, author, to, label, token):
    attrs = {
                '_class':'button', 
                'onclick': 'if (confirm("Are you sure?")) { var f = $("<form method=post ><input type=hidden name=_xsrf value=%s /></form>").get(0); this.parentNode.appendChild(f); f.action = this.href;f.submit(); };return false;' % token
            }
    return link_if_editor(user, author, to, label, **attrs)

def select(name, args, *validators, **attrs):
    from forms import Dropdown
    dropdown = Dropdown(name, args, *validators, **attrs)
    return dropdown.render()
    
def query_string(url,remove=None):
    if remove:
        import re
        for q in remove:
            url = re.sub("([?&]?)%s=[\w:-]+[?&]?" % q, '', url)
    return url
    