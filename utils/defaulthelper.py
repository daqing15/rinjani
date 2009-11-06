
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
    from .time import timesince
    return timesince(time, now)

def timeuntil(dt):
    from .time import timeuntil
    return timeuntil(dt)

def utc_to_local(dt):
    return dt.replace(tzinfo=None)

def time(dt, format=""):
    return dt.strftime("")

def alternate(items):
    return items[0]

def get(val, default):
    return val or default

def getarr(arr, idx, default=None):
    try:
        return arr[idx]
    except: pass
    return default

def medium_size(attachment):
    return attachment['thumb_src'].replace('.s.', '.m.')

### html tag helpers
def link_to(to, label=None, **attrs):
    attrs = attrs_to_str(attrs)
    if not label:
        label = to
    return "<a href='%s' %s>%s</a>" % (to, attrs, label)

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
    

    