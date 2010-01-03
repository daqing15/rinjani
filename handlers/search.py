import tornado.web

from main import BaseHandler
from rinjani.indexing import index
from rinjani.pagination import SearchPagination
        
class SearchHandler(BaseHandler):
    def get(self, type=None):
        q = self.get_argument('q', None)
        args = self.request.arguments
        sortby = self.get_argument('sb', 'score')
        sort = self.get_argument('s', 'desc')
        faceted = False
        params = {'sort':"%s %s" % (sortby,sort)}
        
        _ = self._
        
        try:
            if type == 'near':
                radius = self.get_argument('radius', 600)
                params.update({
                           'qt': 'geo',
                           'radius': radius, 
                           'lat': self.get_argument('lat'), 
                           'lng': self.get_argument('lng')
                           })
            elif q:
                params.update({'facet': 'true', 
                               'facet.field': ['type','tags','geo_distance']})
                faceted = True
                if 'fq' in args:
                    params.update({'fq': args['fq']})
            
            if q or type == 'near':
                pagination = SearchPagination(self, index, q, params)
                self.render("search", pagination=pagination, q=q, error=None,\
                            faceted=faceted, sortby=sortby)
                return
        except tornado.web.HTTPError:
            self.render("search", pagination=[], q=q, error=_("Missing location attributes."))
            return
        except:
            self.render("search", pagination=[], q=q, error=_("Search facility is down"))
            return
        
        self.render("search", pagination=[], q=q, error=_("Empty query"),sortby=sortby)
