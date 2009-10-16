import web
from web import form
from tornado.escape import xhtml_escape
import logging

class InvalidFormDataError(Exception): pass

def _(str):
    if getattr(MyForm, 'locale', None):
        str = MyForm.locale.translate(str)
    #return web.net.websafe(str)
    return str

class Input(form.Input):
    def rendernote(self, note):
        if note: return '<p class="invalid">%s</p>' % _(note)
        else: return ""

class Textarea(Input, form.Textarea): pass
class Textbox(Input, form.Textbox): pass
class Password(Input, form.Password): pass
class Dropdown(Input, form.Dropdown): pass
class Checkbox(Input, form.Checkbox): pass

class MyForm(form.Form):
    def __init__(self, *inputs, **kw):
        self.handler = None
        form.Form.__init__(self, *inputs, **kw)

    def render_css(self):
        out = []
        out.append(self.rendernote(self.note))
        for i in self.inputs:
            sep = False
            try:
                sep = i.pre_separator
                print "ada sep"
            except: pass
            if sep:
                out.append('<hr /')
                
            out.append('<div class="i">')
            if isinstance(i, Checkbox):
                out.append('<label for="%s">%s <span class="cb-label">%s</span></label>' % (i.id, i.render(), _(i.description)))
            else:
                out.append('<label for="%s">%s</label>' % (i.id, _(i.description)))
                out.append(i.render())
            out.append(self.rendernote(i.note))
            out.append('</div>')
            out.append('\n')
        return ''.join(out)

    def rendernote(self, note):
        if note:
            return '<p class="invalid">%s</p>' % _(note)
        else:
            return ""

class Button(form.Button):
    def render(self):
        attrs = self.attrs.copy()
        attrs['name'] = self.name
        attrs['class'] = 'button'
        return '<button %s>%s</button>' % (attrs, _(self.name.title()))

class MaxLength(form.Validator):
    def __init__(self, len):
        self.len = len
        self.msg = "Max length is %d" % len 
    def valid(self, value):
        if not value: return True
        return bool(len(value) <= self.len) 

class MaxChunks(form.Validator):
    def __init__(self, len, separator, msg):
        self.len = len
    def valid(self, value):
        if not value: return True
        #return bool(len(value) <= self.len)
        return True 
            
vpass = form.regexp(r".{3,20}", 'Must be between 3 and 20 characters')
vemail = form.regexp(r".*@.*", "Must be a valid email address")

register_form = MyForm(
    Textbox("username", form.notnull, description="User Name"),
    Password("password", form.notnull, vpass, description="Password"),
    Password("password2", form.notnull, vpass, description="Repeat password"),
    Dropdown(name='type', args=[('agent', 'Staff of Social Organization'), ('sponsor', 'Corporate Representative'), ('public', 'Public/None of above')], description='I am a'),
    Checkbox("agree", form.notnull, checked=False, value="1", pre_separator=True, description="I agree to <a target='_blank' href='/page/tos'>Terms of Service</a> of Peduli"),
    validators = [form.Validator("Passwords didn't match", lambda i: i.password == i.password2)]
)

login_form = MyForm(
    Textbox("username", form.notnull, size=30, description="Username"),
    Password("password", form.notnull, size=30, description="Password"),
)

activity_form = MyForm(
    Textbox("title", form.notnull, size=53, description="Title"),
    Textarea("excerpt", form.notnull, rows=2, cols=50, description="Excerpt"),
    Textarea("content", form.notnull, rows=7, cols=50, description="Content"),
    Textarea("deliverable", form.notnull, rows=3, cols=50, description="Deliverable"),
    Checkbox("need_donation", checked=True, pre_separator=True, description="Need donation?"),
    Checkbox("need_volunteer", checked=False, description="Need volunteer?"),
    Textbox("tags", MaxChunks(4, ',', "Must be at most three tags"), size=53, description="Tags")
 )

article_form = MyForm(
    Textbox("title", form.notnull, size=53, description="Title"),
    Textarea("excerpt", form.notnull, rows=3, cols=50, description="Excerpt"),
    Textarea("content", form.notnull, rows=6, cols=50, description="Content"),
    Textbox("tags", MaxChunks(4, ',', "Must be at most three tags"), size=53, description="Tags")
 )

commentbox_form = MyForm(
    Textarea("content", form.notnull, rows=3, cols=25, description="Say something"),
)

page_form = MyForm(
    Textbox("title", form.notnull, size=53, description="Title"),
    Textbox("slug", form.notnull, size=53, description="Slug - use alphabet and dash (-)"),
    Textarea("content", form.notnull, rows=6, cols=50, description="Content"),
)

profile_form = MyForm(
    Textbox("fullname", form.notnull, size=53, description="Full Name"),
    Textarea("about", form.notnull, rows=3, cols=50, description="Short description about you"),
    Textarea("profile_content", form.notnull, rows=10, cols=50, description="Long description about you"),
)

profile_public_form = MyForm(
    Textbox("fullname", form.notnull, size=53, description="Full Name"),
    Textbox("dateofbirth", size=53, description="Date of Birth"),
    Textarea("about", form.notnull, rows=3, cols=50, description="Short description about you"),
)

