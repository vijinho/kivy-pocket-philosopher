'''
Aforgizmo GUI
=============

An App which saves, retrieves, edits and displays aphorisms

This app is written in Python using the Kivy library for cross-platform support (Android, IOS, Windows, Linux, Mac OSX).  See http://kivy.org/docs/guide/packaging.html for instructions on packaging the application for the different platforms.
'''
# python core/system imports
import os
import random
import imghdr
import re

# kivy imports
import kivy
kivy.require('1.8.0')
from kivy.config import Config
from kivy.utils import platform
from kivy.core.window import Window
from kivy.app import App
from kivy.properties import ObjectProperty, ListProperty
from kivy.factory import Factory
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.actionbar import ActionBar
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.listview import ListView, ListItemButton

# application imports
from peewee import *
from models import Aphorism

Config.set('kivy', 'window_icon', 'assets/img/icon.png')

class ActionBarMain(ActionBar):
    def about(self):
        WidgetAbout().open()

    def help(self):
        WidgetHelp().open()

    def new(self):
        FormNew().open()

class WidgetAbout(Popup):
    pass

class WidgetHelp(Popup):
    pass

class WidgetAphorism(BoxLayout):
    pixel = 'assets/img/pixel.png'

    def random_get(self):
        for A in Aphorism.select().order_by(fn.Random()).limit(1):
            return A

    def random_set(self):
        if int(app.config.get('display', 'bg_enabled')) == 1:
            self.background_set(self.background_random_get())
        A = self.random_get()
        self.set(A)
        return A

    def set(self, A, tpl = None):
        self.aphorism = A
        if tpl == None:
            tpl = """\"[b]{aphorism}[/b]\"\n\n    -- [i]{author}[/i]"""
        formatted = tpl.format(aphorism =  A.aphorism, author = A.author)
        self.ids.quote.text = formatted
        return (tpl, formatted)

    def background_set(self, path):
        if imghdr.what(path) in ('jpeg', 'png', 'tiff'):
            self.ids.background.source = path
        else:
            self.ids.background.source = self.pixel

    def background_random_get(self):
        return app.background_random_get()

    def background_random_set(self):
        self.background_set(self.background_random_get())


class WidgetInputSearch(TextInput):
    pat = re.compile('[^A-Za-z0-9_]')
    def insert_text(self, substring, from_undo=False):
        s = re.sub(self.pat, '', substring.lower())
        self.on_text_validate()
        return super(WidgetInputSearch, self).insert_text(s, from_undo=from_undo)

    def on_text_validate(self):
        app.Main.ids.FormSearch.search(text = self.text)

class FormSearch(BoxLayout):
    def search(self, text):
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

class ButtonSearchResults(ListItemButton):
   aphorism = ListProperty()
   pass


class FormTextInput(TextInput):
    max_chars = 255
    valid_chars = ''
    def insert_text(self, substring, from_undo=False):
        if len(self.valid_chars) > 0:
            valid_chars = '[^' + self.valid_chars + ']'
            pat = re.compile(valid_chars)
            s = re.sub(valid_chars, '', substring)
        else:
            s = substring
        super(FormTextInput, self).insert_text(s, from_undo=from_undo)
        self.validate(self.max_chars)

    def validate(self, max_chars):
        if int(max_chars) <= 0:
            max_chars = self.max_chars
        s = self.text
        self.text = (s[:max_chars]) if len(s) > max_chars else s

class FormNew(Popup):
    def new(self):
        data = {
            'aphorism': self.ids.aphorism.text,
            'author'  : self.ids.author.text,
            'source'  : self.ids.source.text,
            'tags'    : self.ids.tags.text
        }

        if len(data['author']) == 0:
            data['author'] = app.config.get('editor', 'default_author')

        if len(data['source']) == 0:
            data['source'] = app.config.get('editor', 'default_source')

        if len(data['aphorism']) > 0:
            try:
                a = Aphorism(
                    aphorism = data['aphorism'],
                    author   = data['author'],
                    source   = data['source'],
                    hashtags = data['tags'])
                a.save()
            except Exception:
                print "Fail!"
            else:
                app.root.aphorism_display_by_id(a.id)
                self.dismiss()

    def cancel(self):
        self.dismiss()
        print "Cancel New!"


class Main(BoxLayout):
    '''Main UI Screen Widget
    .. versionadded:: 1.0
    .. note:: This is the king of the app widgets
    .. warning:: Handle with care!
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
        widget = Factory.WidgetAphorism()
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
                        widget.background_random_set()

                    self.ids.Screens.current = 'Main'
                    return A

    def aphorism_random_display(self):
        container = self.aphorism_clear_widget()
        widget = Factory.WidgetAphorism()
        A = widget.random_set()
        container.add_widget(widget)
        return A


class MainApp(App):
    '''Main Program
    '''
    use_kivy_settings = False

    def __init__(self):
        self.title = 'Pocket Philosopher'
        self.icon = 'assets/img/icon.png'
        App.__init__(self)

    def build(self):
        self.Main = Main(app = self)
        return self.Main

    def build_config(self, config):
        config.setdefaults('display', {
            'bg_folder': 'assets/img/bg'
        })
        config.setdefaults('display', {
            'bg_enabled': 1
        })
        config.setdefaults('editor', {
            'default_author': '(Anonymous)'
        })
        config.setdefaults('editor', {
            'default_source': '(Unknown)'
        })

    def build_settings(self, settings):
        jsondata = """[
            {
                "type": "title",
                "title": "Background Image Settings"
            },
            {
                "type": "bool",
                "title": "Show Images?",
                "desc": "Show a random background image behind each aphorism?",
                "section": "display",
                "key": "bg_enabled",
                "true": "auto"
            },
            {
                "type": "path",
                "title": "Image Folder",
                "desc": "The top-level folder used to find the background images.",
                "section": "display",
                "key": "bg_folder"
            },
            {
                "type": "title",
                "title": "Editor Settings"
            },
            {
                "type": "string",
                "title": "Default Author",
                "desc": "What text should appear for the author's name when not entered?",
                "section": "editor",
                "key": "default_author"
            },
            {
                "type": "string",
                "title": "Default Source",
                "desc": "What text should appear for the source of the aphorism when not entered?",
                "section": "editor",
                "key": "default_source"
            }
            ]"""
        settings.add_json_panel('Pocket Philosopher Settings',
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
        self.background_refresh_list()
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

    def background_random_get(self):
        """
        Get a random bg image path string
        :return: file path to random bg image
        """
        background = random.choice(self.backgrounds)
        # fix bug where the list and not a string is returned by bg_random
        if (isinstance(background, kivy.properties.ObservableList)):
            return self.backgrounds_random()
        return background


if __name__ == '__main__':
    app = MainApp()
    app.run()
