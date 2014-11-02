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

# application imports
from peewee import *
from models import Aphorism
