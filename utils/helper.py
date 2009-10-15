
def attrs_to_str(attrs):
    if not isinstance(attrs, dict):
        return ''
    
    attrs = ["%s='%s'" % (k.lstrip('_'),v) for k, v in attrs.iteritems()]
    return ' '.join(attrs)
    
class HtmlHelper:
    @classmethod
    def link_to(cls, to, label=None, **attrs):
        attrs = attrs_to_str(attrs)
        if not label:
            label = to
        return "<a href='%s' %s>%s</a>" % (to, attrs, label)
    
    @classmethod
    def link_if_auth(cls, user, to, label=None, usertype_needed='all', **attrs):
        if user:
            if (isinstance(usertype_needed, list) and usertype_needed.count(user['type'])) \
                or user['type'] == usertype_needed \
                or usertype_needed == 'all' \
                or user['is_admin']:
                return cls.link_to(to, label, **attrs)
        return ''
    
    @classmethod
    def link_if_editor(cls, user, author, to, label=None, **attrs):
        if user and (user['is_admin'] or user == author):
            return cls.link_to(to, label, **attrs)
        return ''
    
    @classmethod
    def select(cls, items, selected=None):
        pass
    
    