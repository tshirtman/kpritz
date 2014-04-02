import webbrowser
import urllib2
import json
from wsgiref.simple_server import make_server
#import osc
from pocket_keys import API_KEYS
from random import randint

PORT = randint(8080, 9090)

BASE_URL = 'https://getpocket.com/'
REDIRECT_URL = "http://localhost:%s/authorized/" % PORT


def get_token(platform):
    req = urllib2.Request(
        BASE_URL + 'v3/oauth/request',
        json.dumps({
            "consumer_key": API_KEYS[platform],
            "redirect_uri": REDIRECT_URL}),
        {"Content-Type": "application/json", "X-Accept": "application/json"})
    result = urllib2.urlopen(req).read()
    return json.loads(result)["code"]


def web_redirect(environ, start_response):
    print "redirect called"
    start_response('200 OK', [('Content-Type', 'text/html')])
    return ["app authorized, you can close this tab"]


def authorize(platform, callback):
    code = get_token(platform)
    webbrowser.open(
        BASE_URL + 'auth/authorize?request_token=' + code +
        '&redirect_uri=' + REDIRECT_URL)
    srv = make_server('localhost', PORT, web_redirect)
    # we only want to serve once
    srv.handle_request()
    finish_authorize(platform, code, callback)


def finish_authorize(platform, code, callback):
    req = urllib2.Request(
        BASE_URL + 'v3/oauth/authorize',
        json.dumps({"consumer_key": API_KEYS[platform], "code": code}),
        {"Content-Type": "application/json", "X-Accept": "application/json"})
    result = json.loads(urllib2.urlopen(req).read())
    print result
    callback(API_KEYS[platform], result["access_token"], result["username"])


def sync():
    pass
