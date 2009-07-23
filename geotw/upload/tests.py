# coding=UTF-8
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
from models import *
import urllib
import urllib2
import mimetools, mimetypes
import os, stat

if not on_production_server:
    from google.appengine.api.images import images_stub

ROOT_PATH = os.path.dirname(__file__)
#How I do gae test:-)
#1. 
#using gaeunit: http://code.google.com/p/gaeunit/
#and need to fix a bug of Django : Ticket #5176 
#http://code.djangoproject.com/ticket/5176

#2.
#using appengine_django_helper:
#http://code.google.com/intl/zh-CN/appengine/articles/appengine_helper_for_django.html
#http://appengineguy.com/2008/06/proper-unit-testing-of-app-enginedjango.html [GFW blocked]
#run from cmd: manage.py test upload
#Here i use the 2nd way:P
#enjoy 
class FileTest(unittest.TestCase):
    
    def setUp(self):        
        # Start with a fresh api proxy.
        apiproxy_stub_map.apiproxy = apiproxy_stub_map.APIProxyStubMap()

        # Use a fresh stub datastore.
        # From this point on in the tests, all calls to the Data Store, such as get and put,
        # will be to the temporary, in-memory datastore stub.         
        stub = datastore_file_stub.DatastoreFileStub(u'myTemporaryDataStorage', '/dev/null', '/dev/null')
        apiproxy_stub_map.apiproxy.RegisterStub('datastore_v3', stub)

        #User a memcache stub
        apiproxy_stub_map.apiproxy.RegisterStub('memcache', memcache_stub.MemcacheServiceStub())

        # Use a fresh stub UserService.
        apiproxy_stub_map.apiproxy.RegisterStub('user', user_service_stub.UserServiceStub())
        os.environ['AUTH_DOMAIN'] = 'gmail.com'
        os.environ['USER_EMAIL'] = 'myself@appengineguy.com' # set to '' for no logged in user 
        os.environ['SERVER_NAME'] = 'testserver' 
        os.environ['SERVER_PORT'] = '80' 
        os.environ['USER_IS_ADMIN'] = '1' #admin user 0 | 1
        os.environ['APPLICATION_ID'] = 'myTemporaryDataStorage' 
        
        # Use a fresh urlfetch stub.
        apiproxy_stub_map.apiproxy.RegisterStub('urlfetch', urlfetch_stub.URLFetchServiceStub())

        # Use a fresh images stub.
        
        if not on_production_server:
            apiproxy_stub_map.apiproxy.RegisterStub('images', images_stub.ImagesServiceStub())



        # Use a fresh mail stub.
