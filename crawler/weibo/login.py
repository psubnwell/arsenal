"""
参考资料：
[ref: xchaoinfo/fuck-login](https://github.com/xchaoinfo/fuck-login/tree/master/003%20weibo.cn)
[ref: “史上最详细”的Python模拟登录新浪微博流程](https://zhuanlan.zhihu.com/p/23064000)
[ref: ruansongsong/weibo_forward_analysis](https://github.com/ruansongsong/weibo_forward_analysis)
"""

import re
import rsa
import time
import json
import base64
import random
import logging
import binascii
import requests
import urllib.parse
import http.cookiejar
from PIL import Image

class WeiboLogin(object):
    """微博的登录程序
    """

    def __init__(self, username, password, cookie_path):
        self.username = username
        self.password = password

        # 维持一个会话，自动处理 Cookies
        self.session = requests.Session()
        # 全局更新 headers，避免每次请求附带
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36'
        })
        self.cookie_path = cookie_path
        self.session.cookies = http.cookiejar.LWPCookieJar(filename=self.cookie_path)

        # index_url = 'http://weibo.com/login.php'
        # self.session.get(index_url, headers=headers, timeout=2)
        # self.postdata = dict()

    def encrypt_username(self):
        """此函数用于加密微博登录用户名（E-Mail 地址或手机号码）
        """
        # 将用户名进行 URL 编码
        url_encoded_username = urllib.parse.quote_plus(self.username)
        # 将 URL 编码进行 base64 加密
        base64_username = base64.b64encode(url_encoded_username.encode('utf-8'))
        secure_username = base64_username.decode('utf-8')
        return secure_username  # 又叫做 su

    def prelogin(self, su):
        """此函数用于发送微博预登陆（prelogin）请求，以获取加密密码、正式登录所需的参数
        如 servertime、nonce、pubkey、rsakv 等
        """
        # 构建预登陆 URL（Prelogin URL）
        prelogin_url = 'http://login.sina.com.cn/sso/prelogin.php'
        params = {
            'entry': 'weibo',
            'checkpin': 1,
            'callback': 'sinaSSOController.preloginCallBack',
            'rsakt': 'mod',
            'client': 'ssologin.js(v1.4.19)',
            'su': su,
            '_': int(time.time() * 1000)
        }
        # 发送请求
        response = self.session.get(prelogin_url, params=params)
        # print(response.text)
        prelogin_data = json.loads(re.search(r'\((?P<data>.*)\)', response.text).group('data'))
        # print('prelogin_data', prelogin_data)
        return prelogin_data

    def encrypt_password(self, servertime, nonce, pubkey):
        """此函数用于加密微博登录密码
        """
        # 将十六进制数 pubkey 和 10001 转化为十进制整型，创建 RSA 公钥
        public_key = rsa.PublicKey(int(pubkey, 16), int('10001', 16))
        # 微博返回的文件 loginLayers.js 中的加密方式
        message = str(servertime) + '\t' + str(nonce) + '\n' + str(self.password)
        # 将连接后的字符串进行 RSA 加密（要求 message 为 byte 形式）
        encrypted_password = rsa.encrypt(message.encode('utf-8'), public_key)
        # 将加密后的信息转化为十六进制
        secure_password = binascii.b2a_hex(encrypted_password)
        return secure_password  # 又叫做 sp

    def recognize_captcha(self, pcid):
        """此方法用于识别验证码（暂时为手动输入）
        """
        captcha_url = 'https://login.sina.com.cn/cgi/pin.php'
        params = {
            'r': int(random.random() * 1e8),
            's': 0,
            'p': pcid
        }
        response = self.session.get(captcha_url, params=params)
        # 保存验证码
        with open('captcha.jpg', 'wb') as f:
            f.write(response.content)
        # 弹出验证码图片
        im = Image.open('captcha.jpg')
        im.show()
        im.close()
        # 手动输入验证码
        door = input('请输入验证码：')
        return door

    def login_weibo_com(self):
        """此方法用于发送微博正式登录请求
        """
        secure_username = self.encrypt_username()
        prelogin_data = self.prelogin(secure_username)
        secure_password = self.encrypt_password(
            prelogin_data['servertime'],
            prelogin_data['nonce'],
            prelogin_data['pubkey']
        )

        # 构建正式登录的 URL 、参数和 POST 表单数据
        login_url = 'https://login.sina.com.cn/sso/login.php'
        params = {
            'client': 'ssologin.js(v1.4.19)',
            '_': int(time.time() * 1000)
        }
        login_url = login_url + '?' + urllib.parse.urlencode(params)
        post_data = {
            'entry': 'weibo',
            'gateway': '1',
            'from': '',
            'savestate': '7',
            'useticket': '1',
            'pagerefer': 'https://passport.weibo.com',
            'vsnf': '1',
            'service': 'miniblog',
            'encoding': 'UTF-8',
            'pwencode': 'rsa2',
            'sr': '1366*768',
            'prelt': '115',
            'cdult': '38',
            'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
            'rsakv': prelogin_data['rsakv'],
            'servertime': prelogin_data['servertime'],
            'nonce': prelogin_data['nonce'],
            'su': secure_username,
            'sp': secure_password,
            'returntype': 'TEXT'
        }
        # 如果需要验证码则需在表单中添加验证码
        if prelogin_data['showpin']:
            door = self.recognize_captcha(prelogin_data['pcid'])
            post_data['door'] = door

        # 发送请求
        response = self.session.post(login_url, data=post_data)
        login_data = response.json()
        # print('login_data: ', login_data)

        # 登录之后还有一个跳转
        jump_url = 'https://passport.weibo.com/wbsso/login'
        ssosavestate = int(re.findall(r'==-(\d+)-', login_data['ticket'])[0]) + 3600 * 7
            # ssosavestate 这个参数值是猜的，也有人用 int(time.time())
        jump_params = {
            'callback': 'sinaSSOController.callbackLoginStatus',
            'ticket': login_data['ticket'],
            'ssosavestate': ssosavestate,
            'client': 'ssologin.js(v1.4.19)',
            '_': int(time.time() * 1000)
        }
        jump_headers = {
            'Host': 'passport.weibo.com',
            'Referer': 'https://weibo.com',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36'
        }
        response = self.session.get(jump_url, params=jump_params, headers=jump_headers)
        jump_data = json.loads(re.search(r'\((?P<result>.*)\)', response.text).group('result'))
        # print('jump data: ', jump_data)
        uid = jump_data['userinfo']['uniqueid']
        screen_name = jump_data['userinfo']['displayname']
        return uid, screen_name

    def login_m_weibo_cn(self):
        """此方法用于将 weibo.com 登陆成功的 Cookies 登录到 m.weibo.cn
        """
        login_url = 'https://login.sina.com.cn/sso/login.php'
        login_params = {
            'url': 'https://m.weibo.cn/',
            '_rand': time.time(),
            'gateway': 1,
            'service': 'sinawap',
            'entry': 'sinawap',
            'useticket': 1,
            'returntype': 'META',
            'sudaref': '',
            '_client_version': '0.6.26'
        }
        login_headers = {
            'Host': 'login.sina.com.cn',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36'
        }
        response = self.session.get(login_url, params=login_params, headers=login_headers)
        response.encoding = response.apparent_encoding
        login_data = re.findall(r'replace\(\"(.*?)\"\);', response.text)[0]

        # 跳转
        login_url = login_data
        login_headers['Host'] = 'passport.weibo.cn'
        response = self.session.get(login_url, headers=login_headers)

        # 跳转
        login_url = 'https://m.weibo.cn'
        login_headers['Host'] = 'm.weibo.cn'
        response = self.session.get(login_url, headers=login_headers)

        login_data = re.findall(r'login\:\s\[(.*?)\]', response.text)[0]
        if login_data == '1':
            print('Login m.weibo.cn succeed!')
        else:
            print('Login m.weibo.cn failed!')


    def login(self):
        """微博的登录程序
        """
        self.login_weibo_com()
        self.login_m_weibo_cn()

        # 保存 Cookies
        self.session.cookies.save()

if __name__ == '__main__':
    username = '17817815233'
    password = 'asd123654'
    cookie_path = "output/cookies"  # 保存cookie 的文件名称
    weibo = WeiboLogin(username, password, cookie_path)
    weibo.login()
