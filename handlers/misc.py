
import urllib2, urllib
import tornado.web
from main import BaseHandler

class SurveyHandler(BaseHandler):
    GFORM_BASEURL = 'http://spreadsheets.google.com/embeddedform?key='
    GFORM_ACTION = 'http://spreadsheets.google.com/formResponse'
    
    def get(self):
        form_id = self.get_argument('f','').strip()
        if not form_id:
            self.finish("")
            return
        
        # check regex of id, only allow alpha?
        html = self.cache.get("gform:%s" % form_id, True)
        if html:
            self.finish(html)
            return
        
        url = self.GFORM_BASEURL + form_id
        try:
            html = urllib2.urlopen(url).read()
            if html:
                html = self.clean_up(html)
                self.cache.set("gform:%s" % form_id, html, 1800) # 10menit?
                self.finish(html)
        except:
            self.finish("") 
            
    def post(self):
        data = urllib.urlencode(self.get_utf_arguments())
        req = urllib2.Request(self.GFORM_ACTION, data)  
        try:
            html = urllib2.urlopen(req).read()
            html = self.clean_up(html)
            self.finish(html)
            return
        except: pass
        self.finish("ERROR HAPPENED. SH*T.")
    
    def clean_up(self, html):
        html_extra = [
            '<link rel="stylesheet" href="/static/css/embed.css" type="text/css" />',
            ''
        ]
        html = html.replace('</head>', ''.join(html_extra) + '</head>')
        html = html.replace(self.GFORM_ACTION, '/survey/')
        return html
    
    def get_utf_arguments(self):
        args = self.get_arguments()
        args = [(key, value.encode('utf-8')) for key,value in args.iteritems()]
        return dict(args)