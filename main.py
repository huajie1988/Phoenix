#-*- coding: UTF-8 -*-

import ConfigParser,sys,threading,time
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
        cf.read("./Lib/conf")
        self.conf=cf
        db=self.conf.options("db")
        db_info={}
        for d in db:
            db_info[d]=self.conf.get("db",d)
        self.m=Mysql(db_info)
        self.l=Learn()

    def run(self):

        # self.l.calc([.719,.8298,.8376,.698],9.5)
        self.update()

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

            for thd in ts:
                thd.join()
            close=self.share_queue.get()
            if(not close):
                break
            time.sleep(30)

        print("update finish")



    def __get(self,url):
        self.lock.acquire()
        c=Curl(cookie=self.conf.get("curl", "cookie"),proxy_list=self.conf.get("curl", "proxy_list"),user_agent=self.conf.get("curl", "user_agent"))
        r=c.getItemList(url,self.conf.get("rex", "item_rex"))

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

            # d['screenwriter']=info_item_list[int(self.conf.get("constant","screenwriter_rex_pos"))]
            # d['actor']=info_item_list[int(self.conf.get("constant","actor_rex_pos"))]
            # d['type']=info_item_list[int(self.conf.get("constant","type_rex_pos"))]

            detail.append(d)

        self.lock.release()
        return detail

    def __deal(self,url):

        detail=self.__get(url)
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
        sod={"name":detail_title,"img":img_url,"score_real":score,"source_url":detail_url,"type_avg":tavg,"actor_avg":aavg,"director_avg":davg,"screenwriter_avg":savg}
        if(not rt):
            som.add(sod)
        else:
            som.save(sod,where="name='"+detail_title+"'")

        theta=self.l.calc([tavg/10,aavg/10,davg/10,savg/10],score)

        thm=self.m.table('theta')
        thm.add({"theta1":theta[0],"theta2":theta[1],"theta3":theta[2],"theta4":theta[3],"theta5":theta[4]})

        self.lock.release()






if __name__ == '__main__':
    ml=MovieLearn()
    ml.run()