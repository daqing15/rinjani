#!/usr/bin/python -W ignore::DeprecationWarning

import sys
import os
DIR = os.path.abspath(os.path.dirname(__file__))
PARENT_DIR = os.path.dirname(DIR)
sys.path = [DIR, PARENT_DIR] + sys.path

from datetime import datetime
from supervisor.childutils import listener, get_headers, eventdata, getRPCInterface
import twitter

from settings import TWITTER_USER, TWITTER_PASSWORD

def send_twitter(tw):
    api = twitter.Api(username=TWITTER_USER, password=TWITTER_PASSWORD)
    api.PostUpdate(tw)

def main():
    rpci = getRPCInterface(os.environ)

    while True:
        h, p = listener.wait()
        if not h['eventname'] == 'PROCESS_STATE_EXITED':
            listener.ok()
            continue

        ph, _pd = eventdata(p + '\n')
        if ph['processname'] == 'mongodb':
            if int(ph['expected']):
                listener.ok()
                continue

            listener.send("MONGODB HAS BEEN RESTARTED. SO WILL APP!")
            rpci.supervisor.stopProcessGroup('app')
            rpci.supervisor.startProcessGroup('app', True)
            listener.ok()
            now = datetime.now()
            send_twitter("[FATAL] %s - mongodb has been restarted" % now.isoformat())
            return

        listener.ok()

if __name__ == '__main__':
    main()

