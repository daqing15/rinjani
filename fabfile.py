from fabric.api import *

def setup():
    env.hosts = ['user@obscurite.ind.ws']
    env.mongo = '/opt/devel/mongodb/bin/mongo'

    env.localdir = '/rinjani/app'
    env.remotebase = '/rinjani'
    env.remotedir = '%s/app' % env.remotebase
    env.remotedbdir = '%s/var/db' % env.remotebase
    env.envi = 'production'
    env.db = 'peduli'

setup()

def tag():
    run("%s %s %s/bin/mr-tag.js" % (env.mongo, env.db, env.remotedir))

def rebuilddb():
    run("supervisorctl stop all && rm -rf %s && mkdir %s" % (env.remotedbdir, env.remotedbdir))
    run("supervisorctl start all && /opt/devel/mongodb/bin/mongo %s %s/bin/dummydata.js" % (env.db, env.remotedir))
    tag()

def restart_supervisor():
    run("killall supervisord && supervisord")


def backup():
    run("tar -czf /rinjani/var/backup/%s_`date +%%y_%%m_%%d_%%H`.tar.gz %s" % (env.envi, env.remotedir))

def sync(path):
    local("rsync -rzvh %s/%s %s:%s/%s" % (env.localdir, path, env.hosts[0], env.remotedir, path))

def synctemplates():
    sync('templates/')

def synclib():
    sync('lib/')

def stat():
    run("uptime; free; supervisorctl status")
