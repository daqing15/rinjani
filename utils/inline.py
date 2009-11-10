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

import re
import settings
import sys

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
    (?P<kwargs>(?:\s\b[a-z_]+=([\"\'][^\"\']+[\"\']|\w+))+)?\Z # kwargs match everything at the end in groups " name=arg"
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
        patt = r"([a-z]+)=([\"\'][^\"\']+[\"\']|\w+)"
        for k,v in re.findall(patt, kwtxt):
            #print "%s: %s" % (k,re.sub("[\'\"]",'', v))
            kwargs[str(k)] = v
        #sys.exit()
        
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
            
            except InlineUnrenderableError:
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
        return "YOUTUBE"
        video_id = self.value
        match = re.search(r'(?<=v\=)[\w]+', video_id)
        if match:
            video_id = match.group()
        print self.kwargs
        return "<embed youtube string here>"

IMAGE_CONTENT_TYPES = ['image/jpeg', 'image/png', 'image/gif']

class SlideshowInline(TemplateInline):
    code = "<div class='unit'><a href='/static/uploads/%(src)s' title='%(filename)s'><img src='/static/uploads/%(thumb_src)s' /></a></div>"
    wrapper = "<div class='line slideshow'>%s</div>"
    def __init__(self, attachments):
        images = []
        for a in attachments:
            if a and a['type'] in IMAGE_CONTENT_TYPES:
                images.append(a.copy())
        self.images = images
        
    def __call__(self, value, **kwargs): return(self)
    
    def render(self):
        if not self.images:
            return ""
        code = ""
        for p in self.images:
            p['thumb_src'] = p['thumb_src'].replace('.s.', '.m.')
            code += self.code % p
        return self.wrapper % code 
    
class AttachmentInline(TemplateInline):
    """
        {{ attachment idx caption="the caption" url="http://example.com" }}
    """
    code_image = "<img src='/static/uploads/%(src)s' />"        
    code = "<a target='_blank' href='/static/uploads/%(src)s'><img src='/static/img/attachment.png' /></a>"
    wrapper = "<div class='attachment'>%(code)s<p class='caption'>%(caption)s</p></div>"
    
    def __init__(self, attachments):
        self.attachments = attachments
        
    def __call__(self, value, **kwargs):
        try:
            self.value = value
            self.kwargs = kwargs
        except: 
            self.value = False
        return self
        
    def render(self):
        if not self.value:
            return ""
        
        from utils import get_attachment_with_filename
        
        if self.attachments:
            try:
                attachment = get_attachment_with_filename(self.value, self.attachments)
                if attachment:
                    self.kwargs.update({'src':attachment['src']})
                    if attachment['type'] in IMAGE_CONTENT_TYPES:
                        code = self.code_image % self.kwargs
                    else:
                        code = self.code % self.kwargs
                    if self.kwargs.has_key('caption'):
                            return self.wrapper % {'code': code, 'caption': self.kwargs['caption'].strip("'")}
                    return code
            except: 
                raise
        return ""
         
# The default registry.
processor = InlineProcessor()
processor.register('youtube', YoutubeInline)
#processor.register('attachment', AttachmentInline(["xx.jpg"])) # call from model

content = """
Isinya

{{ photo 1 title="saya laper"}}

"""

#print processor.process(content)

