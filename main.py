# scoding: utf-8
# copyright 2014 tshirtman
# Kpritz is free software and is distributed under the GPL licence

from __future__ import division

from kivy.app import App
from kivy.properties import ListProperty, NumericProperty, StringProperty
from kivy.clock import Clock
from kivy.config import Config
from kivy.factory import Factory
from ConfigParser import NoOptionError
from os.path import join
from epub2txt import dump
import html2text

__version__ = '0.1'

Config.setdefaults('Kpritz', {
    'speed': 260,
    'lastbook': '',
    'bg_color': '1 1 1 1',
    'fg_color': '0 0 0 1',
    'hl_color': '1 0 0 1',
    'text_size': '100',
    'default_path': '.',
    })

SENTENCE_END = (u'.', 'u!', u'?', u'...', u'…', u':')


class Kpritz(App):
    bookname = StringProperty(Config.get('Kpritz', 'lastbook'))
    speed = NumericProperty(Config.getint('Kpritz', 'speed'))
    bg_color = ListProperty(
        map(float, Config.get('Kpritz', 'bg_color').split()))
    fg_color = ListProperty(
        map(float, Config.get('Kpritz', 'fg_color').split()))
    hl_color = ListProperty(
        map(float, Config.get('Kpritz', 'hl_color').split()))
    text_size = NumericProperty(Config.getfloat('Kpritz', 'text_size'))
    default_path = StringProperty(Config.get('Kpritz', 'default_path'))
    text = ListProperty([])
    position = NumericProperty(0)

    def build(self):
        super(Kpritz, self).build()
        if self.bookname:
            try:
                self.open('', self.bookname)
            except IOError:
                self.bookname = ''

        return self.root

    def save_position(self):
        Config.set('Kpritz', self.bookname, self.position)

    def get_words(self, f):
        if f.endswith('.epub'):
            return dump(f).split()

        elif f.endswith('.html'):
            h = html2text.HTML2Text()
            h.ignore_links = True
            h.unicode_snob = True
            h.ignore_images = True
            h.ignore_emphasis = True
            h.skip_internal_links = True
            with open(f) as fd:
                return h.handle(fd.read()).split()

        else:
            with open(f) as fd:
                return fd.read().split()

    def open(self, path, filename):
        if self.position:
            self.save_position()

        f = join(path, filename)
        Config.set('Kpritz', 'lastbook', f)
        self.bookname = f

        try:
            self.text = [unicode(w, 'utf-8') for w in self.get_words(f)]

        except Exception, e:
            p = Factory.ErrorPopup().open()
            p.message = str(e)

        try:
            self.position = Config.getint('Kpritz', f)
        except NoOptionError:
            self.position = 0

    def play(self, *args):
        self._next()

    def _next(self, *args):
        if self.position + 1 < len(self.text):
            self.position += 1
            Clock.schedule_once(self._next, 60 / self.speed)

    def pause(self, *args):
        Clock.unschedule(self._next)

    def previous(self, *args):
        self.position -= 1

    def next(self, *args):
        self.position += 1

    def previous_sentence(self, *args):
        while True:
            self.position -= 1

            if self.position == 0:
                break

            elif self.text[self.position - 1].endswith(SENTENCE_END):
                break

    def next_sentence(self, *args):
        while True:
            self.position += 1

            if self.position == len(self.text):
                break

            elif self.text[self.position - 1].endswith(SENTENCE_END):
                break

    def on_pause(self, *args):
        Config.write()
        return True

    def on_resume(self, *args):
        return True

    def on_speed(self, *args):
        Config.set('Kpritz', 'speed', self.speed)

    def on_bg_color(self, *args):
        Config.set('Kpritz', 'bg_color', ' '.join(map(str, self.bg_color)))

    def on_fg_color(self, *args):
        Config.set('Kpritz', 'fg_color', ' '.join(map(str, self.fg_color)))

    def on_hl_color(self, *args):
        Config.set('Kpritz', 'hl_color', ' '.join(map(str, self.hl_color)))

    def on_text_size(self, *args):
        Config.set('Kpritz', 'text_size', self.text_size)

    def on_default_path(self, *args):
        Config.set('Kpritz', 'default_path', self.default_path)

    def on_stop(self, *args):
        self.save_position()
        Config.write()


if __name__ == '__main__':
    Kpritz().run()
