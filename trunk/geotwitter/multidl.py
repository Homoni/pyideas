import sys, time
from httplib import *
from thread import *
from threading import *

parts=[]
thread_amount=5
PART_LENGTH=1024
lock=RLock()
class Part(Thread):
    def __init__(self, NO, resource):
        #for short only
        self.resource=resource
        r=resource
        self.NO=NO
        self.pos_start=int(r.content_length / thread_amount)*NO
        self.length=int(r.content_length / thread_amount)
        self.pos_end=self.pos_start+self.length
        self.downloaded=0
        self.speed=0
        parts.append(self)
        Thread.__init__(self, name='part_%s' % (NO))
    def run(self):
        http=HTTPConnection(self.resource.host, 80)
        headers={
           'Range':'bytes=%s-%s' % (self.pos_start, self.pos_end)
        };
        http.request('GET', self.resource.url, '', headers)
        resp=http.getresponse()
        while self.downloaded < self.length:
            self.ongetdata(resp.read(PART_LENGTH))
    def ongetdata(self, data):
        lock.acquire()
        self.resource.F.seek(self.downloaded+self.NO*self.length, 0)
        self.resource.F.write(data)
        lock.release()
        self.downloaded+=PART_LENGTH

class Resource:
    def __init__(self, url):
        #get host & url
        n=url.find('/', 7)
        self.host=url[7:n]
        self.url=url[n:]
        #get length
        http=HTTPConnection(self.host, 80)
        http.request('GET', self.url)
        resp=http.getresponse()
        self.content_length=int(resp.getheader('Content-Length'))
        #get filename & create a file before download
        n=url.rfind('/')
        self.filename=url[n+1:]
        print self.filename
        self.F=open(self.filename, 'wb+')
        print >> self.F, 'x'*self.content_length


def begin_download(url):
    #get the host and url
    r=Resource(url)
    for i in range(thread_amount):
        p=Part(i, r)
        p.start()

def part_begin_download(p, r):
     start_new_thread(x_part_begin_download, (p, r))

try:
     thread_amount=int(sys.argv[2])
except:
     thread_amount=1
begin_download(sys.argv[1])