# Aforgizmo

An App which saves, retrieves, edits and displays aphorisms.  
This app is written in Python using the Kivy library for cross-platform support (Android, IOS, Windows, Linux, Mac OSX).  See http://kivy.org/docs/guide/packaging.html for instructions on packaging the application for the different platforms.

## What is an Aphorism?
 * http://www.thefreedictionary.com/aphorism
 * http://en.wikipedia.org/wiki/Aphorism

## Setup
 * `$ pip install --editable .`
 * `python models.py` - setup database `data/aphorisms.db`
 * insert example aphorisms with `aforgizmo insert` then hit the RETURN/ENTER 
 key twice
 
### Manual Database Setup
```
CREATE TABLE "aphorism" (
    "id" INTEGER NOT NULL PRIMARY KEY, 
    "author" VARCHAR(255) NOT NULL, 
    "source" VARCHAR(255) NOT NULL, 
    "aphorism" TEXT NOT NULL, 
    "hashtags" TEXT NOT NULL, 
    "created" DATETIME NOT NULL
);
```
 
## Command Line Usage
Type `aforgizmo` or failing that:

```
$ python aforgizmo.py --help 

Usage: aforgizmo [OPTIONS] COMMAND [ARGS]...

Options:
  -v, --verbose
  -l, --logfile FILENAME
  --help                  Show this message and exit.

Commands:
  add     Add an aphorism.
  dump    Dump all aphorisms to a file.
  get     Get an aphorism by ID.
  insert  Insert aphorisms by file.
  list    Show all aphorisms.
  random  Get a random aphorism.
  remove  Remove an aphorism by ID.
  search  Search for an aphorism by tag.
  show    Show an aphorism by ID for display.
``` 
 
 * `aforgizmo COMMAND --help`
 * `sqlite3 data/aphorisms.db` see http://www.sqlite.org/cli.html

### Searching by hashtag text
* `aforgizmo search -t '%blah%'` where blah is the tag text you are searching
 for
 
## See Also
 * https://github.com/jcalazan/random-quotes - A similar Kivy App 

-- 
(c) Copyright 2014 Vijay Mahrra 
http://about.me/vijay.mahrra
