import sys

# taken from django source code
def get_mod_handler(callback):
    # Converts 'handlers.stories.StoryListHandler' to
    # ['handlers.stories', 'StoryListHandler']
    try:
        dot = callback.rindex('.')
    except ValueError:
        return callback, ''
    return callback[:dot], callback[dot+1:]

def import_module(mod_name, class_name):
    __import__(mod_name, {}, {}, [class_name])
    #print sys.modules[mod_name]
    return getattr(sys.modules[mod_name], class_name)
