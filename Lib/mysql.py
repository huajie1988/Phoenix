#-*- coding: UTF-8 -*-
__author__ = 'Huajie'


import MySQLdb,types,sys

class Mysql(object):
    cur=''
    tableName=''
    db=''
    def __init__(self,db_info):
        self.db=MySQLdb.connect(host=db_info['host'],user=db_info['user'],passwd=db_info['pass'],db=db_info['db'],charset=db_info['charset'])
        self.cur=self.db.cursor(cursorclass = MySQLdb . cursors . DictCursor )    #让返回的是字典类型

    def table(self,table):
        self.tableName=table
        return self

    def add(self,data):
        sql="insert into "+self.tableName+"(%field_list%) values(%placeholder_list%)"
        placeholder_list=[]
        field_list=[]
        param=[]
        for d in data:
            placeholder_list.append("%s")
            field_list.append(d)
            param.append(data[d])
        placeholder=','.join(placeholder_list)
        field=','.join(field_list)
        sql=sql.replace('%placeholder_list%',placeholder).replace('%field_list%',field)
        res=False
        try:
            self.cur.execute(sql,param)
            self.db.commit()     #加上这句之后才会提交执行，否则不执行
            res=int(self.cur.lastrowid)
        except:
            # 发生错误时回滚
            self.db.rollback()

        return res

    def save(self,data,where=''):
        sql="update "+self.tableName+" SET %placeholder_list% "
        if(where!=''):
            sql+=" WHERE "+where
        placeholder_list=[]
        param=[]
        for d in data:
            placeholder_list.append(d+"=%s")
            param.append(data[d])
        placeholder=','.join(placeholder_list)
        sql=sql.replace('%placeholder_list%',placeholder)
        res=False
        try:
            res=self.cur.execute(sql,param)
            self.db.commit()     #加上这句之后才会提交执行，否则不执行
        except MySQLdb.Error, arg:
            (errno, err_msg) = arg
            print "recv failed: %s, errno=%d" % (err_msg, errno)
            # 发生错误时回滚
            self.db.rollback()

        return res

    def __find(self,where='',fields='*',order='',limit=''):
        sql="select "+fields+ " from "+self.tableName
        if(where!=''):
            sql+=" WHERE "+where

        if(order!=''):
            sql+=" ORDER BY "+order

        if((type(limit) is types.IntType) and int(limit)>0):
            sql+=" LIMIT "+str(limit)

        return sql

    def find(self,where='',fields='*',order=''):
        sql=self.__find(where=where,fields=fields,order=order,limit=1)
        self.cur.execute(sql)
        rets=self.cur.fetchall()
        return rets[0] if len(rets)>0 else {}

    def findAll(self,where='',fields='*',order=''):
        sql=self.__find(where=where,fields=fields,order=order)
        self.cur.execute(sql)
        rets=self.cur.fetchall()
        return rets

    def findBySQL(self,sql):
        res=False
        try:
            res=self.cur.execute(sql)
            self.db.commit()
        except:
            # 发生错误时回滚
            self.db.rollback()
        return res

    def test(self):
        return 111