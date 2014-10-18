'''
Aforgizmo Database Models
=========================

Models to handle aphorism data
'''

from peewee import *
import click
import datetime

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
