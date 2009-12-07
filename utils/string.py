import re
from BeautifulSoup import BeautifulSoup, Comment
import markdown2

def dummy_translate(str):
    """ Dummy _. used to catch gettext. 
        actual translation is done in tabs.html template.
    """
    return str

def markdown(s):
    return s and markdown2.markdown(s)

def title(s):
    """Converts a string into titlecase."""
    return s and re.sub("([a-z])'([A-Z])", lambda m: m.group(0).lower(), s.title())
    
# django.template.defaultfilters
def capfirst(s):
    """Capitalizes the first character of the value."""
    return s and s[0].upper() + s[1:]

def _strips(direction, text, remove):
    if direction == 'l': 
        if text.startswith(remove): 
            return text[len(remove):]
    elif direction == 'r':
        if text.endswith(remove):   
            return text[:-len(remove)]
    else: 
        raise ValueError, "Direction needs to be r or l."
    return text

def rstrips(text, remove):
    """
    removes the string `remove` from the right of `text`

        >>> rstrips("foobar", "bar")
        'foo'
    
    """
    return _strips('r', text, remove)

def lstrips(text, remove):
    """
    removes the string `remove` from the left of `text`
    
        >>> lstrips("foobar", "foo")
        'bar'
    
    """
    return _strips('l', text, remove)

def strips(text, remove):
    """
    removes the string `remove` from the both sides of `text`

        >>> strips("foobarfoo", "foo")
        'bar'
    
    """
    return rstrips(lstrips(text, remove), remove)

def commify(n, sep='.'):
    """Add commas to an integer `n`"""

    if n is None: return None
    r = []
    for i, c in enumerate(reversed(str(n))):
        if i and (not (i % 3)):
            r.insert(0, sep)
        r.insert(0, c)
    return ''.join(r)

def numify(string):
    """
    Removes all non-digit characters from `string`.
    
        >>> numify('800-555-1212')
        '8005551212'
        >>> numify('800.555.1212')
        '8005551212'
    
    """
    return ''.join([c for c in str(string) if c.isdigit()])

def denumify(string, pattern):
    """
    Formats `string` according to `pattern`, where the letter X gets replaced
    by characters from `string`.
    
        >>> denumify("8005551212", "(XXX) XXX-XXXX")
        '(800) 555-1212'
    
    """
    out = []
    for c in pattern:
        if c == "X":
            out.append(string[0])
            string = string[1:]
        else:
            out.append(c)
    return ''.join(out)

def listify(value, separator=','):
    """
        >>> listify('good, day , ha ha', ',')
        ['good', 'day', 'ha ha']
    """
    if value and value.strip():
        return [item.strip() for item in value.split(separator) if item.strip()]

def sanitize(value, extra_valid_tags=[], extra_valid_attrs=[]):
    """ 
    Filter value from unwanted html tags/attrs
    """
    r = re.compile(r'[\s]*(&#x.{1,7})?'.join(list('javascript:')))
    validTags = 'p i strong b u a h2 h3 h4 pre br img ul ol li'.split()
    validTags += extra_valid_tags
    validAttrs = 'href src alt title height'.split()
    soup = BeautifulSoup(value)
    
    for comment in soup.findAll(text=lambda text: isinstance(text, Comment)):
        comment.extract()
    for tag in soup.findAll(True):
        if tag.name not in validTags:
            tag.hidden = True
        
        tag.attrs = [(attr, r.sub('', val)) for attr, val in tag.attrs
                     if attr in validAttrs]
    return soup.renderContents().decode('utf8')

def strip_tags(value):
    """
        >>> strip_tags('< a good="day">ha</a>')
        'ha'
    """
    return re.sub(r'<[^<]*?/?>', '', value)

def sanitize_tags(tags):
    _tags = []
    for tag in tags:
        tag = slugify(tag)
        _tags.append(tag.replace('-',' '))
    return _tags

def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    import unicodedata
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
    return re.sub('[-\s]+', '-', value)

# taken from django.utils.encoding
def force_unicode(s, encoding='utf-8', errors='strict'):
    try:
        if not isinstance(s, basestring,):
            if hasattr(s, '__unicode__'):
                s = unicode(s)
            else:
                try:
                    s = unicode(str(s), encoding, errors)
                except UnicodeEncodeError:
                    if not isinstance(s, Exception):
                        raise
                    # If we get to here, the caller has passed in an Exception
                    # subclass populated with non-ASCII data without special
                    # handling to display as a string. We need to handle this
                    # without raising a further exception. We do an
                    # approximation to what the Exception's standard str()
                    # output should be.
                    s = ' '.join([force_unicode(arg, encoding, True,
                            errors) for arg in s])
        elif not isinstance(s, unicode):
            # Note: We use .decode() here, instead of unicode(s, encoding,
            # errors), so that if s is a SafeString, it ends up being a
            # SafeUnicode at the end.
            s = s.decode(encoding, errors)
    except UnicodeDecodeError:
        raise
    return s

# django.template.defaultfilters
def truncate_words(s, num):
    "Truncates a string after a certain number of words."
    if not s:
        return s
    
    length = int(num)
    words = s.split()
    if len(words) > length:
        words = words[:length]
        if not words[-1].endswith('...'):
            words.append('...')
    return u' '.join(words)
    
# django.template.defaultfilters
def truncate_html_words(s, num):
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
    