cookielibcookies = cookielib.CookieJar()
opener =urllib2.build_opener(
                             urllib2.HTTPCookieProcessor(cookies),
                             MultipartPostHandler.MultipartPostHandler)
params = { "username" :"bob", "password" : "riviera","file" : open("filename","rb") }
opener.open("http://wwww.bobsite.com/upload/", params)