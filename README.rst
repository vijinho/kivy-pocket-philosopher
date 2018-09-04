Pocket Philosopher
==================

This app which saves, retrieves, edits and displays random aphorisms on
random backgrounds.

It runs from Android version 2.2 and is available on Google Play at:

https://play.google.com/store/apps/details?id=com.urunu.aforgizmo

Features
--------
-  Command-line interface utility to manipulate, import/export and display the data
-  Copy aphorisms to the clipboard for sharing in other applications
-  Easily search aphorisms
-  Specify any local folder on your device for image display
-  Backup/Restore the database locally
-  Import data from a remote URL (example included)
-  Download background images from a remote URL (example included)
-  User flash message notifications with timed-removal

What is an Aphorism?
--------------------

-  http://www.thefreedictionary.com/aphorism
-  http://en.wikipedia.org/wiki/Aphorism

Setup
-----

-  ``$ pip install --editable .``
-  ``nosetests`` - run 'nose' tests in tests/

Manual Database Setup
~~~~~~~~~~~~~~~~~~~~~
If you wish to setup the database manually instead of automatically when the
application runs:

Run ``python models.py`` - setup database ``data/aphorisms.db`` or
::

    CREATE TABLE "aphorism" (
        "id" INTEGER NOT NULL PRIMARY KEY,
        "author" VARCHAR(255) NOT NULL,
        "source" VARCHAR(255) NOT NULL,
        "aphorism" TEXT NOT NULL,
        "hashtags" TEXT NOT NULL,
        "created" DATETIME NOT NULL
    );

-  Insert the example aphorisms from ``data/aphorisms.json`` with
   ``aforgizmo insert`` then hit the RETURN/ENTER key twice

Command Line Usage
------------------

Type ``aforgizmo`` or failing that:

::

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

-  ``aforgizmo COMMAND --help``
-  ``sqlite3 data/aphorisms.db`` see http://www.sqlite.org/cli.html

Running the Kivy App
--------------------

-  On Mac OS X: ``kivy main.py`` - On other platforms it may 'just work'
   with ``python main.py``
-  Alternatively, run .

See Also
--------

-  https://travis-ci.org/vijinho/aforgizmo - Travis Build Test
-  https://github.com/jcalazan/random-quotes - A similar Kivy App

This app is written in Python using the Kivy library for
cross-platform support (Android, IOS, Windows, Linux, Mac OSX). See
http://kivy.org/docs/guide/packaging.html for instructions on packaging
the application for the different platforms.

(c) Copyright 2014 Vijay Mahrra http://www.urunu.com/
