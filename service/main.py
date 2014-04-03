from kivy.lib import osc
from time import sleep
import pocketclient
from kivy.utils import platform

SERVICE_PORT = 4000


class Service(object):
    def __init__(self):
        osc.init()
        self.oscid = osc.listen(ipAddr='localhost', port=SERVICE_PORT)
        osc.bind(self.oscid, self.pocket_connect, '/pocket/connect')
        osc.bind(self.oscid, self.pocket_list, '/pocket/list')
        osc.bind(self.oscid, self.pocket_mark_read, '/pocket/mark_read')

    def run(self):
        while self._run:
            osc.readQueue(self.oscid)
            sleep(.1)

    def pocket_connect(self, *args):
        pocketclient.authorize(platform(), self.save_pocket_token)

    def pocket_list(self, *args):
        pass

    def pocket_mark_read(self, *args):
        pass


if __name__ == '__main__':
    Service().run()
