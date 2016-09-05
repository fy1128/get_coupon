# -*- coding: utf-8 -*-
'''
Required
- requests
- bs4
Info
- author : "huangfs"
- email : "huangfs@bupt.edu.cn"
- date : "2016.4.13"
'''
import os,sys,shutil,time,random
import requests
from bs4 import BeautifulSoup
import cookielib, urllib, urllib2
from tesseract import image_to_string
from selenium import webdriver

default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

try:
    input = raw_input
except:
    pass

def get_userdata(file_url):
    data=[]
    with open(file_url,'r') as f1:
        flists=f1.readlines()
        for flist in flists:
            if flist[-1]=='\n':
                flist=flist[0:-1]
            if flist.strip() and (flist[0] != '#'):
                data.append(flist)
        data=tuple(data)
        return data

class JDlogin(object):
    def __init__(self,un,pw):
        self.headers = {'User-Agent':"Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
                        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Encoding':'gzip, deflate, sdch',
                        'Accept-Language':'zh-CN,zh;q=0.8',
                        'Connection':'keep-alive',
                        }
        self.session = requests.session()
        self.login_url = "http://passport.jd.com/uc/login"
        self.post_url = "https://passport.jd.com/uc/loginService"
        self.auth_url = "https://passport.jd.com/uc/showAuthCode"
        self.home_url = "http://home.jd.com/"
        self.un = un
        self.pw = pw
        try:
            self.browser = webdriver.PhantomJS('phantomjs')
        except Exception, e:
            pass

    def cookie_update(self):
        print "\nAuto handle cookie in file, Mozilla Format ...";
        #cookie = cookielib.LWPCookieJar()
        print ('Setting cookies ...')
        cookie = requests.utils.dict_from_cookiejar(self.session.cookies)
        try:
            with open('cookies.txt', 'r') as f:
                with open('cookies.new.txt', 'w') as g:
                    for line in f.readlines():
                        #new_line = line.strip().split()[1][:-2]
                        if urllib.quote(self.un) not in line:
                            g.write(line)
            shutil.move('cookies.new.txt', 'cookies.txt')
            with open('cookies.txt', 'a') as f:
                data = ''
                for k, v in cookie.items():
                    data = data + k + '=' + v + ';'
                f.write(data + '\n')
        except Exception as e:
            print (e)
        finally:
            f.close()
            g.close()

        #cookie.save('cookies.txt', ignore_expires=True, ignore_discard=True)
        print ('\n######## ' + self.un + ' login complete ########\n')

    def get_authcode(self,url):
        self.headers['Host'] = 'authcode.jd.com'
        self.headers['Referer'] = 'https://passport.jd.com/uc/login'
        response = self.session.get(url, headers = self.headers)
        with open('authcode.jpg','wb') as f:
            f.write(response.content)
        # authcode = input("plz enter authcode:")
        authcode = image_to_string('authcode.jpg', False)
        return authcode

    def get_info(self):
        '''获取登录相关参数'''
        try:
            #page = self.session.get(self.login_url, headers = self.headers )
            #soup = BeautifulSoup(page.text, "lxml")
            self.browser.get(self.login_url)
            time.sleep(3)
            soup = BeautifulSoup(self.browser.page_source, "lxml")
            
            # set cookies from PhantomJS
            for cookie in self.browser.get_cookies():
                self.session.cookies[cookie['name']] = str(cookie['value'])      
                
            input_list = soup.select('.form input')

            data = {}
            data['uuid'] = input_list[0]['value']
            #data['machineNet'] = ''
            #data['machineCpu'] = ''
            #data['machineDisk'] = ''
            data['eid'] = input_list[1]['value']
            data['fp'] = input_list[2]['value']
            data['_t'] = input_list[3]['value']
            data['loginType'] = input_list[4]['value']
            data['pubKey'] = input_list[5]['value']
            #rstr = input_list[6]['name']
            #data[rstr] = input_list[6]['value']
            data['chkRememberMe'] = 'on'
            acRequired = self.session.post(self.auth_url, data={'loginName':self.un}).text #返回({"verifycode":true})或({"verifycode":false})

            if 'true' in acRequired:
                # print ('need authcode, plz find it and fill in ')
                print ('auth code required ... processing ...')
                acUrl = soup.select('.form img')[0]['src2']
                acUrl = 'http:{}&yys={}'.format(acUrl,str(int(time.time()*1000)))
                authcode = self.get_authcode(acUrl)
                data['authcode'] = authcode
            else:
                data['authcode'] = ''

        except Exception as e:
            print (e)
        finally:
            return data
    def login(self):
        '''
            登录
        '''
        print ('\n######## ' + self.un + ' pending to login ########\n')
        login_test = None
        while login_test is None:
            postdata = self.get_info()
            postdata['loginname'] = self.un
            #postdata['nloginpwd'] = self.pw
            #postdata['loginpwd'] = self.pw

            try:
                self.browser.get('https://fy1128.github.io/jsencrypt-WFD/receiver.html?pwd=' + urllib.quote(self.pw) + '&pubKey=' + postdata['pubKey'])
                time.sleep(3)
                soup = BeautifulSoup(self.browser.page_source, "html.parser")
                postdata['nloginpwd'] = str(soup.select_one('#pwd').text)
            except Exception as e:
                print('Encrypt password failed: ' + str(e))
                login_test = 1
            finally:
                self.browser.service.process.send_signal(signal.SIGTERM)
                self.browser.quit()

            del(postdata['pubKey'])

            # url parameter
            payload = {
                'r': random.random(),
                'uuid' : postdata['uuid'],
                'version' : 2015
            }

            try:
                self.headers['Host'] = 'passport.jd.com'
                self.headers['Origin'] = 'https://passport.jd.com'
                self.headers['X-Requested-With'] = 'XMLHttpRequest'
                login_page = self.session.post(self.post_url, data = postdata, headers = self.headers)

                # 若返回{“success”:”http://www.jd.com”}，说明登录成功，登录失败继续重试到成功为止
                if login_page.text != '({"success":"//www.jd.com"})':
                    print('LOGIN FAILED', login_page.text )
                    time.sleep(1)
                else:
                    print(login_page.text)
                    self.cookie_update()
                    login_test = 1
            except Exception as e:
                print (e)
                pass

if __name__=="__main__":
    x = input("Generate users' cookies automatically (Y/N) ? ")
    if x.upper() == 'N':
        username = input("plz enter username:")
        password = input("plz enter password:")
        JD = JDlogin(username,password)
        JD.login()
    elif x.upper() == 'Y':
        users = get_userdata('users.txt')
        if len(users) < 1:
            print ('Users is empty!!')
            sys.exit()
        for u in users:
            u = u.split(' ')
            username = u[0]
            password = u[1]
            JD = JDlogin(username,password)
            JD.login()
    else:
        print ('Invaild input detected!!')
