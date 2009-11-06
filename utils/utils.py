import hashlib
import logging
import os
import shutil
from facebook import Facebook

ATTACHMENT_SEPARATOR = '$'
ATTACHMENT_FIELD_SEPARATOR = '#'

def sanitize_path(path, real_prefix=None):
    path = os.path.basename(path)
    if real_prefix:
        return os.path.join(real_prefix, path)
    return path

def move_attachments(basepath, attachments):
    def get_path(path):
        src = os.path.join(basepath, sanitize_path(path, "tmp"))
        dest = os.path.join(basepath, sanitize_path(path))
        logging.warning("Moving from %s to %s" % (src, dest))
        return (src, dest)
    
    for i, a in enumerate(attachments):
        if a['src'][0:4] == "tmp/":
            for size in ['.', '.s.', '.m.']:
                try:
                    shutil.move(*get_path(a['thumb_src'].replace('.s.', size)))
                except: pass
            a['src'] = a['src'].lstrip("tmp/")
            a['thumb_src'] = a['thumb_src'].lstrip("tmp/")
            attachments[i] = a
    return attachments
    
def parse_attachments(attachments, is_edit=False):
    _attachments = []
    for a in attachments.split(ATTACHMENT_SEPARATOR):
        a = a.split(ATTACHMENT_FIELD_SEPARATOR)
        # filetype#src#thumb_src#filename
        prefix = 'tmp' if not is_edit else ''
        src = sanitize_path(a[1], prefix)
        thumb_src = sanitize_path(a[2], prefix)
        attachment = dict(type=a[0], src=src, thumb_src=thumb_src, filename=a[3])
        _attachments.append(attachment)

    return _attachments
    
    
def get_attachment_with_filename(filename, attachments):
    for a in attachments:
        if a['filename'] == filename:
            return a
            
def unique_filename(parts):
    uf = "-".join(parts)
    return "%s-%s" % (parts[0], hashlib.sha1(uf).hexdigest())

def fit_bounding_box(box_width, box_height, width, height):
    """
    Returns a tuple (new_width, new_height) which has the property
    that it fits within box_width and box_height and has (close to)
    the same aspect ratio as the original size
    """
    
    width_scale = float(box_width) / float(width) 
    height_scale = float(box_height) / float (height)
    
    # max() -> fill aspect, min() -> fit aspect 
    scale = min(width_scale, height_scale)
    return (int(width * scale), int(height * scale))

def create_thumbnails(path, sizes):
    from PIL import Image, ImageOps
    
    ext = path.split('.')[-1]
    path_without_ext = path.rstrip(ext)
    img = Image.open(path)
    size = img.size
    # sizes = [(20,20),], 
    for box_size, crop, suffix in sizes:
        bw, bh = box_size
        logging.error("Resizing to %sx%s" % (bw, bh))
        
        if size[0] > bw or size[1] > bh:
            if crop:
                new_image = ImageOps.fit(img, (bw, bh), Image.ANTIALIAS)
            else:
                w, h = fit_bounding_box(bw, bh, size[0], size[1])
                logging.warning("No cropping, using fit: %s x %s" % (w, h))
                new_image = img.resize((w, h), Image.ANTIALIAS)
            if suffix:
                new_path = path_without_ext + "%s." % suffix + ext
            else:
                new_path = path_without_ext + ext
            logging.error("Saving new resized image: " + new_path)
            new_image.save(new_path, None, quality=85)

def save_user_upload(path, file_content):
    try:
        with open(path, mode="wb") as f:
            f.write(file_content)
            logging.warning("done writing %s" % path)
            return True
    except: pass
    return False

def fill_fb_data(api_key, secret_key, uid, fields, data):
    facebook = Facebook(api_key, secret_key)
    infos = facebook.users.getInfo(uid, fields)
    
    for key in infos.keys():
        data[key] = infos[key]
    return data

def extract_input_array(d, prefix):
    input = []
    extracted = []
    for key, value in d.iteritems():
        if key.startswith(prefix) and key.replace(prefix, ''):
            input.append(value)
            extracted.append(key)
    if extracted:
        for key in extracted:
            del(d[key])
    return input