"""
bad bad code. i gave up.
"""

import os
import subprocess
import logging
import shutil
import tempfile
from mimetypes import guess_extension
from main import BaseHandler, authenticated
from utils.utils import unique_filename, create_thumbnails, sanitize_path
from utils.string import slugify
from models import Article, Activity

PIC_SIZES = [((50,50), True, 's'), ((110,90), True, 'm'), ((550, 700), False, '')]
IMAGE_CONTENT_TYPES = ['image/jpeg', 'image/png', 'image/gif']
ALLOWED_CONTENT_TYPES = IMAGE_CONTENT_TYPES +  \
        ['application/msword', 'application/msexcel', 'application/pdf']
            
class AddHandler(BaseHandler):
    html = r"""
<div class='thumb tt' title='%(filename)s'>    
<img rel='%(type)s' src='/static/uploads/%(thumb_src)s' />
<span class='insert' rel='%(filename)s' title='Click to insert this attachment to content'>^</span>
<span class='rm' rel='%(filename)s' title='Click to remove this attachment'>X</span>
</div>
"""
    # [((width, height), cropped?)]
    
    
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
                return self.json_response('FILE TYPE UNKNOWN', 'ERROR')
            
            ext = guess_extension(file_type)
            if file_type not in ALLOWED_CONTENT_TYPES:
                try:
                    os.remove(tmppath)
                except: pass
                return self.json_response('FILE TYPE NOT ALLOWED', 'ERROR')
            
            if is_new_doc:
                name = os.path.join("tmp", name)
            
            src = name + ext
            upload_path = self.settings.upload_path
            path = os.path.join(upload_path, src)
            shutil.move(tmppath, path)
            
            if file_type in IMAGE_CONTENT_TYPES:
                create_thumbnails(path, PIC_SIZES)
                thumb_src = name + '.s' + ext 
            else:
                thumb_src = self.settings.static_url + '/img/attachment.png'
            
            no += 1
            filename = slugify(f['filename'])
            
            """ no#filetype#src#thumb_src#filename"""
            
            # save to doc
            if not is_new_doc:
                cls = Article if self.get_argument('type') == 'article' else Activity
                try:
                    doc = cls.one({'slug': self.get_argument('slug')} )
                    doc['attachments'] += [dict(type=unicode(file_type), src=unicode(src), thumb_src=unicode(thumb_src), filename=unicode(filename))]
                    doc.save()
                except Exception, e:
                    return self.json_response("Failed updating doc: " + e.__str__(), "ERROR")
                
            attachment = "%s#%s#%s#%s" % (file_type, src, thumb_src, filename)
            attachments = [a for a in attachments.split('$') if a]
            attachments = "$".join(attachments + [attachment])
            
            html = self.html % dict(no=no, type=file_type, thumb_src=thumb_src, filename=filename)
            return self.json_response(None, "OK", dict(html=html, attachments=attachments, counter=no))
        except IOError:
            return self.json_response("Cant write to file system", 'ERROR')
        except Exception, e:
            return self.json_response(e.__str__(),'ERROR')
        
        return self.json_response("Upload failed. Please contact our administrator.",'ERROR')

class RemoveHandler(BaseHandler):
    def remove(self, filename):
        path = os.path.join(self.settings.upload_path, filename)
        logging.error("removing %s" % path)
        try:
            os.remove(path)
        except: pass
        
    def post(self):
        try:
            logging.warning(self.get_arguments())
            
            filename = self.get_argument('filename')
            slug = self.get_argument('slug', None)
            
            thumb = False
            if slug:
                # there's only two kind of doc
                cls = Article if self.get_argument('type') == 'article' else Activity
                doc = cls.one({'slug': slug} )
                
                for i, a in enumerate(doc.attachments):
                    if a['filename'] ==  filename:
                        del(doc.attachments[i])
                        doc.save()
                        if a['type'] in IMAGE_CONTENT_TYPES:
                            self.remove(a['thumb_src'])
                        self.remove(a['src'])
                        return self.json_response("Attachment succesfully removed", "OK")
                return self.json_response("Attachment not found", "ERROR")
            else:
                thumb = self.get_argument('thumb')
                if self.get_argument('attachment_type') in IMAGE_CONTENT_TYPES:
                    if thumb:
                        self.remove("tmp/" + sanitize_path(thumb))
                parts = thumb.split('.')
                path = '.'.join(parts[0:-2]) + '.' + parts[-1]
                self.remove("tmp/" + sanitize_path(path))
                return self.json_response(None, "OK")
        except Exception, e: 
            return self.json_response(e.__str__(), "ERROR")
        
        return self.json_response(None, "OK")
        
        