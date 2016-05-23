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
import re
import subprocess

from .. import command
from .. import utils
from .. import noteselector as NS
from .. import itemselector as IS


class ListCommand(command.Command):
    def get_name(self):
        return 'list'

    def register_parser(self, subparsers):
        parser = subparsers.add_parser(
            self.get_name(),
            formatter_class=argparse.RawTextHelpFormatter,
            help='lists some notes that have recently be changed',
            description='lists some notes that have recently be changed\n'
                        'result may not consistent after file copied.')

        parser.add_argument(
            '-d', '--dir', dest='dir', action='store_true',
            help='show directories recently be used')

    def run(self, args):
        def start_note_selector():
            note_items = [NS.note_item_factory(
                path,
                rootdir=self.rootdir,
                text_format=self.config['selector']['list_format'],
                default_editor=self.config['selector']['editor'],
                default_file_browser=self.config['selector']['file_browser'],
                config=self.config,
                )
                for path in sorted(self.get_all_md_paths(),
                                   key=lambda x: x.stat().st_mtime,
                                   reverse=True)]
            NS.start_note_selector(note_items, self.config)

        def start_dir_selector():
            usage = (
                '\n'
                'How to use\n'
                '==================================================\n'
                '## Open a Directory ##\n'
                '    <number>               => e.g., 9\n'
                '    <number> /             => e.g., 9/\n'
                '        - open folder with default filebrowser\n'
                '    <number> @ <opener>    => e.g., 9@firefox\n'
                '        - open folder with special filebrowser\n\n')
            prompt = 'directory> '
            intro = ('Select a Directory (press "help" for usage)\n'
                     '=============================================\n')

            def directory_item_factory(dir_path):
                def text_func(data):
                    return self.config['selector']['list_dir_format'].format(
                        **data.get_properties())

                def task(data, line):
                    def decode_line(line):
                        match = re.search(r'^([/])(.*)', line.strip())
                        if match is not None and match.group(2):
                            opener = match.group(2)
                        else:
                            opener = self.config['selector']['file_browser']
                        return utils.get_opener_command(opener, dir_path)

                    command = decode_line(line)
                    try:
                        subprocess.call(command)
                        return True
                    except FileNotFoundError:
                        print('opener: "{}" not found. cancel.'.format(
                            command[0]))
                        return False

                return IS.Item(text=text_func,
                               task=task,
                               data=NS.PathInfo(dir_path, self.rootdir))

            items = [directory_item_factory(dir_path) for dir_path
                     in sorted(self.get_all_dir_paths(),
                               key=lambda p: p.stat().st_mtime,
                               reverse=True)]

            return IS.start_selector(
                items,
                usage=usage,
                prompt=prompt,
                intro=intro,
                page_size=int(self.config['selector'].get('page_size')),
                reverse=self.config['selector'].getboolean('reverse'))

        self.require_rootdir()
        if args.dir:
            start_dir_selector()
        else:
            start_note_selector()
