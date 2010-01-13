Installation
------------

Install these apps:

* nginx+fair balancer module
* mongodb (1.2)
* redis (not yet used hehe)

and libs (using easy_install):

* markdown2 
* pymongo 
* mongokit 
* tornado
* web.py
* python-simplejson
* python-imaging
* python-twitter
* supervisor

After those apps and libs are installed, run these::

    INSTALLDIR/$ mkdir -p static/uploads/tmp
    INSTALLDIR/$ mkdir static/uploads/avatars
    INSTALLDIR/$ cp ~/avatar.png static/uploads/avatars #40x40px