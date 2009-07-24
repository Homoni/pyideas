import PartUploadHandler, urllib2, cookielib,os

cookies = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookies),PartUploadHandler.MultipartPostHandler)
params = { "username" : "bob", "password" : "riviera", "file" : open("hc20080828_009.jpg", "rb") }
#headers = { 'User-Agent' : user_agent }
#data = urllib.urlencode(values)
size=os.path.getsize('hc20080828_009.jpg')
req1 = urllib2.Request("http://localhost:8000/upload/album/part_upload/", headers={'Range':'bytes=%s-%s' % (0, 3000)})
opener.open(req1, data=params)

req2 = urllib2.Request("http://localhost:8000/upload/album/part_upload/", headers={'Range':'bytes=%s-%s' % (3001, size)})
opener.open(req2, data=params)