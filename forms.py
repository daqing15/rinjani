from web import form
from datetime import datetime
from utils.string import listify
import re
import logging

class InvalidFormDataError(Exception): pass

def _(str):
    if getattr(MyForm, 'locale', None):
        str = MyForm.locale.translate(str)
    #return tornado.escape.xhtml_escape(str)
    return str

BANKS = [('bca', 'BCA'), ('mandiri','Bank Mandiri'), ('muamalat', 'Bank Muamalat')]

class MyForm(form.Form):
    def __init__(self, *inputs, **kw):
        self.handler = None
        form.Form.__init__(self, *inputs, **kw)

    def render_css(self):
        out = []
        out.append(self.rendernote(self.note))
        for i in self.inputs:
            try:
                if i.pre_separator:
                    out.append('<hr /')    
            except: pass
                
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
            html = """
<div id="flash_message">
    <script type="text/javascript">
        document.getElementById('flash_message').style.display = 'none';
    </script>
    <span>%s</span>
</div>"""
            return html % _(note)
        return ""

class Input(form.Input):
    def rendernote(self, note):
        if note: return '<p class="invalid">%s</p>' % _(note)
        else: return ""

class Textarea(form.Textarea, Input): pass
class Textbox(Input, form.Textbox): pass
class Password(Input, form.Password): pass
class Dropdown(Input, form.Dropdown): pass
class File(Input, form.File): pass

class Datefield(Textbox): 
    def get_value(self):
        d = datetime.strptime(self.value, '%d/%m/%Y')
        return d.strftime('%d/%m/%Y')
    
    def set_value(self, value):
        if isinstance(value, datetime):
            self.value = value.strftime('%d/%m/%Y')
        else:
            self.value = value
        
class Checkbox(form.Checkbox, Input): 
    def set_value(self, value):
        pass
    
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
    def __init__(self, len, sep, msg):
        self.len = len
        self.msg = msg
        self.sep = sep
        
    def valid(self, value):
        if not value: return True
        chunks = listify(value, self.sep)
        return bool(len(chunks)) 

class PassValidator(form.Validator):
    def __init__(self): pass 
        
    def valid(self, f):
        p1 = f.get('password', None)
        p2 = f.get('password2', None)
        if not p1 and not p2:
            return True
        elif p1 and p2 and p1 == p2:
            self.msg = "Password length must be between 6-20"
            return bool(re.compile(".{6,20}").match(f.password))
        
        self.msg = "Password didn't match"
        return False
    
vpass = form.regexp(r".{6,20}", 'Must be between 6 and 20 characters')
vemail = form.regexp(r".*@.*", "Must be a valid email address")


register_form = MyForm(
    Textbox("username", form.notnull, description="User Name"),
    Password("password", form.notnull, vpass, description="Password"),
    Password("password2", form.notnull, vpass, description="Repeat password"),
    Dropdown(name='type', args=[('public', 'Public/None of above'), ('agent', 'Staff of Social Organization'), ('sponsor', 'Corporate Representative')], description='I am a'),
    Checkbox("agree", form.notnull, checked=False, value="1", pre_separator=True, description="I agree to <a target='_blank' href='/page/tos'>Terms of Service</a> of Peduli"),
    validators = [form.Validator("Passwords didn't match", lambda i: i.password == i.password2)]
)

new_user_form = MyForm(
    Textbox("username", form.notnull, description="User Name (no space, only alphabets and numbers)"),
    Dropdown(name='type', args=[('agent', 'Staff of Social Organization'), ('sponsor', 'Corporate Representative'), ('public', 'Public/None of above')], description='I am a'),
    Checkbox("agree", form.notnull, checked=False, value="1", pre_separator=True, description="I agree to <a target='_blank' href='/page/tos'>Terms of Service</a> of Peduli"),
)

login_form = MyForm(
    Textbox("username", form.notnull, size=30, description="Username"),
    Password("password", form.notnull, size=30, description="Password"),
)

activity_form = MyForm(
    Textbox("title", form.notnull, size=43, description="Title"),
    Datefield("date_start", _class="date", size=12, description="Start"),
    Datefield("date_end", _class="date", size=12, description="End"),
    Textarea("excerpt", rows=2, cols=40, description="Excerpt"),
    Textarea("content", form.notnull, _class="rte", rows=19, cols=50, description="Content"),
    Textarea("deliverable", _class="rte", rows=9, cols=40, description="Deliverable"),
    Checkbox("need_donation", value="1", description="Need donation"),
    Checkbox("need_volunteer", value="1", description="Need volunteer"),
    Checkbox("enable_comment", value="1", description="Enable comments"),
    Textbox("tags", MaxChunks(4, ',', "Must be at most three tags"), size=53, description="Tags")
 )

article_form = MyForm(
    Textbox("title", form.notnull, size=53, description="Title"),
    Textarea("excerpt", form.notnull, rows=3, cols=60, description="Excerpt", title="Write it short and sweet. "),
    Textarea("content", form.notnull, rows=14, cols=60, _class="rte", description="Article Content", title="You can enter some formatting blah blah"),
    Textbox("tags", MaxChunks(4, ',', "Must be at most three tags"), size=53, description="Tags", title="Separate with comma")
 )

commentbox_form = MyForm(
    Textarea("content", form.notnull, rows=3, cols=25, description="Say something"),
)

page_form = MyForm(
    Textbox("title", form.notnull, size=53, description="Title"),
    Textbox("slug", form.notnull, size=53, description="Slug - use alphabet and dash (-)"),
    Textarea("content", form.notnull, rows=6, cols=50, description="Content", _class="rte"),
)

account_form = MyForm(
    Password("password", form.notnull, vpass, size=20, description="Password", title="Combine alphabet with numbers"),
    Password("password2", form.notnull, vpass, size=20, description="Repeat Password"),
    validators = [PassValidator()]
    
)

profile_form = MyForm(
    Textbox("last_name", form.notnull, size=40, description="Full Name", title="Your organization/ corporate full name, eg. ACT Dompet Dhuafa"),
    Textarea("about", form.notnull, rows=3, cols=40, description="About You",title="Describe your entity in short paragraph"),
    Textarea("profile_content", form.notnull, _class="rte", rows=10, cols=70, description="Your Organization in Lengthy Words", title="Tulis yang panjang"),
    Textbox("contact_person", size=40, description="Contact Person Name"),
    Textbox("phones", size=40, description="Phones", title="You can enter more than one number. Separate them with comma"),
    Textbox("fax", size=40, description="Fax"),
    Textarea("address", rows=3, cols=40, description="Address"),
    Textbox("email", size=40, description="E-Mail"),
    Textbox("website", size=40, description="Website"),
    Textbox("tags", MaxChunks(4, ',', "Must be at most three tags"), size=40, description="Tags", title="Blah")
)

profile_public_form = MyForm(
    Textbox("first_name", form.notnull, size=53, description="First Name"),
    Textbox("last_name", form.notnull, size=53, description="Last Name"),
    Textbox("dateofbirth", size=53, description="Date of Birth"),
    Textarea("about", form.notnull, rows=3, cols=50, description="Short description about you"),
)
