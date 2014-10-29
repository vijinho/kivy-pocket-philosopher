# -*- coding: utf-8 -*-
'''
Pocket Philosopher CLI
======================

An App which saves, retrieves, edits and displays aphorisms
'''

import click
import json
from peewee import fn
from models import Aphorism

# setup config passing storage
class Config(object):
    def __init__(self):
        self.verbose = False

pass_config = click.make_pass_decorator(Config, ensure = True)

@click.group()
@click.option('-v', '--verbose', is_flag = True)
@click.option('-l', '--logfile', type = click.File('w'), required = False)
@pass_config
def cli(config, verbose, logfile):
    config.verbose = verbose
    config.logfile = logfile
    if config.verbose:
        click.secho('Verbose mode: Enabled',
                    fg = 'white', bold = True, reverse = True, blink = True)

@cli.command()
@click.option('-a', '--author',
              prompt   = 'Who are you quoting?',
              help     = 'The author of the aphorism.',
              default  = '(Anonymous)',
              required = True)
@click.option('-s', '--source',
              prompt   = 'Where did you source the text?',
              help     = 'The source of the aphorism text.',
              default  = '(Unknown)',
              required = False)
@click.option('-text', '--aphorism',
              prompt   = 'Write the aphorism',
              help     = 'The text of the aphorism itself.',
              required = True)
@click.option('-t', '--tags',
              prompt   = 'Hashtags',
              help     = 'Hashtags for the aphorism, space or comma separated, '
                   '# symbol optional',
              default  = 'none',
              required = False)
@pass_config
def add(config, author, source, aphorism, tags):
    """Add an aphorism."""
    try:
        a = Aphorism(
            author   = author,
            source   = source,
            aphorism = aphorism,
            tags = tags)
        a.save()
    except Exception:
        click.echo(click.style('Failed saving the aphorism!', fg = 'red'),
                   file = config.logfile)
    else:
        click.echo(click.style('Saved the aphorism successfully.',
                   fg = 'green'),
                   file = config.logfile)

@cli.command()
@click.option('-id',
              type     = int,
              prompt   = 'Aphorism Id',
              help     = 'The aphorism id within the database',
              required = True)
@pass_config
def show(config, id):
    """Show an aphorism by ID for display."""
    try:
        a = Aphorism.get(Aphorism.id == id)
    except Exception as e:
        click.echo(click.style("Exception: %s" % e, fg = 'yellow'),
                   file = config.logfile)
        click.echo(click.style('Failed get the aphorism!', fg = 'red'),
                   file = config.logfile)
    else:
        click.secho('"%s"' % a.aphorism, fg = 'white', bold = True)
        click.secho(' -- %s' % a.author, fg = 'green')
        click.secho('(%s)'   % a.source, fg = 'yellow')

@cli.command()
@click.option('-id',
              type     = int,
              prompt   = 'Aphorism Id',
              help     = 'The aphorism id within the database',
              required = True)
@click.option('-of', '--output-format',
              type     = click.Choice(['text', 'json', 'csv', 'html']),
              default  = 'json',
              prompt   = 'Output Format (json|csv|txt|html)',
              help     = 'The output format of the data.')
@pass_config
def get(config, id, output_format):
    """Get an aphorism by ID."""
    if output_format == 'json':
        try:
            a = Aphorism.get(Aphorism.id == id)
        except Exception as e:
            click.echo(click.style("Exception: %s" % e, fg = 'yellow'),
                       file = config.logfile)
            click.echo(click.style('Failed get the aphorism!', fg = 'red'),
                       file = config.logfile)
        else:
            click.echo(a.ToJSON())
    else:
        click.echo(click.style("Output format '%s' not yet implemented." %
                               output_format, fg = 'red'), file = config.logfile)

@cli.command()
@click.option('-id',
              type     = int,
              prompt   = 'Aphorism Id',
              help     = 'The aphorism id within the database',
              required = True)
