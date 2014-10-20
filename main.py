'''
Aforgizmo GUI
=============

An App which saves, retrieves, edits and displays aphorisms

This app is written in Python using the Kivy library for cross-platform support (Android, IOS, Windows, Linux, Mac OSX).  See http://kivy.org/docs/guide/packaging.html for instructions on packaging the application for the different platforms.
'''
import glob
import os
import random

import kivy
kivy.require('1.8.0')
from kivy.config import Config
from kivy.utils import platform
from kivy.core.window import Window
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty, ListProperty

from peewee import *
import models

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

# replace default pygame icon
Config.set('kivy', 'window_icon', 'assets/img/icon.png')

class MainWindow(BoxLayout):
    '''Main UI Widget
    .. versionadded:: 1.0
    .. note:: This new feature will likely blow your mind
    .. warning:: Please take a seat before trying this feature
    '''
    quote_text = ObjectProperty()
    button_random = ObjectProperty()
    quote_text    = ObjectProperty()
    quote_format  = ObjectProperty()
    quote_font    = ObjectProperty()
    author_font   = ObjectProperty()
    button_font   = ObjectProperty()
    backgrounds = ListProperty([])
    background_image = ObjectProperty()

    #background_image = ObjectProperty()

    def __init__(self,**kwargs):
        """
        Initialise app. Load in background images
        :param kwargs:
        :return:
        """
        super(MainWindow,self).__init__()
        self.backgrounds.append(self.get_bg_images())
        self.background_image.source = self.get_rnd_bg_image()

    def get_bg_images(self):
        """
        Get a the list of background images
        :return: list of the background images
        """
        for root, dirs, files in os.walk('assets/img/bg'):
            for file in files:
                if file.endswith('.jpg'):
                     self.backgrounds.append(os.path.join(root, file))
        return self.backgrounds

    def get_rnd_bg_image(self):
        """
        Get a random background image
        :return: path to random background image
        """
        return random.choice(self.backgrounds)

    def button_random_press(self, *args):
        action = args[0]
        if action == 'random':
            self.background_image.source = self.get_rnd_bg_image()
            for a in models.Aphorism.select().order_by(fn.Random()).limit(1):
                self.quote_text.text = self.quote_format.format(
                                            aphorism = a.aphorism,
                                            author = a.author,
                                            author_font = self.author_font,
                                            author_size = int(self.ids.label_text.font_size * 0.75),
                                            quote_font = self.quote_font)
        else:
            pass

class MainApp(App):
    '''Main Program
    '''
    title = 'Aforgizmo Aphorisms'
    icon = 'assets/img/icon.png'

    def __init__(self):
        App.__init__(self)

    def build(self):
        return MainWindow()

if __name__ == '__main__':
    MainApp().run()
