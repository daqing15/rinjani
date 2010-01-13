from fabric.api import env, local, run

def _setup():
    env.hosts = ['ron@obscurite.ind.ws']
    env.mongo = '/opt/devel/mongodb/bin/mongo'

    env.localdir = '/rinjani/app'
    env.localbase = '/rinjani'
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

def generate_doc():
    import main
    import rinjani.indexing
    rinjani.indexing.generate_doc_content()
    
def generate_index():
    import main
    import rinjani.indexing
    rinjani.indexing.index.rebuild_index()
    
def rebuilddb():
    run("supervisorctl stop all && rm -rf %s && mkdir %s && supervisorctl start all" \
        % (env.remotedbdir, env.remotedbdir))
    run("%s %s %s/bin/dummydata.js" % (env.mongo, env.db, env.remotedir))
    tag()
    restart_app()

def rebuild_localdb():
    local("supervisorctl stop mongodb")
    local("rm -rf %s/var/db" % env.localbase)
    local("mkdir %s/var/db" % env.localbase)
    local("supervisorctl start mongodb")
    local("%s peduli %s/bin/dummydata.js %s/bin/tag-count.js %s/bin/tag-combination-count.js" \
          % (env.mongo, env.localdir, env.localdir, env.localdir)
          )

def rebuilddummy():
    run("%s/bin/dummydata.py" % env.remotedir)
    
def restart_supervisor():
    run("killall supervisord && sleep 2 && supervisord")

def restart_app():
    run("supervisorctl restart 'app:*'")

def backup():
    run("tar -czf /rinjani/var/backup/%s_`date +%%y_%%m_%%d_%%H`.tar.gz %s" \
            % (env.envi, env.remotedir))

def mergecss():
    local("cd %s/static/css && cat app.css mod.css uicomponents.css > /tmp/rinjani.css && yuic /tmp/rinjani.css > %s/static/css/rinjani.css" %(env.localdir, env.localdir) )

def _sync(path):
    local("rsync -rzvh %s/%s %s:%s/%s" % (env.localdir, path, env.hosts[0], env.remotedir, path))

def synctemplates():
    _sync('templates/')

def synclib():
    _sync('lib/')

def sync():
    mergecss()
    _sync('')

