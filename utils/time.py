from datetime import datetime

def timesince(time=False, now=False):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    
    Modified from http://evaisse.com/post/93417709/python-pretty-date-function
    """
    if not now:
        now = datetime.now()
        
    if type(time) is int:
        diff = now - datetime.fromtimestamp(time)
    elif type(time) is str:
        diff = now - datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
    elif time is False:
        diff = now - now
    else:
        diff = now - time
        
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(second_diff) + " seconds ago"
        if second_diff < 120:
            return  "a minute ago"
        if second_diff < 3600:
            return str( second_diff / 60 ) + " minutes ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str( second_diff / 3600 ) + " hours ago"
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(day_diff) + " days ago"
    if day_diff < 31:
        return str(day_diff/7) + " weeks ago"
    if day_diff < 365:
        return str(day_diff/30) + " months ago"
    return str(day_diff/365) + " years ago"

# django.template.defaultfilters
def timeuntil(dt):
    """Formats a date as the time until that date (i.e. "4 days, 6 hours")."""
    if not dt:
        return u''
    try:
        now = datetime.datetime.now()
        return timesince(now, dt)
    except (ValueError, TypeError):
        return u''