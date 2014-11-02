# -*- coding: utf-8 -*-
'''
Aforgizmo GUI
=============

An App which saves, retrieves, edits and displays aphorisms

This app is written in Python using the Kivy library for cross-platform support (Android, IOS, Windows, Linux, Mac OSX).  See http://kivy.org/docs/guide/packaging.html for instructions on packaging the application for the different platforms.
'''
__title__ = 'Pocket Philosopher'
__version__ = '1.0.3'
__author__ = 'vijay.mahrra@gmail.com'

import kivy
kivy.require('1.8.0')
from kivy import platform
from kivy.app import App
from kivy.lang import Builder
from kivy.config import Config
from kivy.factory import Factory
from kivy.core.text import LabelBase
from kivy.core.clipboard import Clipboard
from kivy.network.urlrequest import UrlRequest
from kivy.properties import ObjectProperty, ListProperty, NumericProperty, StringProperty
from kivy.uix.screenmanager import ScreenManager, NoTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.listview import ListItemButton, ListView
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.clock import Clock

import os
import shutil
import imghdr
import random
import re
import time
import json
from peewee import *
from models import Aphorism


class AppError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class MyBoxLayout(BoxLayout):
    pass


class MyGridLayout(GridLayout):
    pass


class FormListActions(MyGridLayout):
    pass


class MyLabel(Label):
    pass


class MyScreenManager(ScreenManager):
    """Set the background image for the app screens"""
    background_image = ObjectProperty(
        Image(
            source='assets/img/bg/background.png'))


class MyImage(Image):
    """Some extensions to the default image class"""
    def __init__(self, **kwargs):
        super(MyImage, self).__init__()

    def texture_width(self):
        """Return the actual width of the loaded image source (texture)"""
        return self.texture.size[0]

    def texture_height(self):
        """Return the actual height of the loaded image source (texture)"""
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
    background_color_normal = ListProperty([0.5, 0.5, 0.5, 0.5])
    background_color_down = ListProperty([0.9, 0.9, 0.9, 0.9])

    def __init__(self, **kwargs):
        super(MyButton, self).__init__(**kwargs)
        self.background_color = self.background_color_normal

    def on_press(self):
        self.background_color = self.background_color_down

    def on_release(self):
        self.background_color = self.background_color_normal


class ImageClickable(ButtonBehavior, MyImage):
    """An image which acts like a button"""
    source_up = ObjectProperty(Image(source='assets/img/pixel.png'))
    source_down = ObjectProperty(Image(source='assets/img/pixel.png'))

    def __init__(self, **kwargs):
        super(ImageClickable, self).__init__(**kwargs)
        self.source = 'assets/img/pixel.png'

    def on_press(self):
        self.source = self.source_down

    def on_release(self):
        self.source = self.source_up


class Notify(ButtonBehavior, BoxLayout):
    """Display a floating user notification on the current screen"""
    msg = StringProperty()
    icon = StringProperty()

    def __init__(self, **kwargs):
        super(Notify, self).__init__()
        self.type = ''
        self.text = ''

    def message(self, msg_type, msg):
        """Show the message using an icon named after the given type"""
        self.msg_type = msg_type
        self.msg = msg
        self.icon = 'assets/img/icons/notify/' + msg_type + '.png'


class FormTextInput(TextInput):
    """TextInput which checks against a regexp and length of input"""
    max_chars = 255
    valid_chars = ''

    def insert_text(self, substring, from_undo=False):
        """Check against regexp of characters"""
        if len(self.valid_chars) > 0:
            valid_chars = '[^' + self.valid_chars + ']'
            pat = re.compile(valid_chars)
            s = re.sub(valid_chars, '', substring)
        else:
            s = substring
        super(FormTextInput, self).insert_text(s, from_undo=from_undo)
        self.validate(self.max_chars)

    def validate(self, max_chars):
        """Check the string length of text input"""
        if int(max_chars) <= 0:
            max_chars = self.max_chars
        s = self.text
        self.text = (s[:max_chars]) if len(s) > max_chars else s


