import re
import settings

"""
Code taken from django_inlines and slighly modified to be working 
outside django template context
"""

INLINE_SPLITTER = re.compile(r"""
    (?P<name>[a-z_]+)       # Must start with a lowercase + underscores name
    (?::(?P<variant>\w+))?  # Variant is optional, ":variant"
    (?:(?P<args>[^\Z]+))? # args is everything up to the end
    """, re.VERBOSE)

INLINE_KWARG_PARSER = re.compile(r"""
    (?P<kwargs>(?:\s\b[a-z_]+=\w+\s?)+)?\Z # kwargs match everything at the end in groups " name=arg"
    """, re.VERBOSE)

class InlineUnrenderableError(Exception): pass
class InlineInputError(InlineUnrenderableError): pass
class InlineValueError(InlineUnrenderableError): pass
class InlineAttributeError(InlineUnrenderableError): pass
class InlineNotRegisteredError(InlineUnrenderableError): pass
class InlineUnparsableError(InlineUnrenderableError): pass

def parse_inline(text):
    """
    Takes a string of text from a text inline and returns a 3 tuple of
    (name, value, **kwargs).
    """
    m = INLINE_SPLITTER.match(text)
    if not m:
        raise InlineUnparsableError
    args = m.group('args')
    name = m.group('name')
    value = ""
    kwtxt = ""
    kwargs = {}
    if args:
        kwtxt = INLINE_KWARG_PARSER.search(args).group('kwargs')
        value = re.sub("%s\Z" % kwtxt, "", args)
        value = value.strip()
    if m.group('variant'):
        kwargs['variant'] = m.group('variant')
    if kwtxt:
        for kws in kwtxt.split():
            k, v = kws.split('=')
            kwargs[str(k)] = v
    return (name, value, kwargs)

class InlineProcessor(object):
    def __init__(self):
        self._registry = {}
        self.START_TAG = getattr(settings, 'INLINES_START_TAG', '{{')
        self.END_TAG = getattr(settings, 'INLINES_END_TAG', '}}')

    @property
    def inline_finder(self):
        return re.compile(r'%(start)s\s*(.+?)\s*%(end)s' % {'start':self.START_TAG, 'end':self.END_TAG})

    def register(self, name, cls):
        if not hasattr(cls, 'render'):
            raise TypeError("You may only register inlines with a `render` method")
        cls.name = name
        self._registry[name] = cls

    def unregister(self, name):
        if not name in self._registry:
            raise InlineNotRegisteredError("Inline '%s' not registered. Unable to remove." % name)
        del(self._registry[name])
        
    def process(self, text, **kwargs):
        def render(matchobj):
            try:
                text = matchobj.group(1)
                name, value, inline_kwargs = parse_inline(text)
                try:
                    cls = self._registry[name]
                except KeyError:
                    raise InlineNotRegisteredError('"%s" was not found as a registered inline' % name)
                inline = cls(value, **inline_kwargs)
                return str(inline.render())
            
            # Silence any InlineUnrenderableErrors unless INLINE_DEBUG is True
            except InlineUnrenderableError:
                debug = getattr(settings, "debug", False)
                if debug:
                    raise
                else:
                    return ""
        text = self.inline_finder.sub(render, text)
        return text

class TemplateInline(object):
    def __init__(self, value, **kwargs):
        self.value = value
        self.kwargs = kwargs
    
class YoutubeInline(TemplateInline):
    """
        {{ youtube 4R-7ZO4I1pI width=850 height=500 }}
    """
    base_url = "http://www.youtube.com/v"
    code = """
<object type="application/x-shockwave-flash" style="width:%(width)spx; height:%(height)spx;" 
    data="%(base_url)/%(id)s">
    <param name="movie" value="http://www.youtube.com/v/%(id)s" />
</object> 
"""       
    def render(self):
        video_id = self.value
        match = re.search(r'(?<=v\=)[\w]+', video_id)
        if match:
            video_id = match.group()
        return "<embed youtube string here>"

class VimeoInline(TemplateInline):
    base_url = ""
    code = """
<object width='%(width)s' height='%(height)s' type='application/x-shockwave-flash' data='%(url)s'>
<param name='allowfullscreen' value='true' />
<param name='allowscriptaccess' value='always' />
<param name='movie' value='%(url)s' />
</object>
"""        

    def render(self):
        video_id = self.value
        match = re.search(r'(?<=v\=)[\w]+', video_id)
        if match:
            video_id = match.group()
        return "<embed flickr string here>"
        
class FlickrInline(TemplateInline):
    code = """
<object width='%(width)s' height='%(height)s' type='application/x-shockwave-flash' data='%(url)s'>
<param name='allowfullscreen' value='true' />
<param name='allowscriptaccess' value='always' />
<param name='movie' value='%(url)s' />
</object>
"""        

    def render(self):
        video_id = self.value
        match = re.search(r'(?<=v\=)[\w]+', video_id)
        if match:
            video_id = match.group()
        return "<embed flickr string here>"
         
# The default registry.
processor = InlineProcessor()
processor.register('youtube', YoutubeInline)
processor.register('flickr', FlickrInline)

content = """
Isinya
{{ flickr x903xk width=400 }}

Video:
{{ youtube x903xk width=400 }}
"""

#print processor.process(content)

