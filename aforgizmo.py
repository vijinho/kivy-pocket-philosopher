'''
Aforgizmo CLI
==============

An App which saves, retrieves, edits and displays aphorisms
'''

import click
import os
import pwd
from peewee import *

# setup config passing storage
class Config(object):
    def __init__(self):
        self.verbose = False
pass_config = click.make_pass_decorator(Config, ensure=True)

@click.group()
@click.option('-v', '--verbose', is_flag=True)
@click.option('-l', '--logfile',
              type=click.File('w'),
              required=False)
@click.option('-dd', '--data-directory',
              type=click.Path(),
              default='data')
@pass_config
def cli(config, verbose, logfile, data_directory):
    config.verbose = verbose
    config.logfile = logfile
    config.username = pwd.getpwuid(os.getuid())[0]

    # set the data directory to 'data' if invalid
    if data_directory is None:
        data_directory = 'data'
    config.data_directory = data_directory
    if (os.path.exists(config.data_directory) is False):
        config.data_directory = 'data'

    # display some verbose information
    if config.verbose:
        click.echo(click.style('Verbose mode: Enabled',
                               fg='white',
                               bold=True,
                               reverse=True,
                               blink=True))
        click.echo(click.style('Data directory: %s' % config.data_directory,
                                fg='yellow'))

@cli.command()
@pass_config
def init(config):
    '''Initialise a clean database of aphorisms.'''
    click.echo(click.style('INITIALISING TO DATABASE NOT YET IMPLEMENTED',
                           fg='red'),
                           file=config.logfile)

@cli.command()
@click.option('-a', '--author',
              prompt='Who are you quoting?',
              help='The author of the aphorism.',
              required=True,
              default='Anonymous')
@click.option('-s', '--source',
              prompt='Where did you source the text?',
              help='The source of the aphorism text.',
              required=False,
              default='Unknown')
@click.option('-text', '--aphorism',
              prompt='Write the aphorism',
              help='The text of the aphorism itself.',
              required=True)
@click.option('-t', '--hashtags',
              prompt='Hashtags',
              help='Hashtags for the aphorism, space or comma separated, '
                   '# symbol optional',
              required=False,
              default='none')
@pass_config
def add(config, author, source, aphorism, hashtags):
    '''Add an aphorism.'''
    click.echo(click.style('SAVING TO DATABASE NOT YET IMPLEMENTED',fg='red'),
                           file=config.logfile)

@cli.command()
@click.option('-id',
              type=int,
              required=True,
              prompt='Aphorism Id',
              help='The aphorism id within the database')
@pass_config
def get(config, id):
    '''Get an aphorism by ID.'''
    click.echo(click.style('LOADING FROM THE DATABASE NOT YET IMPLEMENTED',
                           fg='red'),
                           file=config.logfile)
@cli.command()
@click.option('-id',
              type=int,
              required=True,
              prompt='Aphorism Id',
              help='The aphorism id within the database')
@pass_config
def remove(config, id):
    '''Remove an aphorism by ID.'''
    click.echo(click.style('DELETING FROM THE DATABASE NOT YET IMPLEMENTED',
                           fg='red'),
                           file=config.logfile)
@cli.command()
@pass_config
def random(config):
    '''Get a random aphorism.'''
    click.echo(click.style('LOADING A RANDOM APHORISM FROM THE DATABASE NOT '
                           'YET IMPLEMENTED',
                           fg='red'),
                           file=config.logfile)
@cli.command()
@click.option('-sf', '--source-file',
              required=True,
              help='The full path to the source file.',
              prompt='Source File',
              default='data/aphorisms.json')
@click.option('-if', '--input-format',
              type=click.Choice(['json', 'csv']),
              default='json',
              prompt='Input Format (json|csv)',
              help='The input format of the source file.')
@pass_config
def insert(config, source_file, input_format):
    '''Insert aphorisms by file.'''
    click.echo(click.style('IMPORTING APHORISMS TO THE DATABASE NOT '
                           'YET IMPLEMENTED',
                           fg='red'),
                           file=config.logfile)
@cli.command()
@click.option('-tf', '--target-file',
              type=click.File('w'),
              required=True,
              help='The full path to the output target file.',
              prompt='Target Output File',
              default='data/dumpfile.json')
@click.option('-of', '--output-format',
              type=click.Choice(['text', 'json', 'csv', 'html']),
              default='json',
              prompt='Output Format (json|csv|txt|html)',
              help='The output format of the data.')
@pass_config
def dump(config, target_file, output_format):
    '''Dump all aphorisms to a file.'''
    click.echo(click.style('OUTPUT OF APHORISMS FROM THE DATABASE NOT '
                           'YET IMPLEMENTED',
                           fg='red'),
                           file=config.logfile)
@cli.command()
@pass_config
def list(config):
    '''Show all aphorisms.'''
    click.echo(click.style('LISTONG OF APHORISMS FROM THE DATABASE NOT '
                           'YET IMPLEMENTED',
                           fg='red'),
                           file=config.logfile)
@cli.command()
@click.option('-t', '--tag',
              required=True,
              prompt='Search Tag',
              help='The tag to search for.')
@pass_config
def search(config, tag):
    '''Search for an aphorism by tag.'''
    click.echo(click.style('SEARCHING FOR APHORISMS IN THE DATABASE NOT '
                           'YET IMPLEMENTED',
                           fg='red'),
                           file=config.logfile)
if __name__ == '__main__':
    cli()
