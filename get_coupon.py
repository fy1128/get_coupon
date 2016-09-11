# -*- coding: utf-8 -*-

import requests
import urllib
import os,sys,time,datetime,threading,httplib
import re
from multiprocessing.dummy import Pool as ThreadPool
from urlparse import urlparse

reload(sys)
sys.setdefaultencoding('utf-8')

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

def get_unameincookie(cookie):
    user = re.compile(r';pin=(.+?);', flags=0).findall(cookie)
    if not user:
        user = u'用户不存在'
    else:
        user = urllib.unquote(user[0]).decode('utf-8')
    return user

def get_user():
    global y
    print('')
    uid = 0
    if y < 11:
        for cookie in cookies:
            uid += 1
            print(str(uid)+') '+get_unameincookie(cookie))
        u=int(input('\n请选择用户：'))
        if u <= len(cookies):
            user = get_unameincookie(cookies[u-1])
            print('\n你选择了: '+user+'\n')
            return u
        else:
            print('\n用户不存在，请重输！')
            get_user()
    else:
        for cookie_p in cookies_paypwd:
            uid += 1
            print(str(uid)+') '+get_unameincookie(cookie_p[0]))
        u=int(input('\n请选择用户：'))
        if u <= len(cookies_paypwd):
            user = get_unameincookie(cookies_paypwd[u-1][0])
            print('\n你选择了: '+user+'\n')
            return u
        else:
            print('\n用户不存在，请重输！')
            get_user()

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

def timer():
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
            run=False
            break
        if (delaytime-waited > 15) and (waited % 60 == 0):
            waited = 0
            delaytime=get_webservertime()
        print(datetime.datetime.now().strftime('%H:%M:%S')+': 还剩'+str(delaytime-waited)+'秒')
	
def get_token():
    r=s.get('http://vip.jd.com/bean/25648761.html')
    cer=re.compile('pageConfig.token="(.*)"')
    token=cer.findall(r.text)[0]
    print('token='+token)
    return token
    
def get_itid():
    r=s.get(url)
    cer=re.compile('<div\sclass="p-change-op"\s+itid="(\d+)">')
    itid=cer.findall(r.text)[0]
    print('itemId='+itid)
    return itid
	
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

    user = get_unameincookie(cookie)

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

def post_page(user):
    global token
    global itid
    headers={
    'Accept':'*/*',
    'Accept-Encoding':'gzip, deflate',
    'Accept-Language':'zh-CN,zh;q=0.8',
    'Connection':'keep-alive',
    'Origin':'http://vip.jd.com',
    'X-Requested-With':'XMLHttpRequest',
    'Cookie':user[0],
    'Host':'vip.jd.com',
    'Content-Type':'application/x-www-form-urlencoded',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2743.116 Safari/537.36'
    }
    s=requests.session()
    s.headers=headers
    data='itemId='+itid+'&password='+user[1]+'&token='+token

    user = get_unameincookie(user[0])

    try:
        r=s.post('http://vip.jd.com/bean/exchangeCoupon.html',data=data,timeout=1)
        if '提交错误' in r.text:
            token=get_token()
            return post_page(cookie,password)
        if 'true' in r.text:
            print(datetime.datetime.now().strftime('%H:%M:%S') + ' / ' + user + ': ' + r.text)
            with open('result.txt','a') as fw:
                fw.write(r.text)
    except:
        return post_page(cookie,password)
    else:
        print(datetime.datetime.now().strftime('%H:%M:%S') + ' / ' + user+ ': ' + r.text)		

#模式1：对单个用户进行get操作
def one_get():
    uid = get_user()
    cookie = cookies[uid-1]
    t=threading.Thread(target=get_page(cookie))
    t.start()
    
#模式11：对单个用户进行post操作
def one_post():
    uid = get_user()
    user = cookies_paypwd[uid-1]
    t=threading.Thread(target=post_page(user))
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

#模式12：对所有用户进行post操作
def all_post():
    pool = ThreadPool(len(cookies_paypwd))
    results = pool.map(post_page, cookies_paypwd)
    pool.close()
    pool.join()
    #for i in range(len(passwords)):
    #    cookie,password=cookies[i],passwords[i]
    #    t=threading.Thread(target=post_page,args=(cookie,password))
    #    t.start()

#模式3：对单个用户进行定时get操作
def time_one_get():
    uid = get_user()
    cookie=cookies[uid-1]
    timer()
    print('')
    start=time.clock()
    t=threading.Thread(target=get_page(cookie))
    t.start()
    end=time.clock()
    print('\n共用时%s秒' %(end-start))
    
#模式13：对单个用户进行定时post操作
def time_one_post():
    uid = get_user()
    user=cookies_paypwd[uid-1]
    timer()
    print('')
    start=time.clock()
    t=threading.Thread(target=post_page(user))
    t.start()
    end=time.clock()
    print('\n共用时%s秒' %(end-start))
    
#模式4：对所有用户进行定时get操作
def time_all_get():
    timer()
    print('')
    start=time.clock()
    all_get()
    end=time.clock()
    print('\n共用时%s秒' %(end-start))

