import re
from BeautifulSoup import BeautifulSoup, Comment
import markdown2

def markdown(s):
    return s and markdown2.markdown(s)

def title(s):
    """Converts a string into titlecase."""
    return s and re.sub("([a-z])'([A-Z])", lambda m: m.group(0).lower(), s.title())
    
# django.template.defaultfilters
def capfirst(s):
    """Capitalizes the first character of the value."""
    return s and s[0].upper() + s[1:]
    
def listify(value, separator=','):
    if value and value.strip():
        return [item.strip() for item in value.split(separator)if item.strip()]

def sanitize(value):
    """ 
    Filter value from unwanted html tags/attrs
    """
    r = re.compile(r'[\s]*(&#x.{1,7})?'.join(list('javascript:')))
    validTags = 'p i strong b u a h1 h2 h3 pre br img'.split()
    validAttrs = 'href src alt title'.split()
    soup = BeautifulSoup(value)
    for comment in soup.findAll(text=lambda text: isinstance(text, Comment)):
        comment.extract()
    for tag in soup.findAll(True):
        if tag.name not in validTags:
            tag.hidden = True
        tag.attrs = [(attr, r.sub('', val)) for attr, val in tag.attrs
                     if attr in validAttrs]
    return soup.renderContents().decode('utf8')

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
    