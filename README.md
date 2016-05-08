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

  - dig  - open a file browser in current project's root directory.
  - find - find some notes which contain some special pattern
  - list - lists some notes that have recently be changed
  - show - show current project status.
  - fix  - point out & help to fix the loli project defect. such like...
    - file encoding
    - check the newline format
    - avoid danger character in filename
    - remove empty directory.
    - resourced note directory rename.



## What's the lolikit **wan't** to do?

Everything which other general tools can suffice better, and / or not really often need. Such like...

  - file browsing
  - edit
  - backup
  - version control
  - sync
  - search by filename
  - rename a filename



# How to Install?

You must have a python >= 3.4 and pip. then...

linux:

    pip3 install lolikit

windows:

    py -m pip install lolikit



# How to use?

Change current working directory into you Loli project folder (or sub-folder). Then type command like... 

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

Currently the lolikit's implement just sample ignore the BOM. But I highly recommended DO NOT contain BOM in your note files.



## What's the newline format?

Lolikit believe you should use only one kind of newline format (one of `\n`, `\r`, `\r\n`) in your project. But you can decided which one you want. See `loli help --config`

You can run `loli fix` to check inconsistent of the newline format.



# Changelog

## Version 1.4.0

  - Enhanced: beautify `show` command total size calculate result.
  - Enhanced: `find` command now support path filtering.
  - Tweaked: `dig` command change the API, and can access special file or directory easily.
  - Added: Bash completion support. Try it with `dig` command!
  - Added: `config` command which can help user access those config settings.
  - Fixed: `show` command zero division when current project folder is empty.

## Version 1.3.0

This version change a lot of configure variables. Check `loli help config` if your `lolikitrc` are not work.

  - Enhanced: user can assign a `default_project` in `user` section in your **USER-LEVEL lolikitrc** file. This project will be used automatically when current working directory are not within any loli project folder.
  - Enhanced: note-selector now display a special icon `+` for resourced md.
  - Enhanced: note-selector UI now have `reverse` and `show` commands to reverse display and show current page.
  - Enhanced: note-selector can access "resources" of resourced md directly by `<number>.` command format.
  - Added: `show` command to show current project stats.
  - Added: `dig` command to open the current project's root directory.
  - Tweaked: change `help` command interface and write more doc in here.
  - Tweaked: change a lot of config variables names.

## Version 1.2.2

  - Removed: `-s` options in `find` and `list` commands.
  - Fixed: `prev` command in note selector are mulfunction.

## Version 1.2.1

  - Fixed: error when assign a opener in note selector UI.

## Version 1.2

  - Refactor: re-write the note selector for scalability and change the UI command.
  - Changed: option `editor_command` now change to `editor`.
  - Enhanced: note selector can open a file browser in special note parent folder now.
  - Enhanced: now `loli` can be executed when current working direcotry not in a loli project.
  - Enhanced: note selector can assign a executable as opener in runtime.

## Version 1.1

  - Accroding the rules version 2015-15-17, slight change the resourced notes detecting algorithm.
