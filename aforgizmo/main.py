# -*- coding: utf-8 -*-
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
import json
import time

# kivy imports
import kivy
kivy.require('1.8.0')
from kivy.config import Config
from kivy.utils import platform
from kivy.core.window import Window
from kivy.core.clipboard import Clipboard
from kivy.app import App
from kivy.properties import ObjectProperty, ListProperty, NumericProperty
from kivy.factory import Factory
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.actionbar import ActionBar
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.listview import ListView, ListItemButton
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.lang import Builder
from kivy.core.text import LabelBase

# application imports
from peewee import *
from models import Aphorism

class MyButton(Button):
    """
    Button with a possibility to change the color on on_press (similar to background_down in normal Button widget)
    """
    background_color_normal = ListProperty([0.3, 0.3, 0.3, 0.75])
    background_color_down = ListProperty([0.8, 0.8, 0.8, 0.75])

    def __init__(self, **kwargs):
        super(MyButton, self).__init__(**kwargs)
        self.background_normal = ""
        self.background_down = ""
        self.background_color = self.background_color_normal

    def on_press(self):
        self.background_color = self.background_color_down

    def on_release(self):
        self.background_color = self.background_color_normal

class MyScreenManager(ScreenManager):
    background_image = ObjectProperty(Image(source='assets/img/bg/background.png'))

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
    aphorism = ObjectProperty()

    def copy(self):
        if not self.aphorism:
            return
        A = self.aphorism
        tpl = "\"{aphorism}\"\n  -- {author}\n\n({source})"
        quote = tpl.format(aphorism = A.aphorism, author = A.author, source = A.source)
        Clipboard.put(quote, 'TEXT')
        Clipboard.put(quote, 'text/plain;charset=utf-8')
        Clipboard.put(quote, 'UTF8_STRING')
        w = Factory.WidgetCopy()
        w.textarea_copy.text = quote
        w.textarea_copy.select_all()
        w.open()

    def screenshot(self):
        """
        only works from v 1.8.1
        http://stackoverflow.com/questions/22753306/export-to-png-function-of-kivy-gives-error
        :return:
        """
        self.export_to_png('test.png')

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
        if isinstance(A, Aphorism):
            if tpl == None:
                tpl = """\"[b]{aphorism}[/b]\"\n\n    -- [i]{author}[/i]"""
            formatted = tpl.format(aphorism =  A.aphorism, author = A.author)
            self.ids.quote.text = formatted
            return (tpl, formatted)
        else:
            return A

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
                results.append([a.id, a.ToOneLine(30)])
        self.search_results.item_strings = results
        del self.search_results.adapter.data[:]
        self.search_results.adapter.data.extend(results)
        self.search_results._trigger_reset_populate()

    def args_converter(self, index, data_item):
        id, quote = data_item
        return {'aphorism': (id, quote)}


class ButtonSearchResults(ListItemButton):
   aphorism = ListProperty()

class FormList(BoxLayout):
    results = ObjectProperty()
    def list(self):
        results = []
        try:
            for a in Aphorism.select().order_by(Aphorism.author, Aphorism.source):
                results.append([a.id, a.ToOneLine(30)])
            self.results.item_strings = results
            del self.results.adapter.data[:]
            self.results.adapter.data.extend(results)
            self.results._trigger_reset_populate()
        except Exception as e:
            print e

    def args_converter(self, index, data_item):
        id, quote = data_item
        return {'aphorism': (id, quote)}

    def edit(self):
        id = app.root.select_list_id
        if id > 0:
            app.root.aphorism_edit_by_id(id)

    def delete(self):
        id = app.root.select_list_id
        if id > 0:
            app.root.aphorism_delete_by_id(id)

    def db_import(self):
        files = []
        for root, dirs, files in os.walk('data'):
            for file in files:
                m = re.search('^aphorism(.+).json', 'file')
                if m:
                    files.append(os.path.join(root, file))
        print files
        try:
            filename = 'data/' + files[0]
            with open(filename) as json_file:
                json_data = json.load(json_file)
            Aphorism.insert_many(json_data).execute()
        except Exception as e:
            print e
        else:
            print "success"

    def db_backup(self):
        data = []
        for a in Aphorism.select().order_by(Aphorism.author, Aphorism.source):
            savedata = a.AsHash()
            del(savedata['id'])
            data.append(savedata)
        filename = "data/aphorisms-{0}.json".format(time.strftime("%Y%m%d-%H%M%S"))
        try:
            with open(filename, "w") as fp:
                fp.write(json.dumps(data, fp, indent = 4, sort_keys = True))
        except Exception as e:
            print e
        else:
            print "success"

    def db_reset(self):
        Aphorism.drop_table()
        app.setup_database()

class ButtonListResults(ListItemButton):
    selected_id = NumericProperty()
    aphorism = ListProperty()
    def pressed(self, id):
        self.selected_id = id

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

        # set required fields if empty
        if len(data['author']) == 0:
            data['author'] = app.config.get('editor', 'default_author')
            if len(data['author']) == 0:
                data['author'] = '(Anonymous)'
            self.ids.author.text = data['author']

        if len(data['source']) == 0:
            data['source'] = app.config.get('editor', 'default_source')
            if len(data['source']) == 0:
                data['source'] = '(Unknown)'
            self.ids.source.text = data['source']

        # add aphorism is required fields valid
        if len(data['aphorism']) > 0:
            try:
                a = Aphorism(
                    aphorism = data['aphorism'],
                    author   = data['author'],
                    source   = data['source'],
                    hashtags = data['tags'])
                a.save()
            except Exception as e:
                raise(e)
            else:
                app.root.aphorism_display_by_id(a.id)
                self.dismiss()
        else:
            self.ids.aphorism.focus = True

    def cancel(self):
        self.dismiss()

