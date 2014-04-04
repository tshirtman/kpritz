from kivy.lib import osc
from time import sleep
import pocketclient
from kivy.utils import platform as kivy_platform

SERVICE_PORT = 4000


def platform():
    p = kivy_platform()
    if p.lower() in ('linux', 'waindows', 'osx'):
        return 'desktop'
    else:
        return p


class Service(object):
    def __init__(self):
        osc.init()
        self.last_update = 0
        self.oscid = osc.listen(ipAddr='localhost', port=SERVICE_PORT)
        osc.bind(self.oscid, self.pocket_connect, '/pocket/connect')
        osc.bind(self.oscid, self.pocket_list, '/pocket/list')
        osc.bind(self.oscid, self.pocket_mark_read, '/pocket/mark_read')

    def send(self, **kwargs):
        osc.sendMsg()

    def run(self):
        while self._run:
            osc.readQueue(self.oscid)
            sleep(.1)

    def pocket_connect(self, **kwargs):
        if 'token' in kwargs:
            self.token = kwargs['token']
        else:
            pocketclient.authorize(platform(), self.save_pocket_token)

    def save_pocket_token(self, api_key, token, username):
        self.token = {
            'key': api_key,
            'token': token,
            'username': username
            }

    def pocket_list(self, *args):
        if not self.token:
            if self.pocket_last_update:
                pocketclient.get_items(self.
            else:
                pass
        pass

    def pocket_mark_read(self, *args):
        pass


if __name__ == '__main__':
    Service().run()
