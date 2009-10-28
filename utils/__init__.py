
from facebook import Facebook
                
def fillin_fb_data(api_key, secret_key, uid, fields, data):
    facebook = Facebook(api_key, secret_key)
    infos = facebook.users.getInfo(uid, fields)
    
    for key in infos.keys():
        data[key] = infos[key]
    

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