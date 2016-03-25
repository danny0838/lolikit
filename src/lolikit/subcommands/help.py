#########################################################################
#  The MIT License (MIT)
#
#  Copyright (c) 2014~2015 CIVA LIN (林雪凡)
#
#  Permission is hereby granted, free of charge, to any person obtaining a
#  copy of this software and associated documentation files
#  (the "Software"), to deal in the Software without restriction, including
#  without limitation the rights to use, copy, modify, merge, publish,
#  distribute, sublicense, and/or sell copies of the Software, and to
#  permit persons to whom the Software is furnished to do so,
#  subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included
#  in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
#  OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
#  CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
#  TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
#  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
##########################################################################


import argparse
import textwrap
import sys

from .. import command
from .. import defaultconfig


class HelpCommand(command.Command):
    def get_name(self):
        return 'help'

    def register_parser(self, subparsers):
        parser = subparsers.add_parser(
            self.get_name(),
            formatter_class=argparse.RawTextHelpFormatter,
            help='show help messages about rules & setting detail. etc.',
            description='show help messages about rules & setting detail.'
                        ' etc.')

        parser.add_argument(
            'topic', nargs='?', choices=['rules', 'config'],
            help=(
                '\n'
                'rules  - lolinote ruleset.\n'
                'config - how to configure lolikit & current setting values.\n'
                ))

        self.parser = parser

    def run(self, args):
        if len(sys.argv) == 2:
            self.parser.print_help()
            sys.exit(1)
        elif args.topic == 'rules':
            self.show_rules()
        elif args.topic == 'config':
            self.show_config()

    def show(self, message):
        show_text = textwrap.dedent(message)
        print(show_text)

    def show_rules(self):
        message = textwrap.dedent("""\
            # Loli's Rules #

            1. One note. One file. Every notes are INDEPENDENTLY.
            2. Note files are MARKDOWN format.
            3. Note's filename equiv to "title + .md".
            4. All notes in a multi-level directory tree.
            5. Note's order is the filename string order.
            6. Root folder should have a directory which be named as ".loli".
            7. Note content must encoding as "utf8".

            Check https://bitbucket.org/civalin/lolinote for more detail.""")
        print(message)

    def show_config(self):
        message = textwrap.dedent("""\
            # Lolikit Configuration #

            ## Basic ##

            Lolikit have 3 level settings files.

            - default - in lolikit source code "defaultconfig.py" file.
            - user    - in "~/.lolikitrc".
            - project - in "project/.loli/lolikitrc"

            The default setting will be overwrited by user's setting, and
            user's setting will be overwrited by project's setting.



            -----------------------------------------------------------------



            ## Configuration Format ##

            The lolikitrc files is a kind of "ini" format. It look like...

                [selector]
                reverse = on
                editor  = vim

                [project]
                ignore_patterns = .swp$    # This is a multi-line values
                                  ~$
                [fix]
                newline_mode = posix



            -----------------------------------------------------------------



            ## Variables ##

            ### [user] section ###

            Variables in `user` section can only meaningful within the
            "user configure file" & cannot put in to project configure file.

            #### default_project_dir ####

            Set your default project dir. If your are not under
            any loli project and run `loli` command, the program
            will try to using the `default_project_dir` as your default
            project folder.

            You can let it blank to disable this feature. (default)

            example:
                ~/.notes

            - default: "{default[user][default_project_dir]}"
            - current: "{current[user][default_project_dir]}"


            -----------------------------------------------------------------


            ### [project] section ###

            Variables in `project` section can only meaningful within the
            "project configure file".

            #### ignore_patterns ####

            Determine which path will be ignore by lolikit in current project.
            It is a list of regex patterns and splitted by newline.

            PS: The "^.loli" pattern will be appended automatically and cannot
            be removed.

            - default: {default[project][ignore_patterns]}
            - current: {current[project][ignore_patterns]}


            -----------------------------------------------------------------


            ### [selector] section ###

            Control default selector behavior.

            #### editor ####

            Some lolikit command may use a editor. This setting
            define which editor should be used (by default).

            example:
                vim
                gedit "{{path}}"

            - default: "{default[selector][editor]}"
            - current: "{current[selector][editor]}"

            #### file_browser ####

            Some lolikit command may use a file browser. This setting
            define which file browser should be used (by default).

            example:
                nautilus
                ranger "{{path}}"

            - default: "{default[selector][file_browser]}"
            - current: "{current[selector][file_browser]}"

            #### reverse ####

            Some lolikit command will show a list of notes. This setting
            define the list should be reversed or not.

            - default: {default[selector][reverse]}
            - current: {current[selector][reverse]}

            #### page_size ####

            Some lolikit command will show a list of notes. This setting
            define how much notes in one page.

            - default: {default[selector][page_size]}
            - current: {current[selector][page_size]}

            #### find_format ####

            Define the output format with "find" command.

            - default: "{default[find][output_format]}"
            - current: "{current[find][output_format]}"

            #### list_format ####

            Define the output format with "list" command.

            - default: "{default[list][output_format]}"
            - current: "{current[list][output_format]}"


            -----------------------------------------------------------------

            > Special hint:
            >
            > You can use following variables in *_format:
            >
            >   - {{title}}
            >   - {{filename}}
            >   - {{parent_dirname}}
            >   - {{absolute_path}}
            >   - {{root_relative_path}}
            >   - {{root_relative_dirname}}
            >   - {{top_dirname}}
            >   - {{mtime}}
            >   - {{atime}}
            >   - {{prepend_resourced_icon}}
            >   - {{append_resourced_icon}}
            >   - {{category}}

            -----------------------------------------------------------------


            ### [fix] section ###

            #### danger_pathname_chars ####

            Define what chars is danger in pathname.

            - default: "{default[fix][danger_pathname_chars]}"
            - current: "{current[fix][danger_pathname_chars]}"

            #### danger_pathname_chars_fix_to ####

            Set which char will be used to replace the danger chars when
            fixing.

            - default: "{default[fix][danger_pathname_chars_fix_to]}"
            - current: "{current[fix][danger_pathname_chars_fix_to]}"

            #### newline_mode ####

            Define which newline mode should be used in note files.

            available mode:
                - posix
                - windows
                - mac

            - default: "{default[fix][newline_mode]}"
            - current: "{current[fix][newline_mode]}"
            """).format(
            default=defaultconfig.DEFAULT_CONFIG, current=self.config)
        print(message)
