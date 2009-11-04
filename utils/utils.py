import hashlib
import logging
import os
from facebook import Facebook

def sanitize_path(path, real_prefix=None):
    path = os.path.basename(path)
    if real_prefix:
        return os.path.join(real_prefix, path)
    return path
    
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
    scale = max(width_scale, height_scale)
    return (int(width * scale), int(height * scale))

def create_thumbnails(path, sizes):
    from PIL import Image, ImageOps
    
    ext = path.split('.')[-1]
    path_without_ext = path.rstrip(ext)
    img = Image.open(path)
    size = img.size
    # sizes = [(20,20),], 
    for box_size, crop, suffix in sizes:
        """
        if crop:
            origin_x = (bw - w)/2
            origin_y = (bh - h)/2
            new_image = new_image.crop((origin_x, origin_y, bw, bh))
        """
        bw, bh = box_size
        logging.error("Resizing to %sx%s" % (bw, bh))
        
        if size[0] > bw or size[1] > bh:
            if crop:
                new_image = ImageOps.fit(img, (bw, bh))
            else:
                w, h = fit_bounding_box(bw, bh, size[0], size[1])
                new_image = img.resize((w, h), Image.BICUBIC)
            
            new_path = path_without_ext + "%s." % suffix + ext
            logging.error("Saving new resized image: " + new_path)
            new_image.save(new_path)

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