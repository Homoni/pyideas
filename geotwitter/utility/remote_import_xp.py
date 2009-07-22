#!/usr/bin/env python
#
import os
import sys
import time
import logging
from os.path import abspath, dirname, join
# Hardwire in appengine modules to PYTHONPATH
# or use wrapper to do it more elegantly
appengine_dirs = ['C:/Program Files/Google/google_appengine','C:/Program Files/Google/google_appengine/lib','C:/Program Files/Google/google_appengine/lib/yaml','C:/Program Files/Google/google_appengine/lib/antlr3',]
sys.path.extend(appengine_dirs)
# Add current folder to sys.path, so we can import aecmd
#PROJECT_ROOT = abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
PROJECT_ROOT='E:/Software/code/pythonprj/my_cms/'
sys.path.insert(0, join(PROJECT_ROOT, "common/appenginepatch"))
print join(PROJECT_ROOT, "common/appenginepatch")
import aecmd
aecmd.setup_project()
    
from appenginepatch.appenginepatcher.patch import patch_all, setup_logging
patch_all()
    
from django.conf import settings



# Add your models to path
#my_root_dir = os.path.abspath(os.path.dirname(__file__))
my_root_dir =os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, my_root_dir)

from google.appengine.ext import db
from google.appengine.ext.remote_api import remote_api_stub
from google.appengine.api import apiproxy_stub_map
apiproxy_stub_map.apiproxy = apiproxy_stub_map.APIProxyStubMap()
from google.appengine.api.memcache import memcache_service_pb
from google.appengine.api.memcache import memcache_stub
from google.appengine.api import users
import getpass

from blog.models import *

APP_NAME = 'ihere'
os.environ['AUTH_DOMAIN'] = 'gmail.com'
os.environ['USER_EMAIL'] = 'evertobe@gmail.com'

def auth_func():
    return ('evertobe@gmail.com', 'woodspy2008')
#    return (raw_input('Username:'), getpass.getpass('Password:'))


#def get_key_from_time(self,strtime):
#    strtime=force_unicode(urllib.unquote(smart_str(strtime)))
#    timestamp = time.strptime(strtime,'%Y-%m-%d %H:%M:%S',)
#    return str(time.mktime(timestamp))[:10]
# Use local dev server by passing in as parameter:
# servername='localhost:8080'
# Otherwise, remote_api assumes you are targeting APP_NAME.appspot.com
remote_api_stub.ConfigureRemoteDatastore(
                                         APP_NAME,
                                         '/remote_api',
                                          auth_func,
                                          servername='ihere.appspot.com',
#                                          servername='localhost:8080',
                                        )

# Do stuff like your code was running on App Engine

#foos = Foo.all().fetch(100)
#for foo in foos:
# foo.note = 'Hello World!'
#db.puts(foos)
#timestamp=str(time.time())[:10]
#key_name='post_'+timestamp
#
#post=db.put(Post(
#                                  key_name=key_name,
##                                  parent=category,
##                                  category=category,
#                                  title ='title',
#                                  content ='body',
##                                  date=datetime.datetime.strptime(item['post_date_gmt'],'%Y-%m-%d %H:%M:%S',),
#                                  author =users.get_current_user(),
#                                  authorEmail =users.get_current_user().email(),
#                                  slug ='slug-test1',
##                                  tags=tags,
##                                  categories=categories,
#                                  isPublished=True,
#                                  entryType='post',
#                                ))
#post=Post.get_or_insert(
#                                  key_name=key_name,
##                                  parent=category,
##                                  category=category,
#                                  title ='title',
#                                  content ='body',
##                                  date=datetime.datetime.strptime(item['post_date_gmt'],'%Y-%m-%d %H:%M:%S',),
#                                  author =users.get_current_user(),
#                                  authorEmail =users.get_current_user().email(),
#                                  slug ='slug-test1',
##                                  tags=tags,
##                                  categories=categories,
#                                  isPublished=True,
#      
#logging.info(post)                          
#logging.info(db.get(post).title)
#tag =Tag(name='tagtagtag',slug='tagtagtag',).put()
#logging.info(tag)                          
#logging.info(db.get(tag).name)
apiproxy_stub_map.apiproxy.RegisterStub('memcache', memcache_stub.MemcacheServiceStub())


#-------------------------------------------------------------------
#from blog.models import *
#from blog.counter import *
#
#from google.appengine.ext import db
#
#posts=Post.all().fetch(1000)
#for post in posts: 
#    counter=Counter(str(post.key()))
##    counter.set_count(post.visitcount)
#    counter.count=post.visitcount
##    counter.increment(post.visitcount)
#    logging.info("counter.count=%s"%Counter(str(post.key())).count)
#-----------------------------------------------------------------------
#posts=Post.all().fetch(100)
#
#for post in posts:    
##    index = random.randint(1, Counter.NUM_SHARDS)
#    index=1
#    shard_key_name = 'Shard' + str(post.key()) + str(index)
#    counter=CounterShard.get_or_insert(key_name=shard_key_name,name=str(post.key()),count=post.visitcount)        
#    logging.info("counter.count=%s"%counter.count)

#from blog.models import *
#from google.appengine.ext import db
#clean_tags=Tag.all().fetch(1000)
#[cat.delete() for cat in clean_tags if not cat.entrycount]
#clean_cat=Category.all().fetch(1000)
#[cat.delete() for cat in clean_cat if not cat.entrycount]






from blog.models import *
from digg.models import *
from digg.digg import *
import datetime
from django.template.defaultfilters import striptags
import logging



posts=Post.all().fetch(1000)
diggs=[]
i=0
for post in posts:
    digg = Digg.get_or_insert(
            key_name='d'+post.title,                      
            link=post.get_permalink(),
            title=post.title,
            description=(striptags(post.content))[:320],
            date=post.date,
            category=post.category,
            weight=0.0,
            up=2*(post.commentcount)+post.get_cached_visitcount(),
            down=0,
    )
#        logging.info('digg=%s,%s,%s'%(digg.up,digg.down,digg.date))
    digg.up=2*(post.commentcount)+post.get_cached_visitcount()
    digg.weight=get_weight(digg.up,digg.down,digg.date)
    digg.put()
    i+=1
    logging.info(i)
    