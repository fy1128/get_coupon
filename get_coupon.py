# -*- coding: utf-8 -*-

import requests
import urllib
import time,datetime,threading,httplib
import re
from multiprocessing.dummy import Pool as ThreadPool
from urlparse import urlparse

def get_userdata(file_url, dlist = False):
    data=[]
    with open(file_url,'r') as f1:
        flists=f1.readlines()
        if dlist:
            globals()[dlist] = flists
        for flist in flists:
            if flist[-1]=='\n':
                flist=flist[0:-1]
            if flist.strip() and (flist[0] != '#'):
                data.append(flist)
        data=tuple(data)
        return data

urls=get_userdata('urls.txt', 'urls_parent')
cookies=get_userdata('cookies.txt')
s=requests.session()

i = 0
for l in urls:
    lindex = urls_parent.index(l+"\n")
    lpre = urls_parent[lindex-1].strip()
    comment = ''
    if lpre[0] == '#':
        comment = lpre[1:].strip() + ' -> '
    i += 1
    print(str(i)+') ' + comment + l)

x=int(input('\n请选择第x个url：'))
url = urls[x-1]
url_params = urlparse(url)

def get_webservertime(host = url_params.hostname):
    conn=httplib.HTTPConnection(host)
    conn.request("GET", "/")
    r=conn.getresponse()
    #r.getheaders() #获取所有的http头
    ts=  r.getheader('date') #获取http头date部分
    #将GMT时间转换成北京时间
    ltime= time.strptime(ts[5:25], "%d %b %Y %H:%M:%S")
    nowtime=time.localtime(time.mktime(ltime)+8*60*60)
    print('\n时间校对('+url_params.hostname+'): '+str(datetime.datetime.now().strftime('%H:%M:%S'))+' / '+str(nowtime[3])+':'+str(nowtime[4])+':'+str(nowtime[5]))
    starttime=time.strptime(str(nowtime[0])+'-'+str(nowtime[1])+'-'+str(nowtime[2])+' '+str(target_time),'%Y-%m-%d %H:%M:%S')
    starttime=datetime.datetime(starttime[0],starttime[1],starttime[2],starttime[3],starttime[4],starttime[5])
    nowtime=datetime.datetime(nowtime[0],nowtime[1],nowtime[2],nowtime[3],nowtime[4],nowtime[5])
    return (starttime-nowtime).seconds

def get_page(cookie):
    headers={
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding':'gzip, deflate, sdch',
    'Accept-Language':'zh-CN,zh;q=0.8',
    'Connection':'keep-alive',
    'Cookie':cookie,
    'Host':url_params.hostname,
    'Cache-Control':'max-age=0',
    'Upgrade-Insecure-Requests':'1',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
    }

    user = re.compile(r';pin=(.+?);', flags=0).findall(cookie)
    if not user:
        user = u'用户不存在'
    else:
        user = urllib.unquote(user[0]).decode('utf-8')

    for i in range(0,3,1):
        try:
            r=s.get(url,headers=headers,timeout=60)
        #    print(r.text)
            cer=re.compile('<h1 class="ctxt02"><s class="icon-redbag"></s>(.*)</h1>',flags=0)
            strlist=cer.findall(r.text)
            if not strlist:
                print(datetime.datetime.now().strftime('%H:%M:%S') + ' / ' + user + ': ' + '未知错误')
            else:
                print(datetime.datetime.now().strftime('%H:%M:%S') + ' / ' + user + ': ' + strlist[0])
        except Exception as e:
            print(datetime.datetime.now().strftime('%H:%M:%S') + ' / ' + user + ': ' + str(e))
            continue

        time.sleep(1)        

#模式1：对单个用户进行get操作
def one_get():
    n=int(input('请选择第n个用户进行操作：'))
    print('')
    cookie=cookies[n-1]
    t=threading.Thread(target=get_page(cookie))
    t.start()

#模式2：对所有用户进行get操作
def all_get():
    pool = ThreadPool(len(cookies))
    results = pool.map(get_page, cookies)
    pool.close()
    pool.join()
    #for cookie in cookies:
    #    print('')
    #    t=threading.Thread(target=get_page(cookie))
    #    t.start()

#模式3：对单个用户进行定时get操作
def time_one_get():
    global target_time
    n=int(input('请选择第n个用户进行操作：'))
    cookie=cookies[n-1]
    target_time=str(raw_input('\n请输入开始时间（如00:00:00）：'))
    delaytime = get_webservertime()
    print('\n请等待'+str(delaytime)+'秒\n')
    run=True
    waited=0
    while run:
        time.sleep(1)
        waited += 1
        if delaytime-waited == 0:
            print(datetime.datetime.now().strftime('%H:%M:%S')+': 还剩'+str(delaytime-waited)+'秒')
            print('')
            start=time.clock()
            t=threading.Thread(target=get_page(cookie))
            t.start()
            end=time.clock()
            print('\n共用时%s秒' %(end-start))
            run=False
            break
        if (delaytime-waited > 15) and (waited % 60 == 0):
            waited = 0
            delaytime=get_webservertime()
        print(datetime.datetime.now().strftime('%H:%M:%S')+': 还剩'+str(delaytime-waited)+'秒')

