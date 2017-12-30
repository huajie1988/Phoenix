#-*- coding: UTF-8 -*-

import ConfigParser,sys,threading,time,os,json,random
from Queue import Queue
from Lib.curl import Curl
from Lib.mysql import Mysql
from Lib.learn import Learn

class MovieLearn:
    conf=[]
    lock=""
    share_queue = Queue()
    m=''
    l=''
    def __init__(self):
        cf = ConfigParser.ConfigParser()
        cf.read(os.path.dirname(os.path.realpath(__file__))+"/Lib/conf")
        self.conf=cf
        db=self.conf.options("db")
        db_info={}
        for d in db:
            db_info[d]=self.conf.get("db",d)
        self.m=Mysql(db_info)
        self.l=Learn()

    def run(self):
        # try:

            params=""
            for i in range(1, len(sys.argv)):
                params=sys.argv[i]
            params=params.strip('-')
            if params=='cs':
                self.getComingSoon()
            elif params=='it':
                self.getInTheaters()
            elif params=='ugs':
                self.updateGuessScore()
            elif params=='p':
                url=raw_input("please input a movie url by douban:")
                score = self.prediction(url)
                som=self.m.table('score')
                rt=som.find(where="source_url='"+url+"'")
                if rt:            
                    sod={"score_guess":score}
                    som.save(sod,where="id='"+str(rt['id'])+"'")                
            elif params=='up':
                self.update()
            elif params=='upsi':
                self.updatePassScoreInfo()
            elif params=='test':
                self.test()
        # except Exception as e:
        #     print("Unexpected Error: {}".format(e))
        # print self.__get("https://movie.douban.com/tag/中国电影?&type=T&start=0")
        # self.l.calc([.719,.8298,.8376,.698],9.5)
        # self.update()
        # self.getScore([.626484668109668,.476830211455211,.608571428571429,.625])
        # self.getScore([6.43698092742844/10,8.66153846153846/10,.88,.88])
        # self.updateGuessScore()
        # url=raw_input("please input a movie url by douban:")
        # print self.prediction(url)
        # print self.calcPrediction(6.94391851408029,6.81666666666667,7,7);
        # self.getComingSoon()

    def test(self):
        print "test"

    def calcPrediction(self,type_avg,actor_avg,director_avg,screenwriter_avg):
        tm=self.m.table('type')
        t=tm.find(where="1=1",fields="AVG(score) avg")
        am=self.m.table('actor')
        a=am.find(where="1=1",fields="AVG(score) avg")
        dm=self.m.table('director')
        d=dm.find(where="1=1",fields="AVG(score) avg")
        scm=self.m.table('screenwriter')
        sc=scm.find(where="1=1",fields="AVG(score) avg")
        type_avg= type_avg if type_avg>0 else t['avg']
        actor_avg=actor_avg if actor_avg>0 else a['avg']
        director_avg=director_avg if director_avg>0 else d['avg']
        screenwriter_avg=screenwriter_avg if screenwriter_avg>0 else sc['avg']
        th=self.getTheta()
        avg_score=self.getGuessScore([type_avg/10.0,actor_avg/10.0,director_avg/10.0,screenwriter_avg/10.0],th)
        k,c=self.getGuessTheta()
        val=k*avg_score+c
        if val>10:
            val=avg_score
        return val

    def getComingSoon(self):
        c=Curl(cookie=self.conf.get("curl", "cookie"),proxy_list=self.conf.get("curl", "proxy_list"),user_agent=self.conf.get("curl", "user_agent"))
        csjson=c.getDetail("https://api.douban.com/v2/movie/coming_soon")
        cslist=json.loads(csjson)
        for cs in cslist['subjects']:
            scoend=random.randint(0,99)
            print "scoend:",scoend
            print "st1:", time.time()
            time.sleep(scoend)
            print "st2:", time.time()         
            score=self.prediction(cs['alt'])
            som=self.m.table('score')
            rt=som.find(where="source_url='"+cs['alt']+"'")
            if not rt:
                continue            
            sod={"score_guess":score}
            som.save(sod,where="id='"+str(rt['id'])+"'")


    def getInTheaters(self):
        c=Curl(cookie=self.conf.get("curl", "cookie"),proxy_list=self.conf.get("curl", "proxy_list"),user_agent=self.conf.get("curl", "user_agent"))
        csjson=c.getDetail("https://api.douban.com/v2/movie/in_theaters")
        cslist=json.loads(csjson)
        for cs in cslist['subjects']:
            som=self.m.table('score')
            rt=som.find(where="source_url='"+cs['alt']+"'")
            if not rt:
                continue
            sod={"score_real":cs['rating']['average']}
            som.save(sod,where="id='"+str(rt['id'])+"'")
            if float(cs['rating']['average'])>0:
                theta=self.l.calc([rt['type_avg']/10,rt['actor_avg']/10,rt['director_avg']/10,rt['screenwriter_avg']/10],float(cs['rating']['average']))
                thm=self.m.table('theta')
                thm.add({"theta1":theta[0],"theta2":theta[1],"theta3":theta[2],"theta4":theta[3],"theta5":theta[4]})

            
    def updatePassScoreInfo(self):
        sm=self.m.table('score')
        score=sm.findAll(where="1=1 AND complete = 0", order="id ASC Limit 10")
        for s in score:
            self.__updatePassScoreInfo(s['source_url'],s['id'])
            
    def __updatePassScoreInfo(self,url,id):
        scoend=random.randint(0,99)
        print url
        print "scoend:",scoend
        print "st1:", time.time()
        time.sleep(scoend)
        print "st2:", time.time()


        self.lock = threading.Lock()
        c=Curl(cookie=self.conf.get("curl", "cookie"),proxy_list=self.conf.get("curl", "proxy_list"),user_agent=self.conf.get("curl", "user_agent"))

        d={}
        d["detail_url"]=url
        detail_html=c.getDetail(url)
        filter=self.conf.get("rex", "detail_title_filter_rex").split("&,&")
        
        info=c.getRex(detail_html,self.conf.get("rex", "detail_info_rex"))
        # info_item=c.getRexAll(info,self.conf.get("rex", "detail_info_item_rex"),filter)

        director = c.getRex(info,self.conf.get("rex", "detail_info_item_director_rex"))
        d['director']=c.getRex(director,self.conf.get("rex", "detail_info_item_split_rex"),1,filter).split('/') if  director else ''
        screenwriter = c.getRex(info,self.conf.get("rex", "detail_info_item_screenwriter_rex"))
        d['screenwriter']=c.getRex(screenwriter,self.conf.get("rex", "detail_info_item_split_rex"),1,filter).split('/') if  screenwriter else ''
        actor = c.getRex(info,self.conf.get("rex", "detail_info_item_actor_rex"))
        d['actor']=c.getRex(actor,self.conf.get("rex", "detail_info_item_split_rex"),1,filter).split('/') if  actor else ''
        type = c.getRex(info,self.conf.get("rex", "detail_info_item_type_rex"))
        d['type']=c.getRex(type,self.conf.get("rex", "detail_info_item_split_rex"),1,filter).split('/') if  type else ''

        release_date = c.getRex(info,self.conf.get("rex", "detail_info_item_release_date_rex"))
        # d['release_date']=c.getRex(release_date,self.conf.get("rex", "detail_info_item_split_rex"),1,filter).split('/') if  release_date else ''
        d['release_date']=c.getRex(release_date,self.conf.get("rex", "detail_info_item_release_date_text_rex")) if  release_date else ''
        d['complete']=0
        if len(d['director'])>0 or len(d['screenwriter'])>0 or len(d['actor'])>0 or len(d['type'])>0 or len(d['release_date'])>0 :
            d['complete']=1
        som=self.m.table('score')

        dtype="/".join(d['type'])
        dactor="/".join(d['actor'])
        ddirector="/".join(d['director'])
        dscreenwriter="/".join(d['screenwriter'])
        drelease_date=d['release_date']

        sod={"type":dtype,"actor":dactor,"director":ddirector,"screenwriter":dscreenwriter,"release_date":drelease_date,"complete":d['complete']}
        som.save(sod,where="id='"+str(id)+"'")       

    def prediction(self,url):

        self.lock = threading.Lock()
        c=Curl(cookie=self.conf.get("curl", "cookie"),proxy_list=self.conf.get("curl", "proxy_list"),user_agent=self.conf.get("curl", "user_agent"))

        d={}
        d["detail_url"]=url
        detail_html=c.getDetail(url)
        filter=self.conf.get("rex", "detail_title_filter_rex").split("&,&")
        d["detail_title"]=c.getRex(detail_html,self.conf.get("rex", "detail_title_rex"),0,filter)
        d['img_url']=c.getRex(detail_html,self.conf.get("rex", "detail_img_rex"),1)

        d["score"]=c.getRex(detail_html,self.conf.get("rex", "detail_score_rex"),1)
        info=c.getRex(detail_html,self.conf.get("rex", "detail_info_rex"))
        # info_item=c.getRexAll(info,self.conf.get("rex", "detail_info_item_rex"),filter)

        director = c.getRex(info,self.conf.get("rex", "detail_info_item_director_rex"))
        d['director']=c.getRex(director,self.conf.get("rex", "detail_info_item_split_rex"),1,filter).split('/') if  director else ''
        screenwriter = c.getRex(info,self.conf.get("rex", "detail_info_item_screenwriter_rex"))
        d['screenwriter']=c.getRex(screenwriter,self.conf.get("rex", "detail_info_item_split_rex"),1,filter).split('/') if  screenwriter else ''
        actor = c.getRex(info,self.conf.get("rex", "detail_info_item_actor_rex"))
        d['actor']=c.getRex(actor,self.conf.get("rex", "detail_info_item_split_rex"),1,filter).split('/') if  actor else ''
        type = c.getRex(info,self.conf.get("rex", "detail_info_item_type_rex"))
        d['type']=c.getRex(type,self.conf.get("rex", "detail_info_item_split_rex"),1,filter).split('/') if  type else ''

        release_date = c.getRex(info,self.conf.get("rex", "detail_info_item_release_date_rex"))
        # d['release_date']=c.getRex(release_date,self.conf.get("rex", "detail_info_item_split_rex"),1,filter).split('/') if  type else ''
        d['release_date']=c.getRex(release_date,self.conf.get("rex", "detail_info_item_release_date_text_rex")) if  release_date else ''
        

        sm=self.m.table('score')
        s=sm.find(where="name='"+d["detail_title"]+"'")

        if s and int(s['score_guess'] or 0)>0:
            # when score_real!=score then update 
            if float(d["score"]) >0 and abs(float(d["score"])-float(s['score_real']))>0.1:
                self.__update(d)
            return s['score_guess']


        self.__update(d)
        # tm=self.m.table('type')
        # t=tm.find(where="1=1",fields="AVG(score) avg")
        # am=self.m.table('actor')
        # a=am.find(where="1=1",fields="AVG(score) avg")
        # dm=self.m.table('director')
        # d=dm.find(where="1=1",fields="AVG(score) avg")
        # scm=self.m.table('screenwriter')
        # sc=scm.find(where="1=1",fields="AVG(score) avg")
        # type_avg=s['type_avg'] if s['type_avg']>0 else t['avg']
        # actor_avg=s['actor_avg'] if s['actor_avg']>0 else a['avg']
        # director_avg=s['director_avg'] if s['director_avg']>0 else d['avg']
        # screenwriter_avg=s['screenwriter_avg'] if s['screenwriter_avg']>0 else sc['avg']
        sm=self.m.table('score')
        s=sm.find(where="name='"+d["detail_title"]+"'")

        return self.calcPrediction(s['type_avg'],s['actor_avg'],s['director_avg'],s['screenwriter_avg'])

    def updateGuessScore(self):
        sm=self.m.table('score')
        score=sm.findAll(where="1=1 AND score_guess IS NULL")
        tm=self.m.table('type')
        t=tm.find(where="1=1",fields="AVG(score) avg")
        am=self.m.table('actor')
        a=am.find(where="1=1",fields="AVG(score) avg")
        dm=self.m.table('director')
        d=dm.find(where="1=1",fields="AVG(score) avg")
        scm=self.m.table('screenwriter')
        sc=scm.find(where="1=1",fields="AVG(score) avg")

        guess_score=[]
        th=self.getTheta()
        gtm=self.m.table('guess_theta')
        for s in score:
            type_avg=s['type_avg'] if s['type_avg']>0 else t['avg']
            actor_avg=s['actor_avg'] if s['actor_avg']>0 else a['avg']
            director_avg=s['director_avg'] if s['director_avg']>0 else d['avg']
            screenwriter_avg=s['screenwriter_avg'] if s['screenwriter_avg']>0 else sc['avg']
            avg_score=self.getGuessScore([type_avg/10,actor_avg/10,director_avg/10,screenwriter_avg/10],th)
            guess_score.append({"id":s['id'],"avg_score":avg_score})
            guess_theta=self.l.calcGuessTheta(avg_score,s['score_real'])
            gtm.add({"k":guess_theta[0],"c":guess_theta[1],})

        k,c=self.getGuessTheta()

        sm=self.m.table('score')
        for gs in guess_score:
            val=k*gs['avg_score']+c
            if val>10:
                val=gs['avg_score']
            sm.save({"score_guess":val},"id="+str(gs['id']))

    def update(self):
        self.lock = threading.Lock()
        url_tpl=self.conf.get("url", "url").replace("{tag}",self.conf.get("url", "tag")).replace("{type}",self.conf.get("url", "type"))
        page_size=int(self.conf.get("constant", "page_size"))
        thread_nums=int(self.conf.get("thread", "thread_nums"))
        jump=page_size*thread_nums
        start=0
        while True :
            close=False
            ts=[]
            for t in xrange(thread_nums):
                url=url_tpl.replace("{start}",str(start))
                thread = threading.Thread(target = self.__deal, args = (url, ))
                thread.start()
                ts.append(thread)
                start+=page_size
                print start

            for thd in ts:
                thd.join()
            close=self.share_queue.get()
            if(not close):
                break
            time.sleep(30)

        print("update finish")


    def getGuessScore(self,avg_score,th):
        score=th["theta1"]*avg_score[0]+th["theta2"]*avg_score[1]+th["theta3"]*avg_score[2]+th["theta4"]*avg_score[3]+th["theta5"]
        return score

    def getTheta(self):
        thm=self.m.table('theta')
        th=thm.find(where="1=1",fields="AVG(theta1) theta1,AVG(theta2) theta2,AVG(theta3) theta3,AVG(theta4) theta4,AVG(theta5) theta5")
        return th

    def getGuessTheta(self):
        thm=self.m.table('guess_theta')
        th=thm.find(where="1=1",fields="AVG(k) k,AVG(c) c")
        return th['k'],th['c']

    def __get(self,url):
        self.lock.acquire()
        c=Curl(cookie=self.conf.get("curl", "cookie"),proxy_list=self.conf.get("curl", "proxy_list"),user_agent=self.conf.get("curl", "user_agent"))
        r=c.getItemList(url,self.conf.get("rex", "item_rex"))
        print r
        if len(r)<=0:
            return []
        detail=[]
        for i in r:
            d={}

            d["detail_url"]=c.getRex(i,self.conf.get("rex", "item_href_rex"),1)
            d["img_url"]=c.getRex(i,self.conf.get("rex", "item_img_rex"),1)
            detail_html=c.getDetail(d["detail_url"])
            filter=self.conf.get("rex", "detail_title_filter_rex").split("&,&")
            d["detail_title"]=c.getRex(detail_html,self.conf.get("rex", "detail_title_rex"),0,filter)

            d["score"]=c.getRex(detail_html,self.conf.get("rex", "detail_score_rex"),1)


            if(d["score"]==0):
                continue

            info=c.getRex(detail_html,self.conf.get("rex", "detail_info_rex"))
            info_item=c.getRexAll(info,self.conf.get("rex", "detail_info_item_rex"),filter)
            # info_item_list=[]
            # for item in info_item:
            #     info_item_list.append(c.getRex(item,self.conf.get("rex", "detail_info_item_split_rex"),1).split('/'))

            director = c.getRex(info,self.conf.get("rex", "detail_info_item_director_rex"))
            d['director']=c.getRex(director,self.conf.get("rex", "detail_info_item_split_rex"),1,filter).split('/') if  director else ''
            screenwriter = c.getRex(info,self.conf.get("rex", "detail_info_item_screenwriter_rex"))
            d['screenwriter']=c.getRex(screenwriter,self.conf.get("rex", "detail_info_item_split_rex"),1,filter).split('/') if  screenwriter else ''
            actor = c.getRex(info,self.conf.get("rex", "detail_info_item_actor_rex"))
            d['actor']=c.getRex(actor,self.conf.get("rex", "detail_info_item_split_rex"),1,filter).split('/') if  actor else ''
            type = c.getRex(info,self.conf.get("rex", "detail_info_item_type_rex"))
            d['type']=c.getRex(type,self.conf.get("rex", "detail_info_item_split_rex"),1,filter).split('/') if  type else ''
            release_date = c.getRex(info,self.conf.get("rex", "detail_info_item_release_date_rex"),1)
            # d['release_date']=c.getRex(release_date,self.conf.get("rex", "detail_info_item_split_rex"),1,filter).split('/') if  type else ''
            d['release_date']=c.getRex(release_date,self.conf.get("rex", "detail_info_item_release_date_text_rex"))
        

            # d['screenwriter']=info_item_list[int(self.conf.get("constant","screenwriter_rex_pos"))]
            # d['actor']=info_item_list[int(self.conf.get("constant","actor_rex_pos"))]
            # d['type']=info_item_list[int(self.conf.get("constant","type_rex_pos"))]

            detail.append(d)

        self.lock.release()
        return detail

    def __deal(self,url):

        detail=self.__get(url)
        print detail
        if len(detail)<=0:
            self.share_queue.put(False)
        else:
            for d in detail:
                self.__update(d)
            self.share_queue.put(True)

    def __update(self,detail):

        self.lock.acquire()
        # 特征值组

        type=detail['type']
        actor=detail['actor']
        director=detail['director']
        screenwriter=detail['screenwriter']

        # 其他信息
        detail_title=detail['detail_title']
        detail_url=detail['detail_url']
        img_url=detail['img_url']
        dtype="/".join(detail['type'])
        dactor="/".join(detail['actor'])
        ddirector="/".join(detail['director'])
        dscreenwriter="/".join(detail['screenwriter'])
        drelease_date=detail['release_date']

        # 实际评分
        score=float(detail['score'])
        score_default=5 if score<=0 else score


        tm=self.m.table('type')
        tsum=0
        tlen=max(len(type),1)
        for t in type:
            t=t.replace("'","")
            rt=tm.find(where="name='"+t+"'")
            if(not rt):
                tsum+=score_default
                tm.add({"name":t,"nums":1,"score":score_default,"score_total":score_default})
            else:
                nums=rt['nums']+1
                score_total=rt['score_total']+score_default
                tsum+=score_total/nums
                tm.save({"nums":nums,"score":score_total/nums,"score_total":score_total},where="name='"+t+"'")

        tavg=tsum/tlen

        asum=0
        alen=max(len(actor),1)
        am=self.m.table('actor')
        for ac in actor:
            ac=ac.replace("'","")
            rt=am.find(where="name='"+ac+"'")
            if(not rt):
                asum+=score_default
                am.add({"name":ac,"nums":1,"score":score_default,"score_total":score_default})
            else:
                nums=rt['nums']+1
                score_total=rt['score_total']+score_default
                asum+=score_total/nums
                am.save({"nums":nums,"score":score_total/nums,"score_total":score_total},where="name='"+ac+"'")

        aavg=asum/alen

        dsum=0
        dlen=max(len(director),1)
        dm=self.m.table('director')
        for di in director:
            di=di.replace("'","")
            rt=dm.find(where="name='"+di+"'")
            if(not rt):
                dsum+=score_default
                dm.add({"name":di,"nums":1,"score":score_default,"score_total":score_default})
            else:
                nums=rt['nums']+1
                score_total=rt['score_total']+score_default
                dsum+=score_total/nums
                dm.save({"nums":nums,"score":score_total/nums,"score_total":score_total},where="name='"+di+"'")

        davg=dsum/dlen

        ssum=0
        slen=max(len(screenwriter),1)
        sm=self.m.table('screenwriter')
        for sc in screenwriter:
            sc=sc.replace("'","")
            rt=sm.find(where="name='"+sc+"'")
            if(not rt):
                ssum+=score_default
                sm.add({"name":sc,"nums":1,"score":score_default,"score_total":score_default})
            else:
                nums=rt['nums']+1
                score_total=rt['score_total']+score_default
                ssum+=score_total/nums
                sm.save({"nums":nums,"score":score_total/nums,"score_total":score_total},where="name='"+sc+"'")

        savg=ssum/slen

        som=self.m.table('score')

        rt=som.find(where="name='"+detail_title+"'")
        sod={"name":detail_title,"img":img_url,"score_real":score,"source_url":detail_url,"type_avg":tavg,"actor_avg":aavg,"director_avg":davg,"screenwriter_avg":savg,"type":dtype,"actor":dactor,"director":ddirector,"screenwriter":dscreenwriter,"release_date":drelease_date}

        if(not rt):
            som.add(sod)
        else:
            som.save(sod,where="name='"+detail_title+"'")

        # if score > 0:  
        #     theta=self.l.calc([tavg/10,aavg/10,davg/10,savg/10],score)

        #     thm=self.m.table('theta')
        #     thm.add({"theta1":theta[0],"theta2":theta[1],"theta3":theta[2],"theta4":theta[3],"theta5":theta[4]})

        self.lock.release()






if __name__ == '__main__':
    ml=MovieLearn()
    ml.run()