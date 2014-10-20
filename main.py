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
    app = ObjectProperty(None)
    font_path    = ObjectProperty()
    backgrounds = ListProperty([])
    background_image = ObjectProperty()
    button_random = ObjectProperty()
    quote_text    = ObjectProperty()
    quote_format  = ObjectProperty()
    quote_font    = ObjectProperty()
    author_font   = ObjectProperty()

    def __init__(self,**kwargs):
        """
        Initialise app. Load in background images
        :param kwargs:
        :return:
        """
        super(MainWindow,self).__init__()

        # set the app and config for it
        self.app = kwargs.get('app')
        config = self.app.config

        # set default values from main.ini file
        self.quote_format = config.get('display', 'quote_format')

        self.font_path = config.get('fonts', 'font_path')
        fp = self.font_path + '/';
        self.quote_font = fp + config.get('fonts', 'quote_font')
        self.author_font = fp + config.get('fonts', 'author_font')

        # set up initial aphorism background images
        self.backgrounds.append(self.get_bg_images())
        self.background_image.source = self.get_rnd_bg_image()


    def get_bg_images(self):
        """
        Get a the list of background images
        :return: list of the background images
        """
        for root, dirs, files in os.walk(self.app.config.get('display', 'bg_images_folder')):
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
    use_kivy_settings = False
    title = 'Aforgizmo Aphorisms'
    icon = 'assets/img/icon.png'

    def __init__(self):
        App.__init__(self)

    def build(self):
        config = self.config
        self.MainWindow = MainWindow(app = self)
        return self.MainWindow


    def build_config(self, config):
        config.setdefaults('fonts', {
            'font_path': 'assets/fonts/ubuntu',
            'quote_font': 'Ubuntu-B.ttf',
            'author_font': 'Ubuntu-LI.ttf'
        })
        config.setdefaults('display', {
            'quote_format': '"[color=#fff][b][font={quote_font}]{aphorism}[/font][/b][/color]"\n  [size={author_size}][color=#ddd][i][font={author_font}]  -- {author}[/font][/i][/color][/size]',
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
                "desc": "The folder used for to get the background images.",
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
                images = self.MainWindow.get_bg_images()
                self.MainWindow.backgrounds.item_strings = images

if __name__ == '__main__':
    MainApp().run()