class SearchFormTextInput(FormTextInput):
    max_chars = 30
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


class MyListItemButton(ListItemButton):
    selected_id = NumericProperty()
    aphorism = ListProperty()

    def pressed(self, id):
        app.selected_id = id
        self.selected_id = id
        if self.is_selected:
            app.root.ids.FormList.ids.form_list_actions.clear_widgets()


class FormSearch(MyBoxLayout):
    results = ObjectProperty()

    class ButtonSearchResults(MyListItemButton):
        pass

    def search(self, text):
        """Search the aphorisms in the database by a text string"""
        results = []
        try:
            if len(str(text)) > 2:
                for a in Aphorism.select().where(
                        Aphorism.aphorism.contains(text) |
                        Aphorism.author.contains(text) |
                        Aphorism.source.contains(text) |
                        Aphorism.tags.contains(text)).order_by(Aphorism.author, Aphorism.source):
                    results.append([a.id, a.ToOneLine(40)])
                app.current_search = text
            self.results.item_strings = results
            del self.results.adapter.data[:]
            self.results.adapter.data.extend(results)
            self.results._trigger_reset_populate()
        except Exception as e:
            app.notify(
                'warning',
                'Could not query the database for matching aphorisms.')
            app.notify('error', str(e))

    def args_converter(self, index, data_item):
        id, quote = data_item
        return {'aphorism': (id, quote)}


class FormList(MyBoxLayout):
    results = ObjectProperty()

    class ButtonListResults(MyListItemButton):
        pass

    def list(self):
        """List all database rows"""
        results = []
        try:
            for a in Aphorism.select().order_by(
                    Aphorism.author, Aphorism.source):
                results.append([a.id, a.ToOneLine(40)])
            self.results.item_strings = results
            del self.results.adapter.data[:]
            self.results.adapter.data.extend(results)
            self.results._trigger_reset_populate()
        except:
            app.notify(
                'error',
                'Could not retrieve the aphorisms from the database.')

    def args_converter(self, index, data_item):
        id, quote = data_item
        return {'aphorism': (id, quote)}


class WidgetAphorism(MyBoxLayout):
    """The widget that displays the aphorism on the home screen"""
    pixel = 'assets/img/pixel.png'
    aphorism = ObjectProperty()

    def set(self, A, style=None):
        """Set the widgets current aphorism"""
        if isinstance(A, Aphorism):
            self.aphorism = A
            app.current_aphorism = A
            self.style(style, A)

    def style(self, style=None, A=None):
        """Display the aphorism text in a given style"""
        if int(app.config.get('display', 'bg_enabled')) == 1:
            app.background_set(app.background_get_random())
        if isinstance(A, Aphorism):
            self.aphorism = A
        else:
            A = self.aphorism
        if style is None:
            tpl = """\"[b]{aphorism}[/b]\"\n\n    -- [i]{author}[/i]"""
            formatted = tpl.format(aphorism=A.aphorism, author=A.author)
            self.ids.quote.text = formatted
        elif style == 'full':
            tpl = """\"[b]{aphorism}[/b]\"\n\n    -- [i]{author}[/i]\n\n{source}"""
            formatted = tpl.format(
                aphorism=A.aphorism,
                author=A.author,
                source=A.source)
            self.ids.quote.text = formatted

    def screenshot(self):
        """
        only works from v 1.8.1
        http://stackoverflow.com/questions/22753306/export-to-png-function-of-kivy-gives-error
        :return:
        """
        filename = "data/screenshot-{0}.png".format(
            time.strftime("%Y%m%d-%H%M%S"))
        self.export_to_png(filename)


class Main(MyScreenManager):
    backup_results = ObjectProperty()

    def __init__(self, **kwargs):
        self.transition = NoTransition()
        super(Main, self).__init__()


