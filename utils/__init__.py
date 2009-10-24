
from facebook import Facebook
                
def fillin_fb_data(api_key, secret_key, uid, fields, data):
    facebook = Facebook(api_key, secret_key)
    infos = facebook.users.getInfo(uid, fields)
    
    for key in infos.keys():
        data[info] = infos[key]
    
