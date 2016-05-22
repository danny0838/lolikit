# Lolikit

**Lolikit** is a command line toolkit for Lolinote project. Which is a lightweigth, extremely flexible and no secret personal note-taking ruleset. [Check here](https://bitbucket.org/civalin/lolinote/wiki) for more detail about lolinote project.

If you follow the Loli's roles, The `lolikit` provide some nice tools can work with Loli more comfortable.

Acturally, Loli is small and cute.



# How to Install?

You must have a python >= 3.4 and pip. then...

linux:

    pip3 install lolikit

windows:

    py -m pip install lolikit



# How to Use?

This is some examples:

```sh
# first, read the Loli's rules...

loli help rules


# initialize your project (if not exists)...

mkdir notes
cd notes
loli init


# create / view / edit / move / copy / sync / backup your notes in the project folder...
# Hint: you can use any tools to do anything you want

touch math.md
retext math.md
vim video-games-review.md


# try to use lolikit for daily work...

loli show                       # show current project's info.

loli find eric                  # fulltext search -> keyword: "eric"
loli find "192\.168\.\d+\.\d+"  # fulltext search -> a IPv4 match 192.168.*.*

loli list                       # show a notes list sorted by modified time

loli serve                      # startup a mini web server. let your project and data working like a web site

loli config                     # check current configuration
loli config -u                  # open / edit user level config file. (create if not exists)
loli config -p                  # open / edit project level config file. (create if not exists)

loli check                      # find any defect in your project, and (if you want) try to fix it.
```



# FAQ

## utf8 with BOM?

Currently lolikit just simple ignore the BOM. But I highly recommended DO NOT contain BOM in your note files.



## What's the newline format should I use?

Lolikit believe you should use **only one** kind of newline format (one of `\n`, `\r`, `\r\n`) in your project. But you can decided which one you want.

You can run `loli check` to check inconsistent of the newline characters.



## LICENSE

MIT LICENSE



# Changelog

## Version 1.4.0

- Fixed: a lot of bugs on windows platform.
- Fixed: `loli show` cause zero division when current project folder is empty.
- Fixed: selector recognize resourced note not consider the ignore patterns.
- Tweaked: `loli dig` rename to `loli do` and change the API. Make user working on special file or directory easily.
- Tweaked: `loli fix` rename to `loli check`. And the `fix` section in configuration also be moved to `check` section too.
- Enhanced: slight improve the `loli show` result.
- Enhanced: `loli find` now support path filtering.
- Added: Bash completion support.
- Added: `loli config` help user to access their's configure easily.
- Added: `loli init` help user to create a new loli project.
- Added: `loli serve` command can startup a build-in mini web server and render a loli project to a website. (use commonmark spec.)
    - read only currently.
    - support text-based web browser. (e.g., [w3m](http://w3m.sourceforge.net/))



## Version 1.3.0

This version change a lot of configure variables. Check `loli help config` if your `lolikitrc` are not work.

- Enhanced: user can assign a `default_project` in `user` section in your **USER-LEVEL lolikitrc** file.
    - This project will be used automatically when current working directory are not within any loli project folder.
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
