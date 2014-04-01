import webbrowser
import urllib2
import json
from bottle import route, run
#import osc
import threading
#from exceptions import Exception
from pocket_keys import API_KEYS


BASE_URL = 'https://getpocket.com/'
REDIRECT_URL = "http://localhost:8080/authorized/"


def get_token(platform):
    req = urllib2.Request(
        BASE_URL + 'v3/oauth/request',
        json.dumps({
            "consumer_key": API_KEYS[platform],
            "redirect_uri": REDIRECT_URL}),
        {"Content-Type": "application/json", "X-Accept": "application/json"})
    result = urllib2.urlopen(req).read()
    return json.loads(result)["code"]


def authorize(platform):
    code = get_token(platform)
    webbrowser.open(
        BASE_URL + 'auth/authorize?request_token=' + code +
        '&redirect_uri=' + REDIRECT_URL
    )

    @route('/authorized/')
    def web_redirect():
        print "redirect called"
        finish_authorize(platform, code)
        #raise Exception
    threading.Thread(target=run).run()


def finish_authorize(platform, code):
    req = urllib2.Request(
        BASE_URL + 'v3/oauth/authorize',
        json.dumps({"consumer_key": API_KEYS[platform], "code": code}),
        {"Content-Type": "application/json", "X-Accept": "application/json"})
    result = json.loads(urllib2.urlopen(req).read())
    print result
    save_token(result["access_token"], result["username"])


def save_token(token, username):
    pass


def sync():
    pass