#模式4：对所有用户进行定时get操作
def time_all_get():
    global target_time
    target_time=str(raw_input('\n请输入开始时间（如00:00:00）：'))
    delaytime = get_webservertime()
    print('\n请等待'+str(delaytime)+'秒\n')
    run=True
    waited=0
    while run:
        time.sleep(1)
        waited += 1
        if delaytime-waited == 0:
            print(datetime.datetime.now().strftime('%H:%M:%S')+': 还剩'+str(delaytime-waited)+'秒')
            start=time.clock()
            all_get()
            end=time.clock()
            print('\n共用时%s秒' %(end-start))
            run=False
            break
        if (delaytime-waited > 15) and (waited % 60 == 0):
            waited = 0
            delaytime=get_webservertime()
        print(datetime.datetime.now().strftime('%H:%M:%S')+': 还剩'+str(delaytime-waited)+'秒')

#模式5：对单个用户进行循环get操作
def loop_one_get():
    n=int(input('请选择第n个用户进行操作：'))
    loop_times=int(input('请输入循环次数：'))
    start=time.clock()
    for i in range(loop_times):
        print('')
        cookie=cookies[n-1]
        t=threading.Thread(target=get_page(cookie))
        t.start()
    end=time.clock()
    print('\n共用时%s秒' %(end-start))

#模式6：对所有用户进行循环get操作
def loop_all_get():
    loop_times=int(input('请输入循环次数：'))
    start=time.clock()
    for i in range(loop_times):
        all_get()
    end=time.clock()
    print('\n共用时%s秒' %(end-start))

#模式7：对单个用户进行定时循环get操作
def loop_time_one_get():
    global target_time
    n=int(input('请选择第n个用户进行操作：'))
    cookie=cookies[n-1]
    target_time=str(raw_input('\n请输入开始时间（如00:00:00）：'))
    loop_times=int(input('请输入循环次数：'))
    delaytime = get_webservertime()
    print('\n请等待'+str(delaytime)+'秒\n')
    run=True
    waited = 0
    while run:
        time.sleep(1)
        waited += 1
        if delaytime-waited == 0:
            print(datetime.datetime.now().strftime('%H:%M:%S')+': 还剩'+str(delaytime-waited)+'秒')
            start=time.clock()
            for i in range(loop_times):
                print('')
                t=threading.Thread(target=get_page(cookie))
                t.start()
            end=time.clock()
            print('\n共用时%s秒' %(end-start))
            run=False
            break
        if (delaytime-waited > 15) and (waited % 60 == 0):
            waited = 0
            delaytime=get_webservertime()
        print(datetime.datetime.now().strftime('%H:%M:%S')+': 还剩'+str(delaytime-waited)+'秒')
 
#模式8：对所有用户进行定时循环get操作
def loop_time_all_get():
    global target_time
    target_time=str(raw_input('\n请输入开始时间（如00:00:00）：'))
    loop_times=int(input('请输入循环次数：'))
    delaytime = get_webservertime()
    print('\n请等待'+str(delaytime)+'秒\n')
    run=True
    waited = 0
    while run:
        time.sleep(1)
        waited += 1
        if delaytime-waited == 0:
            print(datetime.datetime.now().strftime('%H:%M:%S')+': 还剩'+str(delaytime-waited)+'秒')
            start=time.clock()
            for i in range(loop_times):
                all_get()
            end=time.clock()
            print('\n共用时%s秒' %(end-start))
            run=False
            break
        if (delaytime-waited > 15) and (waited % 60 == 0):
            waited = 0
            delaytime=get_webservertime()
        print(datetime.datetime.now().strftime('%H:%M:%S')+': 还剩'+str(delaytime-waited)+'秒')

operator={1:one_get,2:all_get,3:time_one_get,4:time_all_get,5:loop_one_get,6:loop_all_get,7:loop_time_one_get,8:loop_time_all_get}

def f(n):
    operator.get(n)()
    print('\n完成')

print('*=============请选择操作模式==============*')
print('*            (1)对单个用户get             *')
print('*            (2)对所有用户get             *')
print('*            (3)对单个用户定时get         *')
print('*            (4)对所有用户定时get         *')
print('*            (5)对单个用户循环get         *')
print('*            (6)对所有用户循环get         *')
print('*            (7)对单个用户定时循环get     *')
print('*            (8)对所有用户定时循环get     *')
print('*=========================================*')

y=int(input('请选择模式（y）：'))
if y in operator.keys():
    f(y)
else:
    print('模式输入错误！')
