import PartUploadHandler, urllib2, cookielib,os

cookies = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookies),PartUploadHandler.MultipartPostHandler)
size=os.path.getsize('hc20080828_009.jpg')
params = { "size" : str(size), "password" : "riviera", "file" : open("hc20080828_009.jpg", "rb") }
#headers = { 'User-Agent' : user_agent }
#data = urllib.urlencode(values)
url='http://ideasyourlife.appspot.com/upload/album/part_upload/'
#url='http://localhost:8000/upload/album/part_upload/'

req1 = urllib2.Request(url, headers={'Range':'bytes=%s-%s' % (0, 3000)})
opener.open(req1, data=params)

req3 = urllib2.Request(url, headers={'Range':'bytes=%s-%s' % (7001, size)})
opener.open(req3, data=params)

req2 = urllib2.Request(url, headers={'Range':'bytes=%s-%s' % (3001, 7000)})
opener.open(req2, data=params)

