import PartUploadHandler, urllib2, cookielib

cookies = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookies),PartUploadHandler.MultipartPostHandler)
params = { "username" : "bob", "password" : "riviera", "file" : open("daodao2.JPG", "rb") }
opener.open("http://localhost:8000/upload/album/", params)