#!/usr/bin/env python
# coding=UTF-8
import os
import sys
import time
import logging
import StringIO
from os.path import abspath, dirname, join
# Hardwire in appengine modules to PYTHONPATH
# or use wrapper to do it more elegantly
appengine_dirs = ['C:/Program Files/Google/google_appengine','C:/Program Files/Google/google_appengine/lib','C:/Program Files/Google/google_appengine/lib/yaml','C:/Program Files/Google/google_appengine/lib/antlr3',]
sys.path.extend(appengine_dirs)
# Add current folder to sys.path, so we can import aecmd
#PROJECT_ROOT = abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
PROJECT_ROOT='E:/Software/code/pythonprj/geotwitter/'
sys.path.insert(0, join(PROJECT_ROOT, "common/appenginepatch"))
print join(PROJECT_ROOT, "common/appenginepatch")
import aecmd
aecmd.setup_project()
    
from appenginepatch.appenginepatcher.patch import patch_all, setup_logging
patch_all()
    
from django.conf import settings

import unittest,os,urllib
from django.test.client import Client
#import the stubs, i.e. the fake datastore, user and mail service and urlfetch
from google.appengine.api import apiproxy_stub_map
from google.appengine.api import datastore_file_stub
#from google.appengine.api import mail_stub
from google.appengine.api import urlfetch_stub
from google.appengine.api import user_service_stub
from google.appengine.api.memcache import memcache_stub

from django.utils.encoding import force_unicode,smart_str
from google.appengine.api import users
#from django.test import TestCase
from appenginepatcher import on_production_server

from google.appengine.ext.db.djangoforms import ModelForm
import unittest
from django.test.client import Client
from google.appengine.api import users
import logging 
if not on_production_server:
    from google.appengine.api.images import images_stub
client = Client()        
ROOT_PATH = os.path.dirname(__file__)
file=open(ROOT_PATH+'/daodao2.JPG')
print ROOT_PATH+'/daodao2.JPG'
part1 = open(ROOT_PATH+'/1daodao2.JPG',"w")
part1.write(file.read(3662))
response = client.post('http://localhost:8080/upload/album/', {'file': part1},HTTP_RANGE='bytes=%s-%s' % (0, 3662))
part1.close()

part2 = open(ROOT_PATH+'/temp1/daodao2.JPG',"w")
file.seek(3663)
part2.write(file.read())
response = client.post('http://localhost:8080/upload/album/', {'file': part2},HTTP_RANGE='bytes=%s-%s' % (3663, 5662))
part2.close()
#part1=StringIO.StringIO(file.read(3662))
#file.seek(3663)
#part2=StringIO.StringIO(file.read())
#print '---------------%s'%part1
#response = client.post('http://localhost:8080/upload/album/', {'file': part2},HTTP_RANGE='bytes=%s-%s' % (3663, 5661))
file.close()
#response = client.post('http://localhost:8080/upload/album/', {'file': file},HTTP_RANGE='bytes=%s-%s' % (0, 3662))
#response = client.post('http://localhost:8080/upload/album/', {'file': file},HTTP_RANGE='bytes=%s-%s' % (3663, 5662))
#file.close()
print 'done!'