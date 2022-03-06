import redis
import os
from flask import Flask

app = Flask(__name__)
redis = redis.Redis(host='redis', port=6379, db=0)

@app.route('/')
def hello_world():
    return 'Hello, World with Nevtik!'

@app.route('/visitor')
def visitor():
    redis.incr('visitor')
    visitor_num = redis.get('visitor').decode("utf-8")
    return "Pengunjung: %s" % (visitor_num)

@app.route('/visitor/reset')
def reset_visitor():
    redis.set('visitor', 0)
    visitor_num = redis.get('visitor').decode("utf-8")
    return "Pengunjung di reset ke %s" % (visitor_num)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
