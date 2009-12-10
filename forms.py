import re
from datetime import datetime
from tornado.escape import xhtml_escape
from web import form
from utils.string import listify, dummy_translate as _
from settings import USERTYPE, TIMEZONES

class InvalidFormDataError(Exception): pass

def __(str):
    if getattr(MyForm, 'locale', None):
        str = MyForm.locale.translate(str)
    return str

def is_required(input):
    for v in input.validators:
        if getattr(v, 'test', None):
            if v.test is bool:
                return True
    return False

def is_checkbox(input):
    return isinstance(input, Checkbox)


class MyForm(form.Form):
    def __init__(self, *inputs, **kw):
        self.handler = None
        form.Form.__init__(self, *inputs, **kw)

    def add_notnull_validator(self, thing, msg):
        self.validators.append(form.Validator(msg, lambda x: bool(thing)))

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
                out.append('<label for="%s">%s %s</label>' % (i.id, __(i.description), i.rendernote(i.note)))
                out.append(i.render())
            #out.append(i.rendernote(i.note))
            out.append('</div>')
            out.append('\n')
        return ''.join(out)

    def rendernote(self, note):
        if isinstance(note, Exception):
            note = note.__str__()

        if note:
            html = """
<div id="flash_message">
    <script type="text/javascript">
        document.getElementById('flash_message').style.display = 'none';
    </script>
    <span>%s</span>
</div>"""
            return html % xhtml_escape(__(note))
        return ""

class Input(form.Input):
    def rendernote(self, note):
        if note: return '<span class="invalid">%s</span>' % _(note)
        else: return ""

class Textarea(Input, form.Textarea): pass
class Textbox(Input, form.Textbox): pass
class Password(Input, form.Password): pass
class File(Input, form.File): pass

class Dropdown(Input, form.Dropdown):
    def render(self):
        for i, arg in enumerate(self.args):
            if isinstance(arg, (tuple, list)):
                value, desc = arg
            else:
                value, desc = arg, arg
            self.args[i] = (value, __(desc))
        return super(Dropdown, self).render()


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

    def render(self):
        self.value = __(self.value)
        return super(Checkbox, self).render()


class Button(form.Button):
    def render(self):
        attrs = self.attrs.copy()
        attrs['name'] = self.name
        attrs['class'] = 'button'
        return '<button %s>%s</button>' % (attrs, __(self.name.title()))

class MaxLength(form.Validator):
    def __init__(self, len):
        self.len = len
        self.msg = _("Maximum %d chars") % len
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
            self.msg = _("Password length must be between 6-20")
            return bool(re.compile(".{6,20}").match(f.password))

        self.msg = _("Password didn't match")
        return False

vusername = form.regexp(r"[a-z0-9]{6,9}", _("4-9 characters of alphabets and numbers, without space"))
vpass = form.regexp(r".{6,20}", _('Must be between 6 and 20 characters'))
vemail = form.regexp(r".*@.*", _("Must be a valid email address"))

api_request_form = MyForm(
    Textbox("email", form.notnull, vemail, description=_("Your email")),
    Textbox("fullname", form.notnull, description=_("Your full name")),
    Textbox("website", description=_("Your website")),
    Textarea("about", rows=3, cols=39, description=_("What are you planning to make?")),
)

register_form = MyForm(
    Textbox("username", form.notnull, vusername, description=_("User Name"), title=_("4-9 characters of alphabets and numbers, without space")),
    Password("password", form.notnull, vpass, description=_("Password")),
    Password("password2", form.notnull, description=_("Repeat password"), title=_("Repeat password")),
    Dropdown(name='type', args=USERTYPE, description=_('I am a')),
    Checkbox("agree", form.notnull, checked=False, value="1", pre_separator=True, description=_("I agree to <a target='_blank' href='/page/tos'>Terms of Service</a> of Peduli")),
    validators = [form.Validator(_("Passwords didn't match"), lambda i: i.password == i.password2)]
)

