# -*- coding: utf-8 -*-
'''
Pocket Philosopher Database Models
===================================

Models to handle aphorism data
'''

import click
from peewee import *
from datetime import datetime
import json

def get_database():
    import ConfigParser
    config = ConfigParser.RawConfigParser()
    config.read('config.ini')
    file = config.get('database', 'file')
    database = SqliteDatabase(file)

class BaseModel(Model):
    """(Peewee) Base Database model for Aphorisms App"""
    class Meta:
        database = get_database()

class Aphorism(BaseModel):
    """Database model for Aphorisms"""
    author   = CharField()
    source   = CharField()
    aphorism = TextField()
    hashtags = TextField()
    created  = DateTimeField(default=datetime.now)

    def AsHash(self):
        """Return a representation of the object field data as a hash
        hack was required to make bulk insert possible by replacing 'T' in
        isoformat
        """
        data = {
            'id':       self.id,
            'created':  self.created.isoformat().replace('T', ' '),
            'author':   self.author,
            'source':   self.source,
            'aphorism': self.aphorism,
            'hashtags': self.hashtags
        }
        return data

    def ToJSON(self):
        """Return a representation of the object field data as JSON"""
        return json.dumps(self.AsHash(), indent = 4, sort_keys = True)

    def ToOneLine(self, length = 80):
        """Return a string of the object data as a one line string"""
        return "{0}: \"{1}\"".format(self.author, (self.aphorism[:length] + '..') if len(self.aphorism) > length else self.aphorism)


def CreateTables():
    """Create database tables for Aphorisms in SQLite"""
    try:
        Aphorism.create_table()
    except OperationalError:
        click.secho('Aphorism table already exists!', fg = 'red')
    else:
        click.secho('Aphorism table successfully created.', fg = 'green')

if __name__ == "__main__":
    CreateTables()
