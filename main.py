'''
Aforgizmo GUI
=============

An App which saves, retrieves, edits and displays aphorisms

This app is written in Python using the Kivy library for cross-platform support (Android, IOS, Windows, Linux, Mac OSX).  See http://kivy.org/docs/guide/packaging.html for instructions on packaging the application for the different platforms.
'''
import kivy
kivy.require('1.8.0')
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty

from peewee import *
import models

class MainWindow(BoxLayout):
    '''Main UI Widget
    '''
    quote_text = ObjectProperty()
    button_previous = ObjectProperty()
    button_next = ObjectProperty()
    button_random = ObjectProperty()

    def aphorism_button_press(self, *args):
        action = args[0]
        if action == 'next':
            pass
        elif action == 'previous':
            pass
        elif action == 'random':
            for a in models.Aphorism.select().order_by(fn.Random()).limit(1):
                self.quote_text.text = '"{0}" -- {1}\n({2})'.format(
                                            a.aphorism, a.author, a.source)
        else:
            pass

class MainApp(App):
    '''Main Program
    '''
    def __init__(self):
        App.__init__(self)

    def build(self):
        self.title = 'Aforgizmo Aphorisms'
        return MainWindow()

if __name__ == '__main__':
    MainApp().run()