class FormEdit(Popup):
    aphorism_id = NumericProperty()

    def edit(self, A):
        if isinstance(A, Aphorism):
            self.aphorism_id = A.id
            self.ids.aphorism.text = A.aphorism
            self.ids.author.text = A.author
            self.ids.source.text = A.source
            self.ids.tags.text = A.hashtags
            self.open()

    def edit_action(self):
        data = {
            'id': int(self.aphorism_id),
            'aphorism': self.ids.aphorism.text,
            'author'  : self.ids.author.text,
            'source'  : self.ids.source.text,
            'tags'    : self.ids.tags.text
        }

        # set required fields if empty
        if len(data['author']) == 0:
            data['author'] = app.config.get('editor', 'default_author')
            if len(data['author']) == 0:
                data['author'] = '(Anonymous)'
            self.ids.author.text = data['author']

        if len(data['source']) == 0:
            data['source'] = app.config.get('editor', 'default_source')
            if len(data['source']) == 0:
                data['source'] = '(Unknown)'
            self.ids.source.text = data['source']

        # add aphorism is required fields valid
        if data['id'] > 0 and len(data['aphorism']) > 0:
            try:
                a = Aphorism(
                    id       = data['id'],
                    aphorism = data['aphorism'],
                    author   = data['author'],
                    source   = data['source'],
                    hashtags = data['tags'])
                a.save()
            except Exception as e:
                raise(e)
            else:
                app.root.aphorism_display_by_id(a.id)
                self.cancel()
        else:
            self.ids.aphorism.focus = True

    def cancel(self):
        self.dismiss()


class FormDelete(Popup):
    aphorism_id = NumericProperty()

    def delete(self, A):
        if isinstance(A, Aphorism):
            self.aphorism_id = A.id
            tpl = "\"[b]{aphorism}[/b]\"\n  -- [i]{author}[/i]\n\nSource: [b]{source}[/b]\n\nTags: [b]{tags}[/b]"
            self.ids.aphorism_text.text = tpl.format(
                aphorism = A.aphorism,
                author = A.author,
                source = A.source,
                tags = A.hashtags
            )
            self.open()

    def delete_action(self):
        if self.aphorism_id > 0:
            try:
                a = Aphorism.get(Aphorism.id == self.aphorism_id)
                a.delete_instance()
            except Exception as e:
                raise(e)
            else:
                app.root.select_list_id = None
                self.cancel()
                app.Main.ids.FormList.list()

    def cancel(self):
        self.dismiss()

class WidgetCopy(Popup):
    textarea_copy = ObjectProperty()

class Main(BoxLayout):
    '''Main UI Screen Widget
    .. versionadded:: 1.0
    .. note:: This is the king of the app widgets
    .. warning:: Handle with care!
    '''
    app            = ObjectProperty(None)
    select_list_id = NumericProperty()

    pixel = 'assets/img/pixel.png'

    def __init__(self, **kwargs):
        super(Main, self).__init__()
        self.app = kwargs.get('app')

    def select_list_id(self, id):
        """
        Hack for listing to get the edit id
        """
        self.select_list_id = id

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

    def aphorism_get_by_id(self, id):
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
                    return A

    def aphorism_display_by_id(self, id):
        try:
            A = self.aphorism_get_by_id(id)
        except:
            return False
        else:
            widget = self.aphorism_display(A)
            if int(app.config.get('display', 'bg_enabled')) == 1:
                widget.background_random_set()

        self.ids.Screens.current = 'Main'
        return A

    def aphorism_edit_by_id(self, id):
        try:
            A = self.aphorism_get_by_id(id)
        except:
            return False
        else:
            self.aphorism_display(A)
            widget = Factory.FormEdit()
            widget.edit(A)
            return widget
        return A

    def aphorism_delete_by_id(self, id):
        try:
            A = self.aphorism_get_by_id(id)
        except:
            return False
        else:
            widget = Factory.FormDelete()
            widget.delete(A)
            return widget
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
    backgrounds = ListProperty()

    def __init__(self):
        self.title = 'Pocket Philosopher'
        self.icon = 'assets/img/icon.png'
        App.__init__(self)

    def setup_database(self):
        try:
            for a in Aphorism.select().limit(1):
                pass
        except Exception:
            Aphorism.create_table()

        if 'a' not in locals():
            try:
                try:
                    Aphorism.create_table()
                except:
                    pass

                with open('data/aphorisms.json') as json_file:
                    json_data = json.load(json_file)
                Aphorism.insert_many(json_data).execute()
            except Exception as e:
                print e
                return e

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
        self.setup_database()

    def build_settings(self, settings):
        with open('data/settings.json', 'r') as settings_json:
            settings.add_json_panel('Pocket Philosopher Settings',
                                self.config, data=settings_json.read())

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
        self.Main.aphorism_random_display()
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


if __name__ in ('__main__', '__android__'):
    Config.set('kivy', 'window_icon', 'assets/img/icon.png')

    KIVY_FONTS = [
        {
            "name": "Ubuntu",
            "fn_regular": "assets/fonts/ubuntu/Ubuntu-L.ttf",
            "fn_bold": "assets/fonts/ubuntu/Ubuntu-M.ttf",
            "fn_italic": "assets/fonts/ubuntu/Ubuntu-LI.ttf",
            "fn_bolditalic": "assets/fonts/ubuntu/Ubuntu-MI.ttf"
        }
    ]
    for font in KIVY_FONTS:
        LabelBase.register(**font)

    # load widget lkv files
    files = []
    for root, dirs, files in os.walk('widgets'):
        for file in files:
            if file.endswith('.kv'):
                Builder.load_file(os.path.join(root, file))

    app = MainApp()
    app.run()
