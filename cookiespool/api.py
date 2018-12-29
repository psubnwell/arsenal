import json

from flask import Flask, g

from . import db

__all__ = ['app']

app = Flask(__name__)

@app.route('/')
def index():
    return '<h2>Welcome to Cookies Pool</h2>'

def get_conn(websites):
    for website in websites:
        setattr(g, website + '_cookies', db.RedisClient('cookies', website))
        setattr(g, website + '_accounts', db.RedisClient('accounts', website))

@app.route('/<website>/random')
def random(website):
    """获取随机的Cookie
    """
    g = get_conn()
    cookies = getattr(g, website + '_cookies').random()
    return cookies

@app.route('/<website>/add/<username>/<password>')
def add(website, username, password):
    """添加用户
    """
    g = get_conn()
    getattr(g, website + '_accounts').set(username, password)

@app.route('/<website>/count')
def count(website):
    """获取Cookies总数
    """
    g = get_conn()
    count = getattr(g, website + '_cookies').count()
    return count

if __name__ == '__main__':
    app.run(host='0.0.0.0')