@pass_config
def remove(config, id):
    """Remove an aphorism by ID."""
    try:
        a = Aphorism.get(Aphorism.id == id)
        click.secho('"%s"'   % a.aphorism, fg = 'white', bold = True)
        click.secho(' -- %s' % a.author,   fg = 'green')
        click.secho('(%s)'   % a.source,   fg = 'yellow')
        click.echo('Are you sure you want to delete this? [yn] ', nl=False)
        c = click.getchar()
        click.echo()
        if c == 'y':
            a.delete_instance()
        else:
            raise Exception("Delete cancelled!")
    except Exception as e:
        click.echo(click.style("Exception: %s" % e, fg = 'yellow'),
                   file = config.logfile)
        click.echo(click.style('Failed delete the aphorism!',fg = 'red'),
                   file = config.logfile)
    else:
        click.echo(click.style('Deleted the aphorism.',fg = 'green'),
                   file = config.logfile)

@cli.command()
@pass_config
def random(config):
    """Get a random aphorism."""
    for a in Aphorism.select().order_by(fn.Random()).limit(1):
        click.secho('id:%d'  % a.id, fg = 'white')
        click.secho('"%s"'   % a.aphorism, fg = 'white', bold = True)
        click.secho(' -- %s' % a.author, fg = 'green')
        click.secho("(%s)\n" % a.source, fg = 'yellow')

@cli.command()
@click.option('-sf', '--source-file',
              help     = 'The full path to the source file.',
              prompt   = 'Source File',
              default  = 'data/aphorisms.json',
              required = True)
@click.option('-if', '--input-format',
              type    = click.Choice(['json', 'csv']),
              default = 'json',
              prompt  = 'Input Format (json|csv)',
              help    = 'The input format of the source file.')
@pass_config
def insert(config, source_file, input_format):
    """Insert aphorisms by file."""
    if input_format == 'json':
        try:
            with open(source_file) as json_file:
                json_data = json.load(json_file)

        except Exception:
            click.echo(click.style('Unable to import the file', fg = 'red'),
                       file = config.logfile)
        else:
            try:
                Aphorism.insert_many(json_data).execute()
            except Exception as e:
                click.echo(click.style('Unable to insert the data',
                           fg = 'red'), file = config.logfile)
            else:
                click.echo(click.style('Inserted the data successfully.',
                           fg = 'green'), file = config.logfile)
    else:
        click.echo(click.style("Insert format '%s' not yet implemented." %
                               input_format, fg = 'red'), file = config.logfile)

@cli.command()
@click.option('-of', '--output-format',
              type    = click.Choice(['text', 'json', 'csv', 'html']),
              default = 'json',
              prompt  = 'Output Format (json|csv|txt|html)',
              help    = 'The output format of the data.')
@pass_config
def dump(config, output_format):
    """Dump all aphorisms to a file."""
    data = []
    if output_format == 'json':
        for a in Aphorism.select().order_by(Aphorism.author, Aphorism.source):
            savedata = a.AsHash()
            del(savedata['id'])
            data.append(savedata)
        click.echo(json.dumps(data, indent = 4, sort_keys = True))
    else:
        click.echo(click.style("Dump format '%s' not yet implemented." %
                               output_format, fg = 'red'), file = config.logfile)

@cli.command()
@pass_config
def list(config):
    """Show all aphorisms."""
    for a in Aphorism.select().order_by(Aphorism.author, Aphorism.source):
        click.secho('id:%d'  % a.id,       fg = 'white')
        click.secho('"%s"'   % a.aphorism, fg = 'white', bold = True)
        click.secho(' -- %s' % a.author,   fg = 'green')
        click.secho("(%s)\n" % a.source,   fg = 'yellow')

@cli.command()
@click.option('-t', '--tag',
              prompt   = 'Search Tag',
              help     = 'The text to search tags for.',
              required = True)
@pass_config
def search(config, tag):
    """Search for an aphorism by tag."""
    tag = '%%{0}%%'.format(tag)
    for a in Aphorism.select().where(
            Aphorism.tags ** tag).order_by(Aphorism.author, Aphorism.source):
        click.secho('id:%d'  % a.id,       fg = 'white')
        click.secho('"%s"'   % a.aphorism, fg = 'white', bold = True)
        click.secho(' -- %s' % a.author,   fg = 'green')
        click.secho("(%s)\n" % a.source,   fg = 'yellow')

if __name__ == '__main__':
    cli()
