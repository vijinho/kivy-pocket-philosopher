'''
Aforgizmo GUI
=============

An App which saves, retrieves, edits and displays aphorisms

This app is written in Python using the Kivy library for cross-platform support (Android, IOS, Windows, Linux, Mac OSX).  See http://kivy.org/docs/guide/packaging.html for instructions on packaging the application for the different platforms.
'''
# python core/system imports
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
from plyer import tts

import os
import shutil
import imghdr
import random
import re
import time
import json
from peewee import *
from models import Aphorism

