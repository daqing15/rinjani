#
# Copyright 2009 rinjani team
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import os
import subprocess
import shutil
import tempfile
from mimetypes import guess_extension
from main import BaseHandler, authenticated
from rinjani.utils import unique_filename, create_thumbnails, sanitize_path
from rinjani.string import slugify
import models

from settings import PIC_SIZES,IMAGE_CONTENT_TYPES, ALLOWED_CONTENT_TYPES
            
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
        doc_type = self.get_argument('content_type', 'article')
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
                self.log("thumb is " + thumb_src) 
            else:
                thumb_src = 'attachment.png'
            
            no += 1
            filename = slugify(f['filename'])
            
            """ no#filetype#src#thumb_src#filename"""
            
            # save to doc
            if not is_new_doc:
                type = self.get_argument('type', None).title()
                if type:
                    cls = getattr(models, type, None)
                    if cls:
                        try:
                            id = 'slug' if cls.structure.has_key('slug') else 'username'
                            doc = cls.one({id: self.get_argument('slug')} )
                            doc['attachments'] += [dict(type=unicode(file_type), src=unicode(src), thumb_src=unicode(thumb_src, 'utf-8'), filename=unicode(filename, 'utf-8'))]
                            doc.save()
                        except Exception, e:
                            return self.json_response("Failed updating doc: " + e.__str__(), "ERROR")
                else:
                    return self.json_response("Unknown document type", "ERROR")
                
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
        self.log("removing %s" % path)
        try:
            os.remove(path)
        except: pass
        
    def post(self):
        try:
            self.log(self.get_arguments())
            
            filename = self.get_argument('filename')
            slug = self.get_argument('slug', None)
            
            thumb = False
            if slug:
                type = self.get_argument('type').title()
                cls = getattr(models, type, None)
                id = 'slug' if cls.structure.has_key('slug') else 'username'
                doc = cls.one({id: slug} )
                
                for i, a in enumerate(doc.attachments):
                    if a['filename'] ==  filename:
                        del(doc.attachments[i])
                        doc.save()
                        if a['type'] in IMAGE_CONTENT_TYPES:
                            for size in ['.', '.s.', '.m.']:
                                self.remove(a['thumb_src'].replace('.s.', size))
                        else:
                            self.remove(a['src'])
                        return self.json_response("Attachment succesfully removed", "OK")
                return self.json_response("Attachment not found", "ERROR")
            else:
                thumb = self.get_argument('thumb')
                if thumb and self.get_argument('attachment_type') in IMAGE_CONTENT_TYPES:
                    for size in ['.', '.s.', '.m.']:
                        self.remove("tmp/" + sanitize_path(thumb).replace('.s.', size))
                return self.json_response(None, "OK")
        except Exception, e: 
            return self.json_response(e.__str__(), "ERROR")
        
        return self.json_response(None, "OK")
        
        