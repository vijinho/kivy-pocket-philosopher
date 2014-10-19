'''
Aforgizmo Database Models
=========================

Models to handle aphorism data
'''

from peewee import *
import click
import datetime
import json

database = SqliteDatabase('data/aphorisms.db')

class BaseModel(Model):
    '''(Peewee) Base Database model for Aphorisms App'''
    class Meta:
        database = database

class Aphorism(BaseModel):
    '''Database model for Aphorisms'''
    author = CharField()
    source = CharField()
    aphorism = TextField()
    hashtags = TextField()
    created = DateTimeField(default=datetime.datetime.now)

    def AsHash(self):
        '''Return a representation of the object field data as a hash'''
        data = {
            'id': self.id,
            'created': self.created.isoformat(),
            'author': self.author,
            'source': self.source,
            'aphorism': self.aphorism,
            'hashtags': self.hashtags
        }
        return data

    def ToJSON(self):
        '''Return a representation of the object field data as JSON'''
        return json.dumps(self.AsHash(), indent=4, sort_keys=True)

def CreateTables():
    '''Create database tables for Aphorisms in SQLite'''
    try:
        Aphorism.create_table()
    except OperationalError:
        click.echo(click.style('Aphorism table already exists!', fg='red'))
    else:
        click.echo(click.style('Aphorism table successfully created.',
                               fg='green'))
    finally:
        pass

if __name__ == "__main__":
    CreateTables()
