# coding: utf-8
from __future__ import division
from kivy.app import App
from kivy.lang import Builder
from kivy.properties import ListProperty, NumericProperty, StringProperty
from kivy.clock import Clock
from kivy.config import Config
from ConfigParser import NoOptionError
from os.path import join

Config.setdefaults('Kpritz', {
    'speed': 260,
    'lastbook': '',
    'bg_color': '1 1 1 1',
    'fg_color': '0 0 0 1',
    'text_size': '100',
    'default_path': '.',
    })

KV = '''
#:import Factory kivy.factory.Factory
#:import join os.path.join
#:import abspath os.path.abspath
BoxLayout:
    orientation: 'vertical'
    ColoredLabel:
        text: app.text[app.position] if app.text else ''
        font_size: '%dpt' % app.text_size
        halign: 'left'
        text_size: self.width, None

    ColoredLabel:
        text:
            '%d / %d (%2d%%)' % (
            app.position, len(app.text),
            100. * app.position / len(app.text))
        size_hint_y: None
        height: self.texture_size[1]

    BoxLayout:
        size_hint_y: None
        height: '30sp'
        ImageButton:
            source: 'open.png'
            on_press: Factory.OpenFile().open()
        ImageButton:
            source: 'previous_sentence.png'
            on_press: app.previous_sentence()
            disabled: app.position == 0
        ImageButton:
            source: 'previous.png'
            on_press: app.previous()
            disabled: app.position == 0
        ImageButton:
            source: 'play.png'
            on_press: app.play()
            on_release: app.pause()
            disabled: app.position >= len(app.text)
        ImageButton:
            source: 'next.png'
            on_press: app.next()
            disabled: app.position == len(self.text)
        ImageButton:
            source: 'next_sentence.png'
            on_press: app.next_sentence()
            disabled: app.position == len(self.text)
        ImageButton:
            source: 'faster.png'
            on_press: app.speed += 10
            disabled: app.speed == 990
        ImageButton:
            source: 'slower.png'
            on_press: app.speed -= 10
            disabled: app.speed == 10
        Label:
            text: '%3d wpm' % app.speed
            size_hint_x: None
            width: self.texture_size[0]

        Button:
            text: 'Aa'
            on_press: Factory.TextSettings().open()


<OpenFile@Popup>:
    title: 'Select a file'
    size_hint: .9, .9
    BoxLayout:
        orientation: 'vertical'
        FileChooserListView:
            path: app.default_path
            id: fc

        BoxLayout:
            Button:
                size_hint_y: None
                height: '30sp'
                text: 'open'
                disabled: not fc.selection
                on_press:
                    app.open(fc.path, fc.selection[0])
                    root.dismiss()
            Button:
                text: 'cancel'
                on_press:
                    root.dismiss()

<PathSelector@Popup>:
    title: 'Select a default path'
    size_hint: .9, .9
    BoxLayout:
        orientation: 'vertical'
        FileChooserListView:
            path: app.default_path
            id: fc

        BoxLayout:
            Button:
                size_hint_y: None
                height: '30sp'
                text: 'select current dir as default path'
                on_press:
                    app.default_path = abspath(fc.path)
                    root.dismiss()

            Button:
                text: 'cancel'
                on_press:
                    root.dismiss()

<TextSettings@Popup>:
    size_hint: .9, .9
    title: 'text settings'
    opacity: .8

    GridLayout:
        cols: 2
        Label:
            size_hint_y: None
            height: '30sp'
            text: 'text size'
        Slider:
            size_hint_y: None
            height: '30sp'
            min: 10
            max: 500
            value: app.text_size
            on_value: app.text_size = self.value

        Label:
            text: 'background color'

        ColorPicker:
            color: app.bg_color
            on_color: app.bg_color = self.color

        Label:
            text: 'foreground color'

        ColorPicker:
            color: app.fg_color
            on_color: app.fg_color = self.color

        Label:
            size_hint_y: None
            height: '30sp'
            text: 'default path'
        Button:
            size_hint_y: None
            height: '30sp'
            text: app.default_path
            on_press: Factory.PathSelector().open()

        Widget:
            size_hint_y: None
            height: '30sp'
            id: span
            Button:
                text: 'close'
                pos: span.pos
                size: span.parent.width, span.height
                on_press: root.dismiss()

<ImageButton@Button>:
    source: ''
    Image:
        center: root.center
        source: join('data', root.source)
        size: root.size

<ColoredLabel@Label>:
    canvas.before:
        Color:
            rgba: app.bg_color
        Rectangle:
            pos: self.pos
            size: self.size
    color: app.fg_color
'''

SENTENCE_END = ('.', '!', '?', '...', '…', ':')


class Kpritz(App):
    bookname = StringProperty(Config.get('Kpritz', 'lastbook'))
    speed = NumericProperty(Config.getint('Kpritz', 'speed'))
    bg_color = ListProperty(
        map(float, Config.get('Kpritz', 'bg_color').split()))
    fg_color = ListProperty(
        map(float, Config.get('Kpritz', 'fg_color').split()))
    text_size = NumericProperty(Config.getfloat('Kpritz', 'text_size'))
    default_path = StringProperty(Config.get('Kpritz', 'default_path'))
    text = ListProperty([])
    position = NumericProperty(0)

    def build(self):
        if self.bookname:
            self.open('', self.bookname)

        root = Builder.load_string(KV)
        return root

    def save_position(self):
        Config.set('Kpritz', self.bookname, self.position)

    def open(self, path, filename):
        if self.position:
            self.save_position()

        f = join(path, filename)
        Config.set('Kpritz', 'lastbook', f)
        self.bookname = f

        with open(f) as fd:
            self.text = fd.read().split()

        try:
            self.position = Config.getint('Kpritz', f)
        except NoOptionError:
            self.position = 0

    def play(self, *args):
        self._next()

    def _next(self, *args):
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

    def on_text_size(self, *args):
        Config.set('Kpritz', 'text_size', self.text_size)

    def on_default_path(self, *args):
        Config.set('Kpritz', 'default_path', self.default_path)

    def on_stop(self, *args):
        self.save_position()
        Config.write()


if __name__ == '__main__':
    Kpritz().run()