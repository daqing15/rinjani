"""
Adapted from solace.utils.pagination
"""

import math
from tornado.web import HTTPError
import pymongo
from werkzeug import url_encode

class Pagination(object):
    """Pagination helper."""

    threshold = 3
    left_threshold = 3
    right_threshold = 1
    normal = u'<a href="%(url)s">%(page)d</a>'
    active = u'<strong>%(page)d</strong>'
    commata = u'<span class="commata">,\n</span>'
    ellipsis = u'<span class="ellipsis">...\n</span>'

    def __init__(self, req, doc_class, query, per_page=15, link_func=None):
        self.page = int(req.get_argument('page', 1))
        self.doc_class = doc_class
        self.query = query
        self.per_page = per_page
        self.translate = req.locale.translate
        self.total = doc_class.all(query).count()
        
        self.pages = int(math.ceil(self.total / float(self.per_page)))
        self.necessary = self.pages > 1
        
        if link_func is None:
            link_func = lambda x: '?page=%d' % self.page
            url_args = req.get_arguments()
            def link_func(page):
                url_args['page'] = page
                return u'?' + url_encode(url_args)
        self.link_func = link_func
    
    @property
    def total_pages(self):
        return self.pages
    
    def __str__(self):
        return str(self.__unicode__())
    
    def __unicode__(self):
        if not self.necessary:
            return u''
        return u'<div class="pagination">%s</div>' % self.generate()

    def get_objects(self, raise_not_found=True):
        """Returns the objects for the page."""
        if raise_not_found and self.page < 1:
            raise HTTPError(404)
        rv = self.doc_class.all(self.query).sort('created_at', pymongo.DESCENDING).skip(self.offset).limit(self.per_page)
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
                          (self.link_func(next), _(u'Next &gt;')))

        return u''.join(result)
