from nose.tools import *

import aforgizmo

def setup(self):
    print 'SETUP!'

def teardown():
    print 'TEARDOWN!'

def test_basic():
    print 'I RAN!'