new_user_form = MyForm(
    Textbox("username", form.notnull, vusername, description=_("User Name"), title=_("4-9 characters of alphabets and numbers, without space")),
    Dropdown(name='type', args=[('agent', _('Staff of Social Organization')), ('sponsor', _('Corporate Representative')), ('public', 'Public/None of above')], description='I am a'),
    Checkbox("agree", form.notnull, checked=False, value="1", pre_separator=True, description=_("I agree to <a target='_blank' href='/page/tos'>Terms of Service</a> of Peduli")),
)

login_form = MyForm(
    Textbox("username", form.notnull, size=30, description=_("Username")),
    Password("password", form.notnull, size=30, description=_("Password")),
)

activity_form = MyForm(
    Textbox("title", form.notnull, size=39, description=_("Title")),
    Datefield("date_start", _class="date", size=15, description=_("Start")),
    Datefield("date_end", _class="date", size=15, description=_("End")),
    Textarea("excerpt", rows=3, cols=39, description=_("Excerpt/Lead")),
    Textarea("content", form.notnull, _class="rte", rel="#contentPreview", rows=12, cols=40, description=_("Content")),
    Textbox("donation_amount_needed", size=30, description=_("Amount of donation needed (Rp)")),
    Checkbox("need_donation", value="1", description=_("Needs donations")),
    Checkbox("need_volunteer", value="1", description=_("Needs volunteers")),
    Textbox("volunteer_tags", size="30", description=_("Volunteer skills needed")),
    Checkbox("enable_comment", value="1", description=_("Enable comments")),
    Textbox("tags", MaxChunks(6, ',', _("Must be at most six tags")), size=39, description="Tags"),
    Textbox("lat", size=10, description="Latitude"),
    Textbox("long", size=10, description="Longitude"),
 )

article_form = MyForm(
    Textbox("title", form.notnull, size=50, description=_("Title")),
    Textarea("excerpt", form.notnull, rows=3, cols=60, description=_("Excerpt/Lead"), title="Write it short and sweet. "),
    Textarea("content", form.notnull, rows=12, cols=60, _class="rte", rel="#contentPreview", description="Article Content"),
    Checkbox("enable_comment", value="1", description=_("Enable comments")),
    Textbox("tags", MaxChunks(6, ',', _("Must be at most six tags")), size=50, description="Tags", title="Separate with comma")
 )

comment_form = MyForm(
    Textarea("comment", form.notnull, MaxLength(100), maxlength=140, style="width:180px", rows=4, cols=25, description="Say something"),
)

page_form = MyForm(
    Textbox("title", form.notnull, size=45, description="Title"),
    Textarea("content", form.notnull, rows=15, cols=50, _class="rte", rel="#contentPreview", description=_("Content")),
)

account_form = MyForm(
    Password("password", form.notnull, vpass, size=20, description=_("Password"), title=_("Combine alphabet with numbers")),
    Password("password2", form.notnull, vpass, size=20, description=_("Repeat Password")),
    validators = [PassValidator()]

)

profile_form = MyForm(
    Textbox("fullname", form.notnull, size=40, description=_("Full Name"), title=_("Your organization/ corporate full name, eg. ACT Dompet Dhuafa")),
    Textarea("about", form.notnull, rows=3, cols=40, description=_("About You"),title=_("Describe your entity in short paragraph")),
    Textarea("profile_content", _class="rte", rel="#contentPreview", rows=10, cols=70, description=_("Your Organization in Lengthy Words")),
    Textbox("contact_person", size=40, description=_("Contact Person Name")),
    Textbox("phones", size=20, description="Phones", title=_("Separate numbers with comma")),
    Textbox("fax", size=20, description="Fax", title=_("Separate numbers with comma")),
    Textarea("address", rows=3, cols=40, description=_("Address")),
    Dropdown('timezone', args=TIMEZONES, description=_('Timezone')),
    Textbox("email", size=40, description=_("E-Mail")),
    Textbox("website", size=40, description=_("Website")),
    Textbox("tags", MaxChunks(6, ',', _("Must be at most six tags")), size=40, description="Your Fields/Skills"),
    Textbox("lat", size=10, description="Latitude"),
    Textbox("long", size=10, description="Longitude")
)