#模式14：对所有用户进行定时post操作
def time_all_post():
    timer()
    print('')
    start=time.clock()
    all_post()
    end=time.clock()
    print('\n共用时%s秒' %(end-start))
    
#模式5：对单个用户进行循环get操作
def loop_one_get():
    uid = get_user()
    cookie=cookies[uid-1]
    loop_times=int(input('请输入循环次数：'))
    start=time.clock()
    for i in range(loop_times):
        print('')
        t=threading.Thread(target=get_page(cookie))
        t.start()
    end=time.clock()
    print('\n共用时%s秒' %(end-start))

#模式15：对单个用户进行循环post操作
def loop_one_post():
    uid = get_user()
    user = cookies_paypwd[uid-1]
    loop_times=int(input('请输入循环次数：'))
    start=time.clock()
    for i in range(loop_times):
        print('')
        t=threading.Thread(target=post_page(user))
        t.start()
    end=time.clock()
    print('\n共用时%s秒' %(end-start))

#模式6：对所有用户进行循环get操作
def loop_all_get():
    loop_times=int(input('请输入循环次数：'))
    start=time.clock()
    for i in range(loop_times):
        print('')
        all_get()
    end=time.clock()
    print('\n共用时%s秒' %(end-start))

#模式16：对所有用户进行循环post操作
def loop_all_post():
    loop_times=int(input('请输入循环次数：'))
    start=time.clock()
    for i in range(loop_times):
        print('')
        all_post()
    end=time.clock()
    print('\n共用时%s秒' %(end-start))
        
#模式7：对单个用户进行定时循环get操作
def loop_time_one_get():
    uid = get_user()
    cookie=cookies[uid-1]
    loop_times=int(input('请输入循环次数：'))
    timer()
    start=time.clock()
    for i in range(loop_times):
        print('')
        t=threading.Thread(target=get_page(cookie))
        t.start()
    end=time.clock()
    print('\n共用时%s秒' %(end-start))

#模式17：对单个用户进行定时循环post操作
def loop_time_one_post():
    uid = get_user()
    user = cookies_paypwd[uid-1]
    loop_times=int(input('请输入循环次数：'))
    timer()
    start=time.clock()
    for i in range(loop_times):
        print('')
        t=threading.Thread(target=post_page(user))
        t.start()
    end=time.clock()
    print('\n共用时%s秒' %(end-start))
 
#模式8：对所有用户进行定时循环get操作
def loop_time_all_get():
    loop_times=int(input('请输入循环次数：'))
    timer()
    start=time.clock()
    for i in range(loop_times):
        print('')
        all_get()
    end=time.clock()
    print('\n共用时%s秒' %(end-start))

#模式18：对所有用户进行定时循环post操作
def loop_time_all_post():
    loop_times=int(input('请输入循环次数：'))
    timer()
    start=time.clock()
    for i in range(loop_times):
        print('')
        all_post()
    end=time.clock()
    print('\n共用时%s秒' %(end-start))

#模式19：对单个用户永久循环post
def loop_forever_one_post():
    uid = get_user()
    user = cookies_paypwd[uid-1]
    while True:
        t=threading.Thread(target=post_page(user))
        t.start()
        time.sleep(1)

#模式20：对所有用户永久循环post
def loop_forever_all_post():
    while True:
        for user in cookies_paypwd:
            t=threading.Thread(target=post_page(user))
            t.start()
            time.sleep(1)
        
operator={1:one_get,2:all_get,3:time_one_get,4:time_all_get,5:loop_one_get,6:loop_all_get,7:loop_time_one_get,8:loop_time_all_get,11:one_post,12:all_post,13:time_one_post,14:time_all_post,15:loop_one_post,16:loop_all_post,17:loop_time_one_post,18:loop_time_all_post,19:loop_forever_one_post,20:loop_forever_all_post}

def f(n):
    operator.get(n)()

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
print('*            (11)对单个用户post           *')
print('*            (12)对所有用户post           *')
print('*            (13)对单个用户定时post       *')
print('*            (14)对所有用户定时post       *')
print('*            (15)对单个用户循环post       *')
print('*            (16)对所有用户循环post       *')
print('*            (17)对单个用户定时循环post   *')
print('*            (18)对所有用户定时循环post   *')
print('*            (19)对单个用户永久循环post   *')
print('*            (20)对所有用户永久循环post   *')
print('*            (0)退出                     *')
print('*=========================================*')

y=int(input('请选择模式（y）：'))
if y in operator.keys():
    if y > 10:
        pay_pwds=get_userdata('paypasswords.txt')
        cookies_paypwd = []
        for cookie in cookies:
            data = []
            user_c = get_unameincookie(cookie)
            for person in pay_pwds:
                item = person.split(' ', 1)
                user_p = item[0].decode('utf-8')
                if user_c == user_p:
                   data.extend([cookie, item[1]])
                   data=tuple(data)
                   cookies_paypwd.append(data)
                   break;

        itid = get_itid()
        token = get_token()
    f(y)
elif y==0:
    exit()
else:
    print('模式输入错误！')
