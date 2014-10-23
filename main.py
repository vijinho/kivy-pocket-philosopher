'''
Aforgizmo GUI
=============

An App which saves, retrieves, edits and displays aphorisms

This app is written in Python using the Kivy library for cross-platform support (Android, IOS, Windows, Linux, Mac OSX).  See http://kivy.org/docs/guide/packaging.html for instructions on packaging the application for the different platforms.
'''
import os
import random
import imghdr
import re
from peewee import *
from models import Aphorism

import kivy
kivy.require('1.8.0')
from kivy.config import Config
from kivy.utils import platform
from kivy.core.window import Window
from kivy.app import App
from kivy.factory import Factory
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.actionbar import ActionBar
from kivy.uix.popup import Popup
from kivy.uix.listview import ListView, ListItemButton
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.button import Button
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
    Window.size = (400, 800)
    Config.set('graphics', 'width', '400')
    Config.set('graphics', 'height', '800')
else:
    Config.set('graphics', 'fullscreen', True)

Config.set('kivy', 'window_icon', 'assets/img/icon.png')


class Main(FloatLayout):
    '''Main UI Screen Widget
    .. versionadded:: 1.0
    .. note:: This new feature will likely blow your mind
    .. warning:: Please take a seat before trying this feature
    '''
    app            = ObjectProperty(None)

    pixel = 'assets/img/pixel.png'

    def __init__(self, **kwargs):
        super(Main, self).__init__()

        # set the app and config for it
        self.app = kwargs.get('app')

    def aphorism_clear_widget(self):
        container = self.ids.aphorism_container
        container.clear_widgets()
        return container

    def aphorism_display(self, A):
        container = self.aphorism_clear_widget()
        widget = Factory.AphorismWidget()
        widget.set(A)
        container.add_widget(widget)
        return widget

    def aphorism_display_by_id(self, id):
        try:
            id = int(id)
        except:
            return False
        else:
            if id:
                try:
                    A = Aphorism.get(Aphorism.id == id)
                except:
                    return False
                else:
                    widget = self.aphorism_display(A)
                    if int(app.config.get('display', 'bg_enabled')) == 1:
                        widget.background_set_random()

                    self.ids.Screens.current = 'Main'
                    return A

    def aphorism_display_random(self):
        container = self.aphorism_clear_widget()
        widget = Factory.AphorismWidget()
        A = widget.set_random()
        container.add_widget(widget)
        return A


class AphorismWidget(BoxLayout):
    pixel = 'assets/img/pixel.png'

    def get_random(self):
        for A in Aphorism.select().order_by(fn.Random()).limit(1):
            return A

    def set_random(self):
        if int(app.config.get('display', 'bg_enabled')) == 1:
            self.set_background(self.background_get_random())
        A = self.get_random()
        self.set(A)
        return A

    def set(self, A, tpl = None):
        self.aphorism = A
        if tpl == None:
            tpl = """
            \"[b]{aphorism}[/b]\"\n  -- [i]{author}[/i]
            """
        formatted = tpl.format(aphorism =  A.aphorism, author = A.author)
        self.ids.quote.text = formatted
        return (tpl, formatted)

    def set_background(self, path):
        if imghdr.what(path) in ('jpeg', 'png', 'tiff'):
            self.ids.background.source = path
        else:
            self.ids.background.source = self.pixel

    def background_get_random(self):
        return app.background_get_random()

    def background_set_random(self):
        self.set_background(self.background_get_random())

class MyButton(Button):
    pass

class SearchInputWidget(TextInput):
    pat = re.compile('[^A-Za-z0-9_]')
    def insert_text(self, substring, from_undo=False):
        s = re.sub(self.pat, '', substring.lower())
        self.on_text_validate()
        return super(SearchInputWidget, self).insert_text(s, from_undo=from_undo)

    def on_text_validate(self):
        app.Main.ids.SearchForm.search_action(text = self.text)

class SearchForm(BoxLayout):
    """
    Search Form for Aphorisms
    """
    def search_action(self, text):
        results = []
        if len(str(text)) > 0:
            search = '%%{0}%%'.format(text)
            for a in Aphorism.select().where(
                Aphorism.aphorism ** search).order_by(Aphorism.author, Aphorism.source):
                results.append([a.id, a.ToOneLine()])
        self.search_results.item_strings = results
        del self.search_results.adapter.data[:]
        self.search_results.adapter.data.extend(results)
        self.search_results._trigger_reset_populate()

    def args_converter(self, index, data_item):
        id, quote = data_item
        return {'aphorism': (id, quote)}

class SearchResultsButton(ListItemButton):
    aphorism = ListProperty()
    pass


class MainApp(App):
    '''Main Program
    '''
    use_kivy_settings = False

    def __init__(self):
        self.title = 'Aforgizmo'
        self.icon = 'assets/img/icon.png'
        App.__init__(self)

    def build(self):
        self.Main = Main(app = self)
        return self.Main

    def build_config(self, config):
        config.setdefaults('fonts', {
            'quote_font': 'assets/fonts/ubuntu/Ubuntu-B.ttf'
        })
        config.setdefaults('display', {
            'bg_folder': 'assets/img/bg'
        })
        config.setdefaults('display', {
            'bg_enabled': 1
        })

    def build_settings(self, settings):
        jsondata = """[
            {
                "type": "title",
                "title": "Display Settings"
            },
            {
                "type": "bool",
                "title": "Show Background Images?",
                "desc": "Show a random background image behind each aphorism?",
                "section": "display",
                "key": "bg_enabled",
                "true": "auto"
            },
            {
                "type": "path",
                "title": "Background Image Folder",
                "desc": "The folder used for to get the background images.",
                "section": "display",
                "key": "bg_folder"
            }
            ]"""
        settings.add_json_panel('Aforgizmo Settings',
                                self.config, data=jsondata)

    def on_config_change(self, config, section, key, value):
        if config is self.config:
            token = (section, key)
            if token == ('display', 'bg_folder'):
                self.background_refresh_list()
            elif token == ('display', 'bg_enabled'):
                pass

    def on_start(self):
        """
        Fired when the application is being started (before the runTouchApp() call.
        """
        self.background_refresh_list()
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

    def background_refresh_list(self):
        """
        Get a the list of file paths to bg images
        :return: list of the bg image path strings
        """
        self.backgrounds = []
        try:
            for root, dirs, files in os.walk(self.config.get('display', 'bg_folder')):
                for file in files:
                    if file.endswith('.jpg'):
                         path = os.path.join(root, file)
                         if imghdr.what(path) in ('jpeg', 'png', 'tiff'):
                             self.backgrounds.append(path)
        except:
            pass

        return self.backgrounds

    def background_get_random(self):
        """
        Get a random bg image path string
        :return: file path to random bg image
        """
        background = random.choice(self.backgrounds)
        # fix bug where the list and not a string is returned by bg_random
        if (isinstance(background, kivy.properties.ObservableList)):
            return self.backgrounds_random()
        return background


class MainActionBar(ActionBar):
    def about_widget(self):
        p = AboutWidget()
        p.open()

    def help_widget(self):
        p = HelpWidget()
        p.open()

class AboutWidget(Popup):
    pass

class HelpWidget(Popup):
    pass


if __name__ == '__main__':
    app = MainApp()
    app.run()
