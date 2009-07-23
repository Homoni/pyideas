# coding=UTF-8
from django.shortcuts import render_to_response
from django.forms import Textarea,FileField,CharField,Form,ModelForm,EmailField
from django.http import HttpResponseRedirect, HttpResponseForbidden,HttpResponseNotFound,HttpResponse
from upload.models import UserFile,FileBin
import os,logging,urllib
from django.utils.encoding import force_unicode,smart_str
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import memcache
from django.core.urlresolvers import reverse
from utility.authorized import admin_required,login_required
from django.template import RequestContext
from django.views.decorators.vary import vary_on_headers
from django.views.decorators.cache import cache_control,cache_page
from django.core.mail import send_mail
from google.appengine.api import images
from ragendja.dbutils import get_object_or_404
from django.contrib.sites.models import Site
from mimetypes import guess_type
FILE_MAX=100
import sys,re
from django.conf import settings
import StringIO

class FileForm(ModelForm):
    file = FileField()    
    class Meta:
        model = UserFile
        exclude = ("creationDate",'mimetype','size','author','name','comment','icon',)

class EmailForm(Form):
    email=EmailField(required=True)

def part_upload(request):
    if request.method == 'POST':
        if 'file' in request.FILES:
            file = request.FILES['file']
            userfile = UserFile.get_or_insert(  
                                    keyname=key,
                                    mimetype=request.META['CONTENT_TYPE'],
                                    author = users.get_current_user(),
                                    size = file.size,
                                    name=file.name,
                                    comment=request.REQUEST.get('comment',''))
            filebin=file.filebin_set.get()
            if filebin is None:
                emptyfile = StringIO.StringIO()
                emptyfile.truncate(file.size)
                if request.META.has_key("Range"):
                    pos_start,pos_end=getRange(request.META["Range"])
                    emptyfile.seek(pos_start, 0)
                    emptyfile.write(db.Blob(file.read()))
                filebin = FileBin(userfile=userfile, bin=db.Blob(emptyfile.read()))
                emptyfile.close()
            else:
                if request.META.has_key("Range"):
                    pos_start,pos_end=getRange(request.META["Range"])
                    s = StringIO.StringIO(filebin.bin)
                    s.seek(pos_start, 0)
                    s.write(file)
                    s.seek(0)
                    filebin.bin=db.Blob(s.read())
                    filebin.put()
                    s.close()
                else:
                    return HttpResponse("err")
#                self.resource.F.seek(self.downloaded+self.NO*self.length, 0)
#                self.resource.F.write(data)
#                headers={
#                   'Range':'bytes=%s-%s' % (self.pos_start, self.pos_end)
#                }
            
    return HttpResponse("done! part%s"%partNO)

def getRange(rangestr):
    regex='\d+'
    reobj = re.compile(regex)
    result = reobj.findall(rangestr)
    return result[0],result[1]
                   

@cache_control(must_revalidate=True)
@vary_on_headers('User-Agent','Cookie')
def albumentry(request):
    if request.method == 'POST':
        if 'file' in request.FILES:
            file = request.FILES['file']
            userfile = UserFile(  mimetype=request.META['CONTENT_TYPE'],
                                    author = users.get_current_user(),
                                    size = file.size,
                                    name=file.name,
                                    comment=request.REQUEST.get('comment',''))
            bin=file.read()
            try:
                userfile.icon=images.resize(bin, width=60)
            except:
                pass
                
            userfile.save() 
            filebin = FileBin(userfile=userfile, bin=db.Blob(bin))
            filebin.save()
            file.close()
            if UserFile.all().count() > FILE_MAX:
                oldest_file = UserFile.all().order('-creationDate').get()
                oldest_file.delete()
            #flush cache in order to update the file list
            memcache.flush_all()
            return HttpResponseRedirect(reverse(albumentry))
        else:
            return HttpResponseRedirect(reverse(albumentry))

    else:
        filelist = UserFile.all().order('-creationDate').fetch(FILE_MAX)
        user = users.get_current_user()
        if user:
            sign_link = '<a href="%s">Logout</a>' % users.create_logout_url(reverse(albumentry))
        else:
            sign_link = '<a href="%s">Login</a>' % users.create_login_url(reverse(albumentry))
        displayFile=None
        if 'key' in request.REQUEST:
            displayFile=get_object_or_404(UserFile,request.REQUEST['key'])     
            
        email_form=EmailForm()       
        template_values = {
            'displayFile':displayFile,               
#            'user': user,
            'sign_link': sign_link,
            'filelist': filelist,
            'form':FileForm(),
            'email_form':email_form,
        }
        return render_to_response('upload/show_albumentry.html',template_values,context_instance=RequestContext(request))

def outer_heaven(request):
    filelist=UserFile.all().order('-creationDate').fetch(FILE_MAX)
    for file in filelist:
        if not file.icon:
            try :
                filebin=file.filebin_set.get()
                file.icon=images.resize(filebin.bin, width=60)
                file.put()
            except:
                pass
    
    return render_to_response('upload/OuterHeaven.html',locals(),context_instance=RequestContext(request))

    
def show_albumentry(request,key):
    userfile = get_object_or_404(UserFile,key)
#    if userfile.icon:
#        return show_icon(request,key)
    
    filebin=userfile.filebin_set.get()
    if not userfile or not filebin:        
        return HttpResponseNotFound()
    return HttpResponse(filebin.bin,'image/JPEG')      

def show_icon(request,key):
    userfile = get_object_or_404(UserFile,key)
    if userfile.icon:
        return HttpResponse(userfile.icon,'image/JPEG')
    return HttpResponseNotFound()

def download_albumentry(request,key):
    userfile = get_object_or_404(UserFile,key)
    filebin=userfile.filebin_set.get()
    if not userfile or not filebin:        
        return HttpResponseNotFound()
    response=HttpResponse(filebin.bin,content_type=guess_type(userfile.name)[0] or 'application/octet-stream')   

    #dealing with unicode :( Can't convert unicode to ascii when decode. 
    #If any solutions, please mail to me: lincong.javatech@gmail.com 
    if isinstance(userfile.name, unicode):
        response['Content-Type'] = 'application/octet-stream'
        encoding=sys.getdefaultencoding() 
        try :
            name=force_unicode(urllib.unquote(smart_str(userfile.name)))
            str=name.decode(encoding)
            filename=str.encode(encoding, 'replace')
            response['Content-Disposition'] = 'attachment; filename="%s"'%filename
        except UnicodeEncodeError:
            filename=userfile.name
            response['Content-Type']=userfile.mimetype 
    else:
        filename=userfile.name
        response['Content-Type']=userfile.mimetype 
    return response

@login_required
def delete_albumentry(request,key):
    userfile = get_object_or_404(UserFile,key)
    if userfile.author==users.get_current_user() or users.is_current_user_admin():
        userfile.delete()
        #flush cache in order to update the file list
        memcache.flush_all()
        return HttpResponseRedirect(reverse(albumentry))
    else:
        return HttpResponseForbidden()



def share(request,key):
    form=EmailForm(request.POST)
    if form.is_valid():
        BASE_URL='http://%s' % (Site.objects.get_current().domain)
        email=form.cleaned_data['email']
        show_url = BASE_URL+reverse(albumentry)+'?key=%s'%key
        download_url=BASE_URL+reverse(download_albumentry, args=[key,])
        sender_address = settings.SERVER_EMAIL
        subject = "Your friend wants to share a picture :-)"
        body = """
                    Your friend wants to share a picture with you.
                    You can watch it at %s, 
                    or you can download it with the link:%s
                    
                """ % (show_url,download_url)
        
        send_mail(subject, body, sender_address, [email,], fail_silently=False)

    return HttpResponseRedirect(reverse(albumentry)+'?key=%s'%key)