#        apiproxy_stub_map.apiproxy.RegisterStub('mail', mail_stub.MailServiceStub()) 

        # Every test needs a client.
        self.client = Client()        

    def test_add_file(self):
        file=open(ROOT_PATH+'/testtxt.txt')
        
        response = self.client.post('/upload/album/', {'file': file})
        file.close()
        self.failUnlessEqual(response.status_code, 302)
        
        returnResponse = self.client.get('/upload/album/')
        self.assertTrue('testtxt.txt' in returnResponse.content)
        userFile=UserFile.all().filter("name =","testtxt.txt").get()
        self.assertTrue(userFile is not None)
    
    def test_download_file(self):    
        self.test_add_file()
        userFile=UserFile.all().filter("name =","testtxt.txt").get()
        bin=userFile.filebin_set.get()
        returnResponse = self.client.get('/upload/album/download/%s'%userFile.key())
        self.assertTrue(returnResponse['Content-Type']=='application/octet-stream')
        self.assertTrue(returnResponse.content==bin.bin)
        
    def test_show_picture(self):    
        file=open(ROOT_PATH+'/daodao2.JPG')
        
        response = self.client.post('/upload/album/', {'file': file})
        file.close()
        self.failUnlessEqual(response.status_code, 302)
        
        returnResponse = self.client.get('/upload/album/')
        self.assertTrue('daodao2.JPG' in returnResponse.content)
        userFile=UserFile.all().filter("name =","daodao2.JPG").get()
        self.assertTrue(userFile is not None)
        
        self.test_add_file()
        userFile=UserFile.all().filter("name =","daodao2.JPG").get()
        bin=userFile.filebin_set.get()
        returnResponse = self.client.get('/upload/album/%s'%userFile.key())
        self.assertTrue(returnResponse['Content-Type']=='image/JPEG')
        self.assertTrue(returnResponse.content==bin.bin)
        
    def test_delete_file(self):
        self.test_add_file()
        userFile=UserFile.all().filter("name =","testtxt.txt").get()
        fileBinKey=userFile.filebin_set.get().key()
        response = self.client.get('/upload/album/delete/%s'%userFile.key())      
        self.assertTrue(UserFile.all().filter("name =",'testtxt.txt').get() is None)
        self.assertTrue(FileBin.get(fileBinKey) is None)
        returnResponse = self.client.get('/upload/album/')
        self.assertTrue('testtxt.txt' not in returnResponse.content)
     
    def multipart_encode(self,vars, files, boundary = None, buffer = None,pos_start=0,pos_end=0):
        if boundary is None:
            boundary = mimetools.choose_boundary()
        if buffer is None:
            buffer = ''
        for(key, value) in vars:
            buffer += '--%s\r\n' % boundary
            buffer += 'Content-Disposition: form-data; name="%s"' % key
            buffer += '\r\n\r\n' + value + '\r\n'
        for(key, fd) in files:
            file_size = os.fstat(fd.fileno())[stat.ST_SIZE]
            filename = os.path.basename(fd.name)
            contenttype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
            buffer += '--%s\r\n' % boundary
            buffer += 'Content-Disposition: form-data; name="%s"; filename="%s"\r\n' % (key, filename)
            buffer += 'Content-Type: %s\r\n' % contenttype
            # buffer += 'Content-Length: %s\r\n' % file_size
            if pos_start:
                fd.seek(pos_start)
            else:
                fd.seek(0)
            if pos_end>pos_start:
                buffer += '\r\n' + fd.read(pos_end-pos_start) + '\r\n'
            else:
                buffer += '\r\n' + fd.read() + '\r\n'
        buffer += '--%s--\r\n\r\n' % boundary
        return boundary, buffer
        
    def test_part_upload(self):
        file=open(ROOT_PATH+'/daodao2.JPG',"rb")
#        file.seek(0,0)
#        part1=file.read(3662)
#        file.seek(3662,0)
#        part2=file.read()
        size=os.path.getsize(ROOT_PATH+'/daodao2.JPG')
        logging.info("-------------------------%s"%size)
        
        boundary, part1=self.multipart_encode(vars=[('size',str(size)),],files=[('file',file),],pos_start=0,pos_end=3662)
        contenttype = 'multipart/form-data; boundary=%s' % boundary
        
        
        logging.info('------len(part1)=%s'%len(part1))
        response = self.client.post(path='/upload/album/part_upload/',content_type=contenttype, data={'file': part1},HTTP_RANGE='bytes=%s-%s' % (0, 3662))
        
        boundary2, part2=self.multipart_encode(vars={'size':size},files={'file':file},pos_start=0,pos_end=3662)
        contenttype2 = 'multipart/form-data; boundary=%s' % boundary2
        logging.info('------len(part2)=%s'%len(part2))
        response = self.client.post(path='/upload/album/part_upload/',content_type=contenttype2, data={'file': part2},HTTP_RANGE='bytes=%s-%s' % (3662, size))
        
#        self.failUnlessEqual(response.status_code, 302)
        
        returnResponse = self.client.get('/upload/album/')
#        self.assertTrue('daodao2.JPG' in returnResponse.content)
        userFile=UserFile.all().filter("name =","daodao2.JPG").get()
        self.assertTrue(userFile is not None)
        self.assertTrue(userFile.size==size)
        file.seek(0,0)
        logging.info('------len(bin)=%s'%len(userFile.filebin_set.get().bin))
        logging.info('------len(file)=%s'%len(file.read()))
        
        self.assertTrue(userFile.filebin_set.get().bin==file.read())
        file.close()

    def tearDown(self):
        #For that we are using a temporary datastore stub located in the memory,we don't have to clean up.
        pass
        