import uuid
import datetime
from pymongo.dbref import DBRef

from main import BaseHandler, authenticated
from models import Content, User
from rinjani.string import sanitize

class AddHandler(BaseHandler):
    @authenticated()
    def post(self):
        next = self.get_argument("next", None)
        text = self.get_argument("text")
        content_id = self.get_argument("content_id")
        
        comment = {"id": unicode(uuid.uuid4()), 
                   'user': DBRef(User.collection_name, self.current_user._id),
                   'created_at': datetime.datetime.utcnow(),
                   'text': sanitize(text),
                   }
        
        parent = self.get_argument("parent", None)
        if parent is None:
            comment.update({"responses": []})
            html = self.render_string("modules/statics/item-comment", 
                                      user=self.current_user,
                                      comment=comment,
                                      commenters={self.current_user._id: self.current_user},
                                      item={'_id': content_id}
                                      )
            append_to = "#commentsbox"
        else:
            html = "<p>%s - %s</p>" % (comment['text'], self.current_user['username'])
            append_to = "#resp-" + parent
            
        js_add_comment = """
function add_resp(id, parent,comment) {
    spec = {_id:id}
    c = db.contents.findOne(spec);
    comments = c['comments'];
    if (parent) {
        idx = null;
        for(var i=0; i< comments.length; i++) {
            if (comments[i]['id'] == parent) {idx=i; break;}
        }
        if (idx != null) {
            comments[idx]['responses'].push(comment);
            c['comments'] = comments
            db.contents.save(c);
        }
    } else {
        db.contents.update(spec, {$push: {"comments": comment}});
    }
}        
        """
        Content.collection.database.eval(js_add_comment, content_id, parent, comment)
                    
        if self.is_xhr():
            data = {'append':True, 'html': html, 'target': append_to}
            return self.json_response(None, "OK", data)  
        
class UpdatesHandler(BaseHandler):
    def post(self):        
        pass
        