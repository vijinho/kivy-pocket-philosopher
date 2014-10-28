# -*- coding: utf-8 -*-
'''
Aforgizmo GUI
=============

An App which saves, retrieves, edits and displays aphorisms

This app is written in Python using the Kivy library for cross-platform support (Android, IOS, Windows, Linux, Mac OSX).  See http://kivy.org/docs/guide/packaging.html for instructions on packaging the application for the different platforms.
'''

import kivy
kivy.require('1.8.0')
from kivy.properties import ObjectProperty, ListProperty, NumericProperty, StringProperty
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.listview import ListItemButton, ListView
from kivy.app import App
from kivy.uix.popup import Popup
from kivy.config import Config
from kivy.core.text import LabelBase
from kivy.uix.label import Label
import os
from kivy.lang import Builder
from models import Aphorism
from kivy.factory import Factory
import imghdr
import random
import re
import time
import json
from kivy.core.clipboard import Clipboard
from peewee import *


class FormTextInput(TextInput):
    pass

class MyBoxLayout(BoxLayout):
    pass

class MyScreenManager(ScreenManager):
    background_image = ObjectProperty(Image(source='assets/img/bg/background.png'))

class MyImage(Image):
    def __init__(self, **kwargs):
        super(MyImage, self).__init__()

    def texture_width(self):
        return self.texture.size[0]

    def texture_height(self):
        return self.texture.size[1]

    def rescale(self, width, height):
        """
        Resize the image to fit the given dimensions, zooming in or out if
        needed without losing the aspect ratio
        :param width: target width
        :param height: target height
        :return: new dimensions as a tuple (width, height)
        """
        ratio = 0.0
        new_width = 0.0
        new_height = 0.0

        target_width = float(width)
        target_height = float(height)

        image_width = float(self.texture_width())
        image_height = float(self.texture_height())

        ratio = target_width / image_width
        new_width = image_width * ratio
        new_height = image_height * ratio

        if (new_height < target_height):
            ratio = target_height / new_height
            new_height *= ratio
            new_width *= ratio

        if new_width > 0 and new_height > 0:
            self.width = new_width
            self.height = new_height

        return (new_width, new_height)

class MyButton(Button):
    """
    Button with a possibility to change the color on on_press (similar to background_down in normal Button widget)
    and also the background image
    """
    background_image = ObjectProperty(Image(source='assets/img/pixel.png'))
    background_color_normal = ListProperty([0.3, 0.3, 0.3, 0.3])
    background_color_down = ListProperty([0.8, 0.8, 0.8, 0.3])

    def __init__(self, **kwargs):
        super(MyButton, self).__init__(**kwargs)
        self.background_normal = ""
        self.background_down = ""
        self.background_color = self.background_color_normal

    def on_press(self):
        self.background_color = self.background_color_down

    def on_release(self):
        self.background_color = self.background_color_normal

class ImageClickable(ButtonBehavior, MyImage):
    source_up = ObjectProperty(Image(source='assets/img/pixel.png'))
    source_down = ObjectProperty(Image(source='assets/img/pixel.png'))

    def __init__(self, **kwargs):
        super(ImageClickable, self).__init__(**kwargs)
        self.source = 'assets/img/pixel.png'

    def on_press(self):
        self.source = self.source_down

    def on_release(self):
        self.source = self.source_up


class MyListItemButton(ListItemButton):
    selected_id = NumericProperty()
    aphorism = ListProperty()
    def pressed(self, id):
        app.selected_aphorism = self.aphorism
        app.selected_id = id
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


class FormSearch(MyBoxLayout):
    results = ObjectProperty()

    class ButtonSearchResults(MyListItemButton):
        pass

    def search(self, text):
        results = []
        if len(str(text)) > 0:
            search = '%%{0}%%'.format(text)
            for a in Aphorism.select().where(
                Aphorism.aphorism ** search).order_by(Aphorism.author, Aphorism.source):
                results.append([a.id, a.ToOneLine(30)])
            app.current_search = text
        self.results.item_strings = results
        del self.results.adapter.data[:]
        self.results.adapter.data.extend(results)
        self.results._trigger_reset_populate()

    def args_converter(self, index, data_item):
        id, quote = data_item
        return {'aphorism': (id, quote)}


