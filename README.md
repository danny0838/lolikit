# Lolikit

Lolinote - Lonote Lite Note-taking Rule set - is a project which defined a pure-text note-taking framework.

It's not like other note-taking system combine all functions into one or few software, Loli try to keepup some basic, easy and reasonable tool-free roles. Let user can use any tools to write, read, share, convert, sync and version control their notes.

If you following the Loli's roles, The `lolikit` is a toolkit for you.

Acturally, Loli is small and cute.



## Where can I find the detail of Loli project?

[See Here](https://bitbucket.org/civalin/lolinote/wiki)



## What's the lolikit do?

Lolikit is a command line supporting toolkit for Loli project, but not a **requirement**. This toolkit provide some good thing let user can work with Loli more comfortable.

Currently the lolikit include the following sub-command...

* find - find some notes which contain some special pattern
* list - lists some notes that have recently be changed
* fix  - point out & help to fix the loli project defect. such like file encoding, check the newline format, avoid danger character in filename, remove empty directory. etc.



## What's the lolikit wan't to do?

Everything which other tool doing better, and / or not really often need it. Such like...

* file browsing
* edit
* backup
* version control
* sync
* search by filename
* rename a filename



# How to Install?

You must have a python >= 3.4 and pip. then...

linux:

    pip3 install lolikit

windows:

    py -m pip install lolikit



# How to use?

Change current working directory into you Loli project folder. Then type command like... 

    loli --help
    loli find <keyword>
    loli list
    loli fix
    loli fix -h
    ...



## LICENSE

MIT LICENSE



# FAQ

## utf8 with BOM?

Currently the lolikit's implement just sample ignore the BOM.



## What the newline format?

Lolikit wish you to use only one kind of newline format (`\n`, `\r`, `\r\n`). But you can decided which one you want to use.

You can run `loli fix` to check inconsistent of the newline format.
