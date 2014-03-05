# scoding: utf-8
# copyright 2014 tshirtman
# Kpritz is free software and is distributed under the GPL licence

from __future__ import division

from kivy.app import App
from kivy.properties import (
    ListProperty, NumericProperty, StringProperty, ObjectProperty)
from kivy.clock import Clock
from kivy.factory import Factory
from ConfigParser import NoOptionError
from os.path import join
from epub2txt import dump
import html2text

__version__ = '0.1'

SENTENCE_END = (u'.', 'u!', u'?', u'...', u'…', u':')


class Kpritz(App):
    bookname = StringProperty('')
    text = ListProperty([])
    position = NumericProperty(0)
    config = ObjectProperty(None)

    def build_config(self, config):
        config.setdefaults('settings', {
            'speed': '250',
            'lastbook': '',
            'bg_color': '#000000FF',
            'fg_color': '#FFFFFFFF',
            'hl_color': '#FF0000FF',
            'text_size': '100',
            'default_path': self.user_data_dir,
            })
        config.add_section('books')
        config.add_callback(self.on_config_change)

    def build(self):
        super(Kpritz, self).build()

        Clock.schedule_once(
            lambda *x: self.open(), 0)

        return self.root

    def save_position(self):
        if self.bookname:
            self.config.set('books', self.bookname, self.position)

    def get_words(self):
        f = self.bookname

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

    def open(self, path='', filename=None):
        if self.position:
            self.save_position()

        if filename:
            f = join(path, filename)
            self.config.set('settings', 'lastbook', f)
            self.bookname = f
        else:
            self.bookname = self.config.get('settings', 'lastbook')

        try:
            self.text = [unicode(w, 'utf-8') for w in self.get_words()]

        except Exception, e:
            p = Factory.ErrorPopup().open()
            p.message = str(e)

        try:
            self.position = self.config.getint('books', self.bookname)
        except NoOptionError:
            self.position = 0

    def play(self, *args):
        self._next()

    def _next(self, *args):
        if self.position + 1 < len(self.text):
            self.position += 1
            Clock.schedule_once(
                self._next, 60 /
                self.config.getint('settings', 'speed'))

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
        #self.config.write()
        return True

    def on_resume(self, *args):
        return True

    def on_config_change(self, section, key, value):
        print "config change"
        self.property('config').dispatch(self)
        self.config.write()

    def on_stop(self, *args):
        self.save_position()
        self.config.write()


if __name__ == '__main__':
    Kpritz().run()
