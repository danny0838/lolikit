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
import io
import subprocess
import configparser

from .. import command
from .. import utils
from .. import defaultconfig


class ConfigCommand(command.Command):
    def get_name(self):
        return 'config'

    def register_parser(self, subparsers):
        parser = subparsers.add_parser(
            self.get_name(),
            formatter_class=argparse.RawTextHelpFormatter,
            help='access lolikit settings',
            description='access lolikit settings\n'
                        'this command without args will show all settings'
                        ' after merged.'
                        'see "loli help config" for more detail.')

        parser.add_argument(
            'editor', metavar='EDITOR', nargs='?',
            help=('editor want to use\n'
                  'it will use "selector.editor" as default'))

        exgroup = parser.add_mutually_exclusive_group()

        exgroup.add_argument(
            '-u', '--user-settings', dest="user_settings",
            action='store_true',
            help='open user\'s lolikitrc')

        exgroup.add_argument(
            '-p', '--project-settings', dest="project_settings",
            action='store_true',
            help='open project\'s lolikitrc.\n'
                 'The current working directory must under a loli project,\n'
                 'or "user.default_project" must a valid value')

    def run(self, args):
        def edit(path):
            opener = args.editor or self.config['selector']['editor']
            command = utils.get_opener_command(opener, path)
            subprocess.call(command)

        def write_config_if_not_exists(path):
            if not path.exists():
                with open(str(path), mode='w', encoding='utf8') as f:
                    commented_config_str = '\n'.join(
                        '# ' + line if line else ''
                        for line in self.__get_default_config_str().split('\n')
                    )
                    commented_config_str = (
                        '# See "loli help config" for more detail\n\n' +
                        commented_config_str)
                    f.write(commented_config_str)

        if args.user_settings:
            path = utils.get_user_lolikitrc_path()
            edit(path)
        elif args.project_settings:
            self.require_rootdir()
            path = utils.get_project_lolikitrc_path(self.rootdir)
            write_config_if_not_exists(path)
            edit(path)
        else:
            self.__print_current_config()

    def __get_config_str(self, config):
        stringio = io.StringIO()
        config.write(stringio)
        stringio.seek(0)
        return stringio.read()

    def __get_self_config_str(self):
        return self.__get_config_str(self.config)

    def __get_default_config_str(self):
        default_config = configparser.ConfigParser()
        default_config.read_dict(defaultconfig.DEFAULT_CONFIG)
        return self.__get_config_str(default_config)

    def __print_current_config(self):
        print(self.__get_self_config_str())