class FormList(MyBoxLayout):
    results = ObjectProperty()

    class ButtonListResults(MyListItemButton):
        pass

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


class WidgetAphorism(MyBoxLayout):
    pixel = 'assets/img/pixel.png'
    aphorism = ObjectProperty()

    def set(self, A, tpl = None):
        self.aphorism = A
        app.current_aphorism = A
        if isinstance(A, Aphorism):
            if tpl == None:
                tpl = """\"[b]{aphorism}[/b]\"\n\n    -- [i]{author}[/i]"""
            formatted = tpl.format(aphorism =  A.aphorism, author = A.author)
            self.ids.quote.text = formatted
            return (tpl, formatted)
        else:
            return A

    def random_set(self):
        if int(app.config.get('display', 'bg_enabled')) == 1:
            self.background_set(app.background_get_random())
        A = app.aphorism_get()
        self.set(A)
        return A

    def background_set(self, path):
        if imghdr.what(path) in ('jpeg', 'png', 'tiff'):
            app.root.ids.background.source = path
            app.current_background = path
        else:
            app.root.ids.background.source = self.pixel
        app.root.ids.background.rescale(app.root.width, app.root.height)

    def background_random_set(self):
        self.background_set(app.background_get_random())

    def screenshot(self):
        """
        only works from v 1.8.1
        http://stackoverflow.com/questions/22753306/export-to-png-function-of-kivy-gives-error
        :return:
        """
        filename = "data/screenshot-{0}.png".format(time.strftime("%Y%m%d-%H%M%S"))
        self.export_to_png(filename)

class Main(MyScreenManager):
    backup_results = ObjectProperty()
    def __init__(self, **kwargs):
        super(Main, self).__init__()

class MainApp(App):
    pixel = 'assets/img/pixel.png'
    use_kivy_settings = False
    backgrounds = ListProperty()
    current_background = StringProperty()
    current_search = StringProperty()
    selected_aphorism = ObjectProperty()
    selected_id = NumericProperty()
    folder = StringProperty()

    def on_selected_id(self, *args):
        id = int(self.selected_id)
        if id > 0:
            print 'Show context-sensitive buttons for selected list item.'

    def __init__(self):
        self.title = 'Pocket Philosopher'
        self.icon = 'assets/img/icon.png'
        self.folder = os.path.dirname(os.path.abspath(__file__))
        self.data_folder = os.path.join(self.folder, 'data')
        App.__init__(self)

    def build(self):
        return Main()

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
                self.backgrounds_refresh()
            elif token == ('display', 'bg_enabled'):
                self.backgrounds_refresh()

    def on_start(self):
        """
        Fired when the application is being started (before the runTouchApp() call.
        """
        self.backgrounds_refresh()
        self.aphorism_random()
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
        self.backgrounds_refresh()
        pass

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

    def form_wipe(self):
        widget = self.FormWipe()
        widget.wipe()

    class FormWipe(Popup):
        def wipe(self):
            self.open()

        def wipe_action(self):
            try:
                app.db_backup()
                Aphorism.drop_table()
                Aphorism.create_table()
            except Exception as e:
                app.root.backup_results.text += "Failed clearing the database.\nError: (" + str(e) + ")\n\n"
            else:
                app.root.backup_results.text += "Successfully cleared the database!" + "\n\n"

            self.dismiss()


    def db_backup(self, path = 'data'):
        data = []
        for a in Aphorism.select().order_by(Aphorism.author, Aphorism.source):
            savedata = a.AsHash()
            del(savedata['id'])
            data.append(savedata)
        try:
            filename = "aphorisms-{0}.json".format(time.strftime("%Y%m%d-%H%M%S"))
            with open(os.path.join(path, filename), "w") as fp:
                fp.write(json.dumps(data, fp, indent = 4, sort_keys = True))
        except Exception as e:
            raise(e)


    def form_backup(self):
        self.FormBackup().open()

    class FormBackup(Popup):
        def backup(self, path, filename):
            if filename and len(filename) > 0:
                filename = os.path.join(path, filename[0])
                if (os.path.isdir(filename)):
                    path = filename
            try:
                app.db_backup(path)
            except Exception as e:
                app.root.backup_results.text += "Failed backup of the file:\n" + path + "\nError: (" + str(e) + ")\n\n"
            else:
                app.root.backup_results.text += "Successfully backed up to the file:\n" + path + "\n\n"

            self.dismiss()

    def form_import(self):
        self.FormImport().open()

    class FormImport(Popup):
        def restore(self, path, filename):
            if filename and len(filename) > 0:
                try:
                    filename = os.path.join(path, filename[0])
                    with open(filename) as json_file:
                        json_data = json.load(json_file)
                    Aphorism.insert_many(json_data).execute()
                except Exception as e:
                    app.root.backup_results.text += "Failed import of the file:\n" + filename + "\nError: (" + str(e) + ")\n\n"
                else:
                    app.root.backup_results.text += "Successfully imported the backup file:\n" + filename + "\n\n"

                self.dismiss()

    def about(self):
        self.WidgetAbout().open()

    class WidgetAbout(Popup):
        pass

    def help(self):
        self.WidgetHelp().open()

    class WidgetHelp(Popup):
        pass

    def backgrounds_refresh(self):
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
        if len(self.backgrounds) > 0:
            background = random.choice(self.backgrounds)
            # fix bug where the list and not a string is returned by bg_random
            if (isinstance(background, kivy.properties.ObservableList)):
                return self.backgrounds_random()
            return background
        else:
            return self.pixel

    def aphorism_copy(self):
        if not self.current_aphorism:
            return
        A = self.current_aphorism
        tpl = "\"{aphorism}\"\n  -- {author}\n\n({source})"
        quote = tpl.format(aphorism = A.aphorism, author = A.author, source = A.source)
        Clipboard.put(quote, 'TEXT')
        Clipboard.put(quote, 'text/plain;charset=utf-8')
        Clipboard.put(quote, 'UTF8_STRING')
        w = self.WidgetCopy()
        w.textarea_copy.text = quote
        w.textarea_copy.select_all()
        w.open()

    class WidgetCopy(Popup):
        textarea_copy = ObjectProperty()


    def aphorism_get(self, id = None):
        try:
            if id is None:
                for A in Aphorism.select().order_by(fn.Random()).limit(1):
                    return A
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

    def aphorism_widget(self, A):
        container = app.root.ids.aphorism_container
        container.clear_widgets()
        widget = Factory.WidgetAphorism()
        widget.set(A)
        container.add_widget(widget)
        return widget

    def aphorism_show(self, id):
        try:
            A = self.aphorism_get(id)
        except:
            return False
        else:
            widget = self.aphorism_widget(A)
            if int(app.config.get('display', 'bg_enabled')) == 1:
                widget.background_random_set()

        app.root.current = 'Main'
        return A

    def aphorism_random(self):
        container = app.root.ids.aphorism_container
        container.clear_widgets()
        widget = Factory.WidgetAphorism()
        A = widget.random_set()
        container.add_widget(widget)
        return A

    def aphorism_new(self):
        self.FormNew().open()

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
                    app.aphorism_show(a.id)
                    self.dismiss()
            else:
                self.ids.aphorism.focus = True

    def aphorism_edit(self):
        id = app.selected_id
        if id > 0:
            try:
                A = self.aphorism_get(id)
            except:
                return False
            else:
                self.aphorism_widget(A)
                widget = self.FormEdit()
                widget.edit(A)
                return widget
            return A

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
                    app.aphorism_show(a.id)
                    self.dismiss()
            else:
                self.ids.aphorism.focus = True

    def aphorism_delete(self):
        id = app.selected_id
        if id > 0:
            try:
                A = self.aphorism_get(id)
            except:
                return False
            else:
                widget = self.FormDelete()
                widget.delete(A)
                return widget
            return A

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
                    app.selected_id = self.aphorism_id
                    self.dismiss()
                    app.root.ids.FormList.list()


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

    files = []
    for root, dirs, files in os.walk('widgets'):
        for file in files:
            if file.endswith('.kv'):
                Builder.load_file(os.path.join(root, file))

    global app
    app = MainApp()
    app.run()
