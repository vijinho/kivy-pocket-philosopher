'''
Aforgizmo GUI
=============

An App which saves, retrieves, edits and displays aphorisms

This app is written in Python using the Kivy library for cross-platform support (Android, IOS, Windows, Linux, Mac OSX).  See http://kivy.org/docs/guide/packaging.html for instructions on packaging the application for the different platforms.
'''
import os
import random
import imghdr
from peewee import *
from models import Aphorism

import kivy
kivy.require('1.8.0')
from kivy.config import Config
from kivy.utils import platform
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.actionbar import ActionBar
from kivy.properties import ObjectProperty, ListProperty


def is_desktop():
    """
    Detect if we are running on the desktop or not
    :return: boolean True if running on a desktop platform or String platform
    """
    if platform in ('linux', 'windows', 'macosx'):
        return True
    else:
        return p

if is_desktop():
    # simulate a mobile app screen size
    Config.set('graphics', 'width', '480')
    Config.set('graphics', 'height', '800')
else:
    Config.set('graphics', 'fullscreen', True)

Config.set('kivy', 'window_icon', 'assets/img/icon.png')


# Declare both screens
class MainScreen(Screen):
    '''Main UI Screen Widget
    .. versionadded:: 1.0
    .. note:: This new feature will likely blow your mind
    .. warning:: Please take a seat before trying this feature
    '''
    app            = ObjectProperty(None)
    font_path      = ObjectProperty()
    quote_template = ObjectProperty()
    quote_font     = ObjectProperty()
    author_font    = ObjectProperty()
    bgs            = ListProperty([])

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__()

        # set the screen manager, app and config for it
        self.name = 'Main'
        self.sm = kwargs.get('sm')
        self.app = kwargs.get('app')

        # set default values from main.ini file
        config = self.app.config
        self.quote_template = config.get('display', 'quote_template')
        self.font_path = config.get('fonts', 'font_path')
        fp = self.font_path + '/'
        self.quote_font = fp + config.get('fonts', 'quote_font')
        self.author_font = fp + config.get('fonts', 'author_font')

        # set up initial aphorism bg images
        self.bgs.append(self.bg_fetch_all())
        self.ids.bg.source = self.bg_random()
        self.btn_random()


    def bg_fetch_all(self):
        """
        Get a the list of file paths to bg images
        :return: list of the bg image path strings
        """
        self.bgs = []
        for root, dirs, files in os.walk(self.app.config.get('display', 'bg_images_folder')):
            for file in files:
                if file.endswith('.jpg'):
                     path = os.path.join(root, file)
                     if imghdr.what(path) in ('jpeg', 'png', 'tiff'):
                         self.bgs.append(path)
        return self.bgs

    def bg_random(self):
        """
        Get a random bg image path string
        :return: file path to random bg image
        """
        bg = random.choice(self.bgs)
        # fix bug where the list and not a string is returned by bg_random
        if (isinstance(bg, kivy.properties.ObservableList)):
            return self.bg_random()
        return bg

    def get_aphorism_formatted(self, Aphorism):
        """
        Get the formatted display string for an aphorism quote
        """
        a = Aphorism
        return self.quote_template.format(
                            aphorism =  a.aphorism,
                            author      = a.author,
                            author_font = self.author_font,
                            author_size = int(self.ids.aphorism.font_size * 0.75),
                            quote_font  = self.quote_font)

    def set_aphorism(self, A):
        """
        Set the current aphorism and save the current aphorism data in the class
        """
        self.ids.aphorism.text = self.get_aphorism_formatted(A)
        self.aphorism = A
        return self.aphorism

    def btn_random(self):
        self.ids.bg.source = self.bg_random()
        for A in Aphorism.select().order_by(fn.Random()).limit(1):
            self.set_aphorism(A)

    def SwitchScreen(self, **kwargs):
        ScreenSwitcher.current = kwargs.get('screen')


class TestScreen(Screen):
    ''' UI Screen Widget
    .. versionadded:: 1.0
    '''
    app            = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(TestScreen, self).__init__()

        # set the screen manager, app and config for it
        self.name = 'Test'
        self.sm = kwargs.get('sm')
        self.app = kwargs.get('app')

        # set default values from main.ini file
        config = self.app.config

    def SwitchScreen(self, **kwargs):
        ScreenSwitcher.current = kwargs.get('screen')


class MainApp(App):
    '''Main Program
    '''
    use_kivy_settings = False

    def __init__(self):
        self.title = 'Aforgizmo Aphorisms'
        self.icon = 'assets/img/icon.png'
        App.__init__(self)

    def build(self):
        # Create the screen manager
        ScreenSwitcher.add_widget(MainScreen(app = self, name = 'Main'))
        ScreenSwitcher.add_widget(TestScreen(app = self, name = 'Test'))
        return ScreenSwitcher

    def build_config(self, config):
        config.setdefaults('fonts', {
            'font_path': 'assets/fonts/ubuntu',
            'quote_font': 'Ubuntu-B.ttf',
            'author_font': 'Ubuntu-LI.ttf'
        })
        config.setdefaults('display', {
            'quote_template': '"[color=#fff][b][font={quote_font}]{aphorism}[/font][/b][/color]"\n  [size={author_size}][color=#ddd][i][font={author_font}]  -- {author}[/font][/i][/color][/size]',
            'bg_images_folder': 'assets/img/bg'
        })


    def build_settings(self, settings):
        jsondata = """[
            {
                "type": "title",
                "title": "Display Settings"
            },
            {
                "type": "path",
                "title": "Background Image Folder",
                "desc": "The folder used for to get the bg images.",
                "section": "display",
                "key": "bg_images_folder"
            }
            ]"""
        settings.add_json_panel('Aforgizmo Aphorisms Settings',
                                self.config, data=jsondata)

    def on_config_change(self, config, section, key, value):
        if config is self.config:
            token = (section, key)
            if token == ('display', 'bg_images_folder'):
                self.MainScreen.bg_fetch_all()

    def on_start(self):
        """
        Fired when the application is being started (before the runTouchApp() call.
        """
        return True

    def on_stop(self):
        """
        Fired when the application stops.
        """
        return True

    def on_pause(self):
        """ For phones/tablets (experimental feature)
        Fired when the application is paused by the OS.
        Warning
        Both on_pause and on_stop must save important data because after
        on_pause is called, on_resume may not be called at all.
        """
        return True

    def on_resume(self):
        """
        Fired when the application is resumed from pause by the OS.
        Beware: you have no guarantee that this event will be fired after the
        on_pause event has been called.
        """
        pass

if __name__ == '__main__':
    # Setup the ScreenManager Instance
    ScreenSwitcher = ScreenManager()
    MainApp().run()