class MainApp(App):
    pixel = 'assets/img/pixel.png'
    use_kivy_settings = False
    backgrounds = ListProperty()
    current_background = StringProperty()
    current_search = StringProperty()
    selected_id = NumericProperty()
    folder = StringProperty()
    data_folder = StringProperty()
    notifications_queue = []

    def on_selected_id(self, *args):
        """Used to store the currently viewed/chosen aphorism id"""
        id = int(self.selected_id)
        if id > 0:
            actions = app.root.ids.FormList.ids.form_list_actions
            actions.clear_widgets()
            actions.add_widget(FormListActions())

    def __init__(self):
        self.title = 'Pocket Philosopher'
        self.icon = 'assets/img/icon.png'
        self.folder = os.path.dirname(os.path.abspath(__file__))
        # make sure android uses the /sdcard folder instead of data/
        if platform == 'android':
            path = '/sdcard/pocketphilosopher/'
            copyfiles = ['aphorisms.json', 'aphorisms-authors.json']
            if not os.path.exists(path):
                os.mkdir(path)
            for f in copyfiles:
                shutil.copyfile(os.path.join('data', f), os.path.join(path, f))
            self.data_folder = path
        else:
            self.data_folder = os.path.join(self.folder, 'data')

        Factory.register('Notify', cls=Notify)
        App.__init__(self)

    def build(self):
        Factory.register('WidgetAphorism', cls=WidgetAphorism)
        return Main()

    def build_config(self, config):
        if platform == 'android':
            if os.path.exists('/sdcard/Pictures'):
                config.setdefaults('display', {
                    'bg_folder': '/sdcard/DCIM'
                })
            elif os.path.exists('/sdcard/Snapseed'):
                config.setdefaults('display', {
                    'bg_folder': '/sdcard/Snapseed'
                })
            else:
                config.setdefaults('display', {
                    'bg_folder': '/sdcard/Pictures'
                })
        else:
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
        config.setdefaults('editor', {
            'default_tags': ''
        })

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
                if value == 1:
                    self.backgrounds_refresh()
                    app.background_set()
                else:
                    app.background_set(self.pixel)

    def on_start(self):
        """
        Fired when the application is being started (before the runTouchApp() call.
        """
        self.setup_database()
        self.backgrounds_refresh()
        self.aphorism_random()
        return True

    def on_stop(self):
        """
        Fired when the application stops.
        """
        self.backgrounds_cleanup()
        return True

    def on_pause(self):
        """ For phones/tablets (experimental feature)
        Fired when the application is paused by the OS.
        Warning
        Both on_pause and on_stop must save important data because after
        on_pause is called, on_resume may not be called at all.
        """
        self.backgrounds_refresh()
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
        """Initial setup for the application/database if empty or not existing"""
        try:
            for a in Aphorism.select().limit(1):
                pass
        except Exception:
            pass

        if 'a' not in locals():
            try:
                try:
                    Aphorism.create_table()
                except:
                    app.notify(
                        'error',
                        'Could not create the database table.  Please check the file permissions in the [b]data[/b] folder.')

                with open('data/aphorisms.json') as json_file:
                    json_data = json.load(json_file)
                Aphorism.insert_many(json_data).execute()
            except Exception:
                app.notify(
                    'error',
                    'Could not load in the initial aphorism data - check that the [b]data/aphorisms.json[/b] file is readable and valid.')

    def notify(self, msg_type, msg, screen=None):
        """Create and display a floating user notification box and timer to remove it"""
        if screen is None:
            screen = app.root.current
        id = 'notifications_' + str(screen)
        w = Factory.Notify()
        w.message(msg_type, msg)
        wid = 'n' + str(random.randint(1000, 20000))
        w.id = wid
        exec 'app.root.ids.' + id + '.add_widget(w)'
        exec 'i = app.root.ids.' + id
        exec 'kids = app.root.ids.' + id + '.children'
        for k in kids:
            if k.id == wid:
                self.notifications_queue.append(id + '.' + k.id)
                Clock.schedule_once(self.remove_notification, 8)

    def remove_notification(self, dt):
        """Callback from the clock to remove a given floating user notification"""
        if len(self.notifications_queue) > 0:
            x = self.notifications_queue.pop(0)
            x = x.split('.')
            id, wid = x
            exec 'i = app.root.ids.' + id
            exec 'kids = app.root.ids.' + id + '.children'
            for k in kids:
                if k.id == wid:
                    i.remove_widget(k)

    def form_wipe(self):
        """open the clear database popup"""
        widget = self.FormWipe()
        widget.wipe()

    class FormWipe(Popup):
        """popup window for database wiping"""
        def wipe(self):
            """open the form"""
            self.open()

        def wipe_action(self):
            """clear the database"""
            try:
                app.db_backup()
                Aphorism.drop_table()
                Aphorism.create_table()
            except Exception as e:
                app.notify('error', 'Failed clearing the database.')
                app.root.backup_results.text += "Failed clearing the database.\nError: (" + str(
                    e) + ")\n\n"
            else:
                app.notify('success', 'Successfully cleared the database!')
                app.root.backup_results.text += "Successfully cleared the database!" + \
                    "\n\n"

            self.dismiss()

    def db_backup(self, path='data'):
        """backup the database to the given path as a json file"""
        data = []
        for a in Aphorism.select().order_by(Aphorism.author, Aphorism.source):
            savedata = a.AsHash()
            del(savedata['id'])
            data.append(savedata)
        try:
            filename = "aphorisms-{0}.json".format(
                time.strftime("%Y%m%d-%H%M%S"))
            with open(os.path.join(path, filename), "w") as fp:
                fp.write(json.dumps(data, fp, indent=4, sort_keys=True))
            app.notify('success', 'Database backup successful!')
        except:
            app.notify('warning', 'Could not backup the database!')

    def form_backup(self):
        """open the backup popup screen"""
        self.FormBackup().open()

    class FormBackup(Popup):
        """perform a backup of the data to the given path and filename"""
        def backup(self, path, filename):
            if filename and len(filename) > 0:
                filename = os.path.join(path, filename[0])
                if (os.path.isdir(filename)):
                    path = filename
            try:
                app.db_backup(path)
            except Exception as e:
                app.notify('error', 'Backup Failed!')
                app.root.backup_results.text += "Failed backup of the file:\n" + \
                    path + "\nError: (" + str(e) + ")\n\n"
            else:
                app.root.backup_results.text += "Successfully backed up to the file:\n" + \
                    path + "\n\n"

            self.dismiss()

    def form_import(self):
        self.FormImport().open()

    class FormImport(Popup):
        """Restore the imported json data file"""
        def restore(self, path, filename):
            if filename and len(filename) > 0:
                try:
                    filename = os.path.join(path, filename[0])
                    with open(filename) as json_file:
                        json_data = json.load(json_file)
                    Aphorism.insert_many(json_data).execute()
                except Exception as e:
                    app.notify('error', 'Import Failed!')
                    app.root.backup_results.text += "Failed import of the file:\n" + \
                        filename + "\nError: (" + str(e) + ")\n\n"
                else:
                    app.notify('success', 'Import Successful!')
                    app.root.backup_results.text += "Successfully imported the backup file:\n" + \
                        filename + "\n\n"

                self.dismiss()

    def form_import_url(self):
        self.FormImportUrl().open()

    class FormImportUrl(Popup):
        url = StringProperty()

        def import_url(self, url):
            """import data from the given json file url"""
            url = url.strip("\r\n\t\s ")
            self.url = url
            if len(url) > 0:
                try:
                    filename = "aphorisms_url-{0}.json".format(
                        time.strftime("%Y%m%d-%H%M%S"))
                    path = os.path.join(
                        os.path.realpath(
                            app.data_folder.strip("\r\n\t\s ")),
                        filename)
                    UrlRequest(url, on_success=self.download)
                except Exception as e:
                    app.notify('error', 'Import from URL failed!')
                    app.root.backup_results.text += "Failed import of the URL:\n" + \
                        url + "\nError: (" + str(e) + ")\n\n"
                else:
                    app.notify('warning', 'Importing the data...')
                    app.root.backup_results.text += "Importing the data from the URL:\n" + \
                        url + "\n\n"
                self.dismiss()
            else:
                app.notify('warning', 'No URL was entered!')
                self.dismiss()

        def download(self, r, data):
            """process data that was downloaded"""
            if len(data) > 0:
                try:
                    Aphorism.insert_many(data).execute()
                except:
                    app.notify('error', 'Import data from URL successful!')
                    app.notify('error', msg)
                    app.root.backup_results.text += msg + "\n\n"
                else:
                    msg = 'Import data from URL successful!'
                    app.notify('success', msg)
                    app.root.backup_results.text += msg + "\n\n"
            else:
                msg = 'Could not download the data.'
                app.notify('warning', msg)
                app.root.backup_results.text += msg + "\n\n"


    def form_download_backgrounds(self):
        self.FormBackgroundUrl().open()

    class FormBackgroundUrl(Popup):
        url = StringProperty()

        def import_backgrounds(self, url):
            """Import backgrounds listed in a txt file at a URL"""
            url = url.strip("\r\n\t\s ")
            self.url = url
            if len(url) > 0:
                try:
                    UrlRequest(url, on_success=self.download)
                except Exception as e:
                    app.notify(
                        'error',
                        'Import background images from URL failed!')
                    app.root.backup_results.text += "Failed import of the URL:\n" + \
                        url + "\nError: (" + str(e) + ")\n\n"
                else:
                    app.root.backup_results.text += "Importing the images from URL:\n" + \
                        url + "\n\n"
                self.dismiss()
            else:
                app.notify('warning', 'No URL was entered!')
                self.dismiss()

        def download(self, r, data):
            """Download the image URLS/files from the text file"""
            error_text = 'No valid images were found to download.'
            if len(data) > 0:
                urls = []
                base_url, file = os.path.split(self.url)

                for line in data.splitlines():
                    line = line.strip("\r\n\t\s ")
                    if line.endswith('.jpg') or line.endswith(
                            '.jpeg') or line.endswith('.tiff') or line.endswith('.png'):
                        if len(line) > 0:
                            if line[:4] == 'http':
                                url = line
                            else:
                                url = base_url + '/' + line
                        urls.append(url)

                downloads = 0
                if len(urls) > 0:
                    for url in urls:
                        base_url, filename = os.path.split(url)
                        path = os.path.join(
                            os.path.realpath(
                                app.config.get(
                                    'display',
                                    'bg_folder')),
                            filename)
                        if os.path.isfile(path):
                            pass
                        else:
                            try:
                                UrlRequest(
                                    url,
                                    file_path=path,
                                    on_success=self.download_ok)
                            except Exception as e:
                                try:
                                    os.remove(path)
                                except:
                                    pass
                                print e
                            else:
                                downloads = downloads + 1

                    if downloads > 0:
                        app.notify(
                            'warning',
                            'Now downloading {0} background images... Please go make a cup of tea and be patient!'.format(downloads))
                        app.notify(
                            'success',
                            'You will be notified after each successful download.'.format(downloads))
                        app.backgrounds_refresh()
                    else:
                        app.notify('warning', error_text)
                else:
                    app.notify('warning', error_text)
            else:
                app.notify('warning', error_text)

        def download_ok(self, req, results):
            """Callback floating user message if download was OK"""
            base_url, file = os.path.split(req.url)
            app.notify(
                'success',
                'Downloaded background image [b]{0}[/b] successfully.'.format(file))
            app.root.backup_results.text += 'Downloaded background image {0} successfully.'.format(
                file)
            app.backgrounds_refresh()


    def get_rst_doc(self, doc):
        """a crash happened on android when using a KV file or importing at the top"""
        from kivy.uix.rst import RstDocument
        return RstDocument(source=doc)

    def about(self):
        self.WidgetAbout().open()

    class WidgetAbout(Popup):

        def __init__(self, **kwargs):
            super(MainApp.WidgetAbout, self).__init__()
            self.ids.rst_doc.add_widget(app.get_rst_doc('docs/about.rst'))

    def help(self):
        self.WidgetHelp().open()

    class WidgetHelp(Popup):
        """help screen popup"""
        def __init__(self, **kwargs):
            super(MainApp.WidgetHelp, self).__init__()
            self.ids.rst_doc.add_widget(app.get_rst_doc('docs/help.rst'))

    def backgrounds_refresh(self):
        """
        Get a the list of file paths to bg images
        :return: list of the bg image path strings
        """
        self.backgrounds = []
        try:
            for root, dirs, files in os.walk(
                    self.config.get('display', 'bg_folder')):
                for file in files:
                    if file.endswith('.jpg') or file.endswith(
                            '.png') or file.endswith('.jpeg') or file.endswith('.tiff'):
                        path = os.path.join(root, file)
                        if platform == 'android':
                            self.backgrounds.append(path)
                        else:
                            if imghdr.what(path) in ('jpeg', 'png', 'tiff'):
                                self.backgrounds.append(path)
        except:
            pass

        return self.backgrounds

    def backgrounds_cleanup(self):
        """remove invvalid image files from the download folder if not running under android"""
        if not platform == 'android':
            try:
                for root, dirs, files in os.walk(
                        self.config.get('display', 'bg_folder')):
                    for file in files:
                        if file.endswith('.jpg') or file.endswith(
                                '.png') or file.endswith('.jpeg') or file.endswith('.tiff'):
                            path = os.path.join(root, file)
                            if imghdr.what(path) in ('jpeg', 'png', 'tiff'):
                                pass
                            else:
                                os.remove(path)
            except:
                pass

    def background_set(self, path=None):
        """set the current background image"""
        if path is None:
            path = app.background_get_random()
        if imghdr.what(path) in ('jpeg', 'png', 'tiff'):
            app.root.ids.background.source = path
            app.current_background = path
        else:
            app.root.ids.background.source = self.pixel
        app.root.ids.background.rescale(app.root.width, app.root.height)

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
        """copy the current aphorism to the clipboard"""
        if not self.current_aphorism:
            return
        A = self.current_aphorism
        tpl = "\"{aphorism}\"\n  -- {author}\n\n({source})"
        quote = tpl.format(
            aphorism=A.aphorism,
            author=A.author,
            source=A.source)
        Clipboard.put(quote, 'TEXT')
        Clipboard.put(quote, 'text/plain;charset=utf-8')
        Clipboard.put(quote, 'UTF8_STRING')
        w = self.WidgetCopy()
        w.textarea_copy.text = quote
        w.open()

    class WidgetCopy(Popup):
        textarea_copy = ObjectProperty()
        pass

    def aphorism_get(self, id=None):
        """get an aphorism by its ID"""
        try:
            if id is None:
                for A in Aphorism.select().order_by(fn.Random()).limit(1):
                    return A
            id = int(id)
        except:
            pass
        else:
            if id:
                try:
                    A = Aphorism.get(Aphorism.id == id)
                except:
                    return False
                else:
                    return A

    def new_aphorism_widget(self, A):
        app.root.ids.aphorism_container.clear_widgets()
        widget = Factory.WidgetAphorism()
        widget.set(A)
        app.root.ids.aphorism_container.add_widget(widget)

    def aphorism_show(self, id):
        """display an aphorism by ID"""
        try:
            A = self.aphorism_get(id)
        except:
            app.notify('warning', 'Could show the aphorism!')
        else:
            self.new_aphorism_widget(A)
        app.root.current = 'Main'

    def aphorism_random(self):
        """Choose a random aphorism and display it"""
        app.root.ids.aphorism_container.clear_widgets()
        try:
            A = app.aphorism_get()
            widget = Factory.WidgetAphorism()
            widget.set(A)
            app.root.ids.aphorism_container.add_widget(widget)
            app.selected_id = A.id
        except:
            app.notify('error', 'Could show the initial aphorism!')

    def aphorism_new(self):
        self.FormNew().open()

    class FormNew(Popup):
        """Add a new aphorism"""
        def new(self):
            data = {
                'aphorism': self.ids.aphorism.text,
                'author': self.ids.author.text,
                'source': self.ids.source.text,
                'tags': self.ids.tags.text
            }

            # set required fields if empty
            if len(data['author']) == 0:
                data['author'] = app.config.get('editor', 'default_author')
                if len(data['author']) == 0:
                    data['author'] = 'Anonymous'
                self.ids.author.text = data['author']

            if len(data['source']) == 0:
                data['source'] = app.config.get('editor', 'default_source')
                if len(data['source']) == 0:
                    data['source'] = 'Unknown'
                self.ids.source.text = data['source']

            if len(data['tags']) == 0:
                data['tags'] = app.config.get('editor', 'default_tags')
                if len(data['tags']) == 0:
                    data['tags'] = ''
                self.ids.source.text = data['tags']

            # add aphorism is required fields valid
            if len(data['aphorism']) > 0:
                try:
                    a = Aphorism(
                        aphorism=data['aphorism'],
                        author=data['author'],
                        source=data['source'],
                        tags=data['tags'])
                    a.save()
                except:
                    app.notify('warning', 'Could not add the aphorism!')
                else:
                    app.selected_id = A.id
                    app.aphorism_show(a.id)
                    app.notify('success', 'Aphorism added successfully!')
                    self.dismiss()
            else:
                self.ids.aphorism.focus = True

    def aphorism_edit(self):
        id = app.selected_id
        if id > 0:
            try:
                A = self.aphorism_get(id)
            except:
                app.notify('warning', 'Could get the aphorism!')
            else:
                self.new_aphorism_widget(A)
                widget = self.FormEdit()
                widget.edit(A)

    class FormEdit(Popup):
        """Edit an existing aphorism"""
        aphorism_id = NumericProperty()

        def edit(self, A):
            """show the aphorism being edited"""
            if isinstance(A, Aphorism):
                self.aphorism_id = A.id
                self.ids.aphorism.text = A.aphorism
                self.ids.author.text = A.author
                self.ids.source.text = A.source
                self.ids.tags.text = A.tags
                self.open()

        def edit_action(self):
            """process the submitted form"""
            data = {
                'id': int(self.aphorism_id),
                'aphorism': self.ids.aphorism.text,
                'author': self.ids.author.text,
                'source': self.ids.source.text,
                'tags': self.ids.tags.text
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
                        id=data['id'],
                        aphorism=data['aphorism'],
                        author=data['author'],
                        source=data['source'],
                        tags=data['tags'])
                    a.save()
                except:
                    app.notify('warning', 'Could not edit the aphorism!')
                else:
                    app.notify('success', 'Edited the aphorism successfully!')
                    app.root.ids.FormList.list()
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
        """delete an aphorism after confirmation"""
        aphorism_id = NumericProperty()

        def delete(self, A):
            if isinstance(A, Aphorism):
                self.aphorism_id = A.id
                tpl = "\"[b]{aphorism}[/b]\"\n  -- [i]{author}[/i]\n\n({source})"
                self.ids.aphorism_text.text = tpl.format(
                    aphorism=A.aphorism,
                    author=A.author,
                    source=A.source,
                    tags=A.tags
                )
                self.open()

        def delete_action(self):
            if self.aphorism_id > 0:
                try:
                    a = Aphorism.get(Aphorism.id == self.aphorism_id)
                    a.delete_instance()
                except:
                    app.notify('error', 'Could not delete the aphorism!')
                else:
                    app.selected_id = self.aphorism_id
                    self.dismiss()
                    app.notify('success', 'Deleted the aphorism!')
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
