#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 2018年5月30日 下午2:11:16

@author: yxb
'''
import sys
import MySQLdb
from _mysql_exceptions import OperationalError
import xml.etree.ElementTree as ET
import time

class MySQLdbCOnn:
#     def __init__(self):
#         pass
#     def __init__(self,db_pre_name,db_total_num,table_total_num,host_ip, user_name, pass_word,is_process_db):
#         self.db_pre_name=db_pre_name
#         self.db_total_num=db_total_num
#         self.table_total_num=table_total_num
#         self.host_ip = host_ip
#         self.user_name = user_name
#         self.pass_word = pass_word
#         self.is_process_db=is_process_db
    def __init__(self,configDic):
        self.db_pre_name=configDic['db_pre_name']
        self.db_total_num=configDic['db_total_num']
        self.table_total_num=configDic['table_total_num']
        self.host_ip =configDic['host_ip' ]
        self.user_name = configDic['user_name']
        self.pass_word = configDic['pass_word']
        self.is_create_db=configDic['is_create_db']
        self.is_process_db=configDic['is_process_db']

            
def parseXml(xml_name):
    try:
        try:
            root = ET.parse(xml_name).getroot()
        except IOError,e:
            print repr(e)+'xml_name:'+xml_name
            sys.exit()
        configs = root.findall('config')     
        propDic = {}
        for config in configs:  
            propertyList = config.findall('property')  
        for prop in propertyList:
            proname = prop.get('name')  
            provalue= prop.find('value').text
            propDic[proname] = provalue 
#         print propDic
    except Exception,e:
        print repr(e)
        sys.exit()
    return propDic
        
def mySQLdbDDL(connClazz,db_name,sql):
    # 打开数据库连接
    try:
        conn = MySQLdb.connect(connClazz.host_ip, connClazz.user_name, connClazz.pass_word, charset='utf8' )
    except Exception,e:
        print 'connClazz error!! ',repr(e)
        return
    # 使用cursor()方法获取操作游标 
    cursor = conn.cursor() 
    try:
        conn.select_db(db_name)
    except OperationalError,e1:
        print repr(e1)
        if connClazz.is_create_db=='true':
            print 'db_name=',db_name,'does not exists,then execute create CREATE DATABASE %s..'%db_name
            createDBSql='CREATE DATABASE if not exists %s'%db_name
            cursor.execute(createDBSql)
            conn.select_db(db_name)
        else:
            print 'db_name=',db_name,'does not exists,then do noting'
            return    
    # 使用execute方法执行SQL语句
    try:
        cursor.execute(sql)
        print 'mySQLdbDDL() success!! sql:%s'%sql
    except Exception, e:
        print 'error ',repr(e)
        conn.rollback()
    # 关闭数据库连接
  
    conn.close()
    
#    
def read_file(name):
    try:
        with open(name, 'r') as f:
            return f.read()
    except IOError:
        print 'not found file:【%s】 error'% (name)

def print_operatin_plan(sql_sample,mySQLdbCOnn):
    print '您的执行计划是:'
    print '数据库配置:【host_ip】=%s,【user_name】=%s,【pass_word】=%s'%(mySQLdbCOnn.host_ip,mySQLdbCOnn.user_name,mySQLdbCOnn.pass_word)
    DB_NUM=int(mySQLdbCOnn.db_total_num)
    TABLE_NUM=int(mySQLdbCOnn.table_total_num)
    print '总库数:【db_total_num】=%s\t总表数:【table_total_num】=%s'%(DB_NUM,TABLE_NUM)
    print '\t具体分配如下:'
    if DB_NUM>1:
        for i in range(0,DB_NUM):
            db_name=mySQLdbCOnn.db_pre_name+"%d"%i
            print '\t数据库:【db_name】=%s,表编号:%d~%d'%(db_name,(TABLE_NUM/DB_NUM)*i,(TABLE_NUM/DB_NUM)*(i+1)-1)
    elif DB_NUM==1:
        print '\t数据库:【db_name】=%s,表编号:%d~%d'%(mySQLdbCOnn.db_pre_name,0,TABLE_NUM)
    else:
        print 'error...【db_total_num】value must >=1'
        sys.exit()
    print '执行语句样例：【sql_sample】=\n\033[0;33;40m%s\033[0m'%sql_sample%(TABLE_NUM-1)

def wait_second(num):
    while num != 0:
        print '\033[0;31;40m%-3d秒后开始执行操作,操作将不可逆,请慎重考虑...\033[0m'%num
        time.sleep(1) # 休眠1秒
        num -= 1

if __name__=='__main__':
    print 'start...'
    argvList=sys.argv
#     print 'sys.argv.len=%d  value=%s' % (len(argvList),argvList)
    if len(argvList)<=1:
        print '请带一个参数 文件名(内附SQL语句样式)'
        sys.exit()            
    file_name=argvList[1]
    sql_sample=read_file(file_name)
    if sql_sample==None or sql_sample=='':
        print 'file:%s is empty' % file_name
        sys.exit()
    configDic=parseXml('config.xml')
    mySQLdbCOnn=MySQLdbCOnn(configDic)
    print_operatin_plan(sql_sample,mySQLdbCOnn)
    if mySQLdbCOnn.is_process_db!='true':
        print '\033[0;31;40m若确定配置无误，请修改配置文件属性 is_process_db.value:true\033[0m'
        sys.exit()
    wait_second(10)

    TABLE_NUM=int(mySQLdbCOnn.table_total_num)
    DB_NUM=int(mySQLdbCOnn.db_total_num)
    for i in range(0,TABLE_NUM):
        if DB_NUM>1:
            db_index=i/(TABLE_NUM/DB_NUM)
            if db_index>DB_NUM:
                db_index=DB_NUM-1
            db_name=mySQLdbCOnn.db_pre_name+"%d"%db_index
        elif DB_NUM==1:
            db_name=mySQLdbCOnn.db_pre_name
        else:
            print 'error...【db_total_num】value must >=1'
            break
        sql=sql_sample%(i)
        mySQLdbDDL(mySQLdbCOnn,db_name,sql)


              
   
    