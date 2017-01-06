#-*- coding: UTF-8 -*-

import urllib,urllib2,re,sys,cookielib,random

class Curl(object):
    source=""
    item=[]
    detail=[]
    conf=[]
    cookie=""
    proxy_list=""
    user_agent=""
    def __init__(self,cookie="",proxy_list="",user_agent=""):
        if(cookie != ""):
            self.cookie=cookielib.MozillaCookieJar(cookie)

        if (proxy_list!=""):
            self.proxy_list=proxy_list.split(",")


        if(user_agent != ""):
            self.user_agent=user_agent

    def __get(self,url):


        if(self.cookie==""):
            headers = {'User-Agent':self.user_agent}
            req = urllib2.Request(url,headers=headers)
            response = urllib2.urlopen(req)
            self.source = response.read()
        else:
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie))
            opener.addheaders=[("User-Agent",self.user_agent)]
            proxy = {'http':self.proxy_list[random.randint(0,len(self.proxy_list)-1)]}
            proxy_support = urllib2.ProxyHandler(proxy)
            urllib2.install_opener(urllib2.build_opener(proxy_support))
            result = opener.open(url)
            self.cookie.save(ignore_discard=True, ignore_expires=True)
            result = opener.open(url)
            self.source = result.read()

    def getItemList(self,url,rex):
        self.__get(url)
        r=re.compile(rex)
        item=r.findall(self.source)
        self.item.append(item)
        return item

    def getRex(self,str,rex,field=0,filters=[]):
        r=re.compile(rex)
        res=r.search(str)
        if(not res):
            return False
        res=res.group(field)
        if(len(filters)>0):
            for f in filters :
                res=re.compile(f,re.S).sub('',res)

        return res

    def getRexAll(self,str,rex,filters=[]):
        r=re.compile(rex)
        res=r.findall(str)
        if(len(filters)>0):
            len_list=len(res)
            for i in xrange(len_list):
                rs=res[i]

                for f in filters :
                    rs=re.compile(f,re.S).sub('',rs)
                res[i]=rs

        return res

    def getDetail(self,url):
        self.__get(url)
        return self.source