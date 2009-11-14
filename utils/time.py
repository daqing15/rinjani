from datetime import datetime
import pytz

def date_to_striso(dt, sep='/'):
    return sep.join(dt.isoformat()[0:10].split('-'))

def striso_to_date(s, sep="/"):
    return datetime(*[int(z) for z in s.split(sep)])

def timesince(time=False, now=False):
    """
    Get a *UTC* datetime object and return a pretty string 
    like 'an hour ago', 'Yesterday', '3 months ago', 'just now', etc
    
    Modified from http://evaisse.com/post/93417709/python-pretty-date-function
    """
    if not now:
        now = datetime.utcnow()
        
    if type(time) is int:
        diff = now - datetime.fromtimestamp(time, tzinfo=pytz.utc)
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
        now = datetime.datetime.utcnow()
        return timesince(now, dt)
    except (ValueError, TypeError):
        return u''