from fabric.api import env, local, run

def _setup():
    env.hosts = ['user@obscurite.ind.ws']
    env.mongo = '/opt/devel/mongodb/bin/mongo'

    env.localdir = '/rinjani/app'
    env.remotebase = '/rinjani'
    env.remotedir = '%s/app' % env.remotebase
    env.remotedbdir = '%s/var/db' % env.remotebase
    env.envi = 'production'
    env.db = 'peduli'

_setup()

def stat():
    run("uptime; free; supervisorctl status; ps xwfv -u user")
    
def tag():
    run("%s %s %s/bin/tag-count.js %s/bin/tag-combination-count.js" \
        % (env.mongo, env.db, env.remotedir, env.remotedir))

def rebuilddb():
    run("supervisorctl stop all && rm -rf %s && mkdir %s && supervisorctl start all" \
        % (env.remotedbdir, env.remotedbdir))
    run("%s %s %s/bin/dummydata.js" % (env.mongo, env.db, env.remotedir))
    tag()
    restart_app()

def restart_supervisor():
    run("killall supervisord && sleep 2 && supervisord")

def restart_app():
    run("supervisorctl restart 'app:*'")

def backup():
    run("tar -czf /rinjani/var/backup/%s_`date +%%y_%%m_%%d_%%H`.tar.gz %s" \
            % (env.envi, env.remotedir))

def mergecss():
    local("cd %s/static/css && cat app.css mod.css uicomponents.css > /tmp/rinjani.css && yuic /tmp/peduli.css > %s/static/css/rinjani.css" %(env.localdir, env.localdir) )

def _sync(path):
    local("rsync -rzvh %s/%s %s:%s/%s" % (env.localdir, path, env.hosts[0], env.remotedir, path))

def synctemplates():
    _sync('templates/')

def synclib():
    _sync('lib/')

def sync():
    _sync('')

