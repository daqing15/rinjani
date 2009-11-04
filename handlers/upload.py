import os
import subprocess
import logging
import shutil
import tempfile
from mimetypes import guess_extension
from tornado.escape import url_escape
from main import BaseHandler, authenticated
from utils.utils import unique_filename, create_thumbnails

class UploadHandler(BaseHandler):
    html = r"""
<div class='thumb tt' title='%(title)s'>    
<a href='#' onclick='R.insertAtCaret("#content", "{{attachment %(no)d caption=\"Edit the caption\"}}\n")'>
<img title='Click to insert %(title)s' src='%(src)s' />
<span>%(no)d</span>
</a>    
</div>
"""
    # [((width, height), cropped?)]
    thumb_sizes = [((50,50), True, 's'), ((550, 700), False, 'm')]
    image_content_types = ['image/jpeg', 'image/png', 'image/gif']
    allowed_content_types = image_content_types +  \
            ['application/msword', 'application/msexcel', 'application/pdf']
    
    def json_response(self, response="ERROR", status='OK'):
        self.finish(dict(status=status, response=response))
    
    @authenticated()
    def post(self):
        name = self.get_argument('name')
        doc_type = self.get_argument('doc_type', 'article')
        attachments = self.get_argument('attachments', '')
        no = int(self.get_argument("attachment_counter", 0))
        is_new_doc = bool(int(self.get_argument('is_new_doc'), 0)) 
        
        f = self.request.files[name][0]
        name = unique_filename([self.current_user.username, \
                                    doc_type, f['filename'], str(len(f['body']))])
        
        logging.warning(self.get_arguments())
        
        try:
            """ 
            Save file to tmp. Check mime; dont trust f['content_type']; use 
            /usr/bin/file instead. If OK, move back to /static/uploads
            """ 
            
            tmppath =  os.path.join(tempfile.gettempdir(), name)
            with open(tmppath, mode="wb") as file:
                file.write(f['body'])
            
            file_type = ''
            try:
                out = subprocess.Popen("/usr/bin/file -i %s" % tmppath, shell=True, stdout=subprocess.PIPE).communicate()[0]
                file_type = out.split()[1]
            except:
                raise
                return self.json_response('NOT ALLOWED', 'ERROR')
            
            ext = guess_extension(file_type)
            if file_type not in self.allowed_content_types:
                try:
                    os.remove(tmppath)
                except: pass
                return self.json_response('NOT ALLOWED', 'ERROR')
            
            if is_new_doc:
                logging.error("============ FILE BARU ============+")
                name = os.path.join("tmp", name)
            
            filename = name + ext
            upload_path = self.settings.upload_path
            path = os.path.join(upload_path, filename)
            shutil.move(tmppath, path)
            
            if file_type in self.image_content_types:
                logging.error('Creating thumbnails for' + path)
                create_thumbnails(path, self.thumb_sizes)
                logging.error('Done creating thumbnails')
                thumb_src = self.settings.upload_url + '/' + name + '.s' + ext 
            else:
                thumb_src = self.settings.static_url + '/img/attachment.png'
            
            no += 1
            title = url_escape(f['filename'])
            
            """ no#filetype#src#thumb_src#filename"""
            attachment = "%d#%s#%s#%s#%s" % (no, file_type, filename, thumb_src, title)
            attachments = [a for a in attachments.split('$') if a]
            attachments = "$".join(attachments + [attachment])
            
            html = self.html % dict(no=no, src=thumb_src, title=title)
            return self.json_response(dict(html=html, attachments=attachments, counter=no))
        except Exception, e:  
            return self.json_response(e,'ERROR')
        
        return self.json_response("Error",'ERROR')
        
