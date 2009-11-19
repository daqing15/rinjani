from web import form
from datetime import datetime
from utils.string import listify
import re
from settings import USERTYPE, TIMEZONES

class InvalidFormDataError(Exception): pass

def _(str):
    if getattr(MyForm, 'locale', None):
        str = MyForm.locale.translate(str)
    #return tornado.escape.xhtml_escape(str)
    return str

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
                out.append('<label for="%s">%s <span class="cb-label">%s</span> %s</label>' % (i.id, i.render(), _(i.description), i.rendernote(i.note)))
            else:
                out.append('<label for="%s">%s %s</label>' % (i.id, _(i.description), i.rendernote(i.note)))
                out.append(i.render())
            #out.append(i.rendernote(i.note))
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
        if note: return '<span class="invalid">%s</span>' % _(note)
        else: return ""

class Textarea(Input, form.Textarea): pass
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
        
class Checkbox(Input, form.Checkbox): 
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
        self.msg = "Maximum %d chars" % len 
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

vusername = form.regexp(r"[a-z0-9]{6,9}", "4-9 characters of alphabets and numbers, without space")    
vpass = form.regexp(r".{6,20}", 'Must be between 6 and 20 characters')
vemail = form.regexp(r".*@.*", "Must be a valid email address")


register_form = MyForm(
    Textbox("username", form.notnull, vusername, description="User Name", title="4-9 characters of alphabets and numbers, without space"),
    Password("password", form.notnull, vpass, description="Password"),
    Password("password2", form.notnull, description="Repeat password", title="Retype password"),
    Dropdown(name='type', args=USERTYPE, description='I am a'),
    Checkbox("agree", form.notnull, checked=False, value="1", pre_separator=True, description="I agree to <a target='_blank' href='/page/tos'>Terms of Service</a> of Peduli"),
    validators = [form.Validator("Passwords didn't match", lambda i: i.password == i.password2)]
)

new_user_form = MyForm(
    Textbox("username", form.notnull, vusername, description="User Name", title="4-9 characters of alphabets and numbers, without space"),
    Dropdown(name='type', args=[('agent', 'Staff of Social Organization'), ('sponsor', 'Corporate Representative'), ('public', 'Public/None of above')], description='I am a'),
    Checkbox("agree", form.notnull, checked=False, value="1", pre_separator=True, description="I agree to <a target='_blank' href='/page/tos'>Terms of Service</a> of Peduli"),
)

login_form = MyForm(
    Textbox("username", form.notnull, size=30, description="Username"),
    Password("password", form.notnull, size=30, description="Password"),
)

activity_form = MyForm(
    Textbox("title", form.notnull, size=39, description="Title"),
    Datefield("date_start", _class="date", size=15, description="Start"),
    Datefield("date_end", _class="date", size=15, description="End"),
    Textarea("excerpt", rows=3, cols=39, description="Excerpt/Lead"),
    Textarea("content", form.notnull, _class="rte", rel="#contentPreview", rows=12, cols=40, description="Content"),
    Textbox("donation_amount_needed", size=30, description="Amount of donation needed (Rp)"),
    Checkbox("need_donation", value="1", description="Needs donations"),
    Checkbox("need_volunteer", value="1", description="Needs volunteers"),
    Textbox("volunteer_tags", size="30", description="Volunteer skills needed"),
    Checkbox("enable_comment", value="1", description="Enable comments"),
    Textbox("tags", MaxChunks(6, ',', "Must be at most six tags"), size=39, description="Tags"),
    Textbox("lat", size=10, description="Latitude"),
    Textbox("long", size=10, description="Longitude"),
 )

article_form = MyForm(
    Textbox("title", form.notnull, size=50, description="Title"),
    Textarea("excerpt", form.notnull, rows=3, cols=60, description="Excerpt/Lead", title="Write it short and sweet. "),
    Textarea("content", form.notnull, rows=12, cols=60, _class="rte", rel="#contentPreview", description="Article Content"),
    Textbox("tags", MaxChunks(6, ',', "Must be at most six tags"), size=50, description="Tags", title="Separate with comma")
 )

comment_form = MyForm(
    Textarea("comment", form.notnull, MaxLength(100), maxlength=140, style="width:180px", rows=4, cols=25, description="Say something"),
)

page_form = MyForm(
    Textbox("title", form.notnull, size=45, description="Title"),
    Textbox("slug", form.notnull, size=45, description="Slug - use alphabet, numbers, and dash (-)"),
    Textarea("content", form.notnull, rows=15, cols=50, _class="rte", rel="#contentPreview", description="Content"),
)

account_form = MyForm(
    Password("password", form.notnull, vpass, size=20, description="Password", title="Combine alphabet with numbers"),
    Password("password2", form.notnull, vpass, size=20, description="Repeat Password"),
    validators = [PassValidator()]
    
)

profile_form = MyForm(
    Textbox("fullname", form.notnull, size=40, description="Full Name", title="Your organization/ corporate full name, eg. ACT Dompet Dhuafa"),
    Textarea("about", form.notnull, rows=3, cols=40, description="About You",title="Describe your entity in short paragraph"),
    Textarea("profile_content", _class="rte", rel="#contentPreview", rows=10, cols=70, description="Your Organization in Lengthy Words", title="Tulis yang panjang"),
    Textbox("contact_person", size=40, description="Contact Person Name"),
    Textbox("phones", size=20, description="Phones", title="Separate numbers with comma"),
    Textbox("fax", size=20, description="Fax", title="Separate numbers with comma"),
    Textarea("address", rows=3, cols=40, description="Address"),
    Dropdown('timezone', args=TIMEZONES, description='Timezone'),
    Textbox("email", size=40, description="E-Mail"),
    Textbox("website", size=40, description="Website"),
    Textbox("tags", MaxChunks(4, ',', "Must be at most three tags"), size=40, description="Your Fields/Skills"),
    Textbox("lat", size=10, description="Latitude"),
    Textbox("long", size=10, description="Longitude")
)

