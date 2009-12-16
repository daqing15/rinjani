"""
Adapted from solace.utils.pagination
"""
import logging
import urllib
import math
from tornado.web import HTTPError

class Pagination(object):
    """Pagination helper."""

    threshold = 6
    left_threshold = 4
    right_threshold = 3
    normal = u'<a href="%(url)s">%(page)d</a>'
    active = u'<strong>%(page)d</strong>'
    commata = u'<span class="commata">,\n</span>'
    ellipsis = u'<span class="ellipsis">...\n</span>'

    def __init__(self, req, doc_class, query=None, per_page=16, fields=None, \
                    wrap=None, link_func=None, sort_by='created_at', sort=-1):
        self.query = {} if query is None else query
        self.fields = fields
        self.page = int(req.get_argument('page', 1))
        self.doc_class = doc_class
        self.per_page = int(req.get_argument('per_page', per_page))
        self.sort_by = sort_by
        self.sort = sort
        self.wrap = wrap is None
        self.req = req

        self.translate = req.locale.translate
        self.pages = int(math.ceil(len(self) / float(self.per_page)))
        self.necessary = self.pages > 1

        if link_func is None:
            link_func = lambda x: '?page=%d' % self.page
            url_args = req.get_arguments()
            def link_func(page):
                url_args['page'] = page
                return u'?' + urllib.urlencode(url_args)
        self.link_func = link_func

    def __len__(self):
        return self.doc_class.all(self.query).count()

    def __str__(self):
        return str(self.__unicode__())

    def __unicode__(self):
        if not self.necessary:
            return u''
        return u'<div class="line pagination">%s</div>' % self.generate()

    def get_objects(self, raise_not_found=True):
        """Returns the objects for the page."""
        
        if raise_not_found and self.page < 1:
            raise HTTPError(404)
        
        if self.fields:
            cursor = self.doc_class.all(self.query, fields=self.fields,\
                                        wrap=self.wrap)
        else:
            cursor = self.doc_class.all(self.query)
        rv = cursor \
                .skip(self.offset)\
                .limit(self.per_page) \
                .sort(self.sort_by, self.sort)

        if raise_not_found and self.page > 1 and not rv:
            raise HTTPError()
        return rv

    @property
    def offset(self):
        return (self.page - 1) * self.per_page

    def generate(self):
        """This method generates the pagination."""
        was_ellipsis = False
        result = []
        next = None
        _ = self.translate

        for num in xrange(1, self.pages + 1):
            if num == self.page:
                was_ellipsis = False
            if num - 1 == self.page:
                next = num
            if num <= self.left_threshold or \
               num > self.pages - self.right_threshold or \
               abs(self.page - num) < self.threshold:
                if result and not was_ellipsis:
                    result.append(self.commata)
                link = self.link_func(num)
                template = num == self.page and self.active or self.normal
                result.append(template % {
                    'url':      link,
                    'page':     num
                })
            elif not was_ellipsis:
                was_ellipsis = True
                result.append(self.ellipsis)

        if next is not None:
            result.append(u'<span class="sep"> </span>'
                          u'<a href="%s" class="next">%s</a>' %
                          (self.link_func(next), _(u'Next') + ' &gt;'))
        
        args = self.req.get_arguments()
        args.pop('per_page', None), args.pop('page', None)
        cp = self.req.request.path + "?" + urllib.urlencode(args)
        html = u''.join(result)
        html = u"<div style='float:right'>%s</div><div style='float:left'><a href='%s&amp;per_page=16'>16</a> <a href='%s&amp;per_page=32'>32</a> <a href='%s&amp;per_page=60'>60</a> %s</div>" % (html, cp, cp, cp, _('per page'))
        return html

class ListPagination(Pagination):
    def __init__(self, req, objects, per_page=16, fields=None, link_func=None):
        self.objects = objects
        super(ListPagination, self).__init__( \
                req, object, {}, per_page, fields, link_func)

    def __len__(self):
        return len(self.objects)

    def get_objects(self):
        from itertools import islice
        return islice(
                iter(self.objects),
                self.offset,
                self.offset + self.per_page
            )

class SearchPagination(Pagination):
    def __init__(self, req, solr, query=None, params={}, per_page=16, \
                 fields=None, link_func=None):
        self.page = int(req.get_argument('page', 1))
        self.per_page = int(req.get_argument('per_page', per_page))
        self.req = req
        
        fields = fields or "id,type,path,score,updated_at,tags,title"
        query_params = {
                          'rows': per_page, 
                          'fl':fields,
                          'start': self.offset,
                          'hl': 'on',
                          'hl.fl': 'content',
                        }
        query_params.update(params)
        results = solr.search(query, **query_params)
        
        if 'facet' in query_params:
            results.facets = results.facets['facet_fields']
        self.results = results
        
        self.translate = req.locale.translate
        self.pages = int(math.ceil(len(self) / float(self.per_page)))
        self.necessary = self.pages > 1

        if link_func is None:
            link_func = lambda x: '?page=%d' % self.page
            url_args = req.get_arguments()
            def link_func(page):
                url_args['page'] = page
                return u'?' + urllib.urlencode(url_args)
        self.link_func = link_func
        
    def __len__(self):
        return self.results.hits
    
    @property
    def offset(self):
        return (self.page - 1) * self.per_page
    
    def get_objects(self, raise_not_found=True):
        return self.results.docs
    
    def __getitem__(self, key):
        return getattr(self.results, key)
    
            