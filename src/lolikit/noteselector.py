#########################################################################
#  The MIT License (MIT)
#
#  Copyright (c) 2014~2016 CIVA LIN (林雪凡)
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

import datetime as DT
import subprocess
import re

from . import itemselector as IS
from . import utils


class NoteInfo():
    """A note info warper"""
    def __init__(self, path, rootdir):
        self.path = path
        self.rootdir = rootdir

    @property
    def title(self):
        return self.path.stem

    @property
    def filename(self):
        return self.path.name

    @property
    def parent_dirname(self):
        return self.path.parent.name

    @property
    def grandparent_dirname(self):
        return self.path.parent.parent.name

    @property
    def absolute_path(self):
        return str(self.path.resolve())

    @property
    def absolute_parent_dirpath(self):
        return str(self.path.parent.resolve())

    @property
    def root_relative_path(self):
        return str(self.path.relative_to(self.rootdir))

    @property
    def root_relative_dirname(self):
        return str(self.path.relative_to(self.rootdir).parent)

    @property
    def top_dirname(self):
        return self.path.relative_to(self.rootdir).parts[0]

    @property
    def mtime(self):
        return DT.datetime.fromtimestamp(self.path.stat().st_mtime)

    @property
    def atime(self):
        return DT.datetime.fromtimestamp(self.path.stat().st_atime)

    @property
    def resourced_icon(self):
        return '[＋] ' if utils.is_rmd(self.path) else ''

    def get_properties(self):
        return {
            'title': self.title,
            'filename': self.filename,
            'parent_dirname': self.parent_dirname,
            'absolute_path': self.absolute_path,
            'root_relative_path': self.root_relative_path,
            'root_relative_dirname': self.root_relative_dirname,
            'top_dirname': self.top_dirname,
            'mtime': self.mtime,
            'atime': self.atime,
            'resourced_icon': self.resourced_icon,
            }


def note_item_factory(path, rootdir, text_format,
                      default_editor, default_file_browser, config):
    noteinfo = NoteInfo(path, rootdir)

    def text_func():
        return text_format.format(**noteinfo.get_properties())

    def run_func(task, opener):
        if task == 'open':
            opener = opener if opener else default_editor
            try:
                subprocess.call([opener, noteinfo.absolute_path])
            except FileNotFoundError:
                print('[cancel]: editor "{}" not found.'.format(opener))
                return False
        elif task == 'file_browsing':
            opener = opener if opener else default_file_browser
            try:
                subprocess.call([opener, noteinfo.absolute_parent_dirpath])
            except FileNotFoundError:
                print('[cancel] file_browser "{}" not found.'.format(opener))
                return False
        elif task == 'attachment_browsing':
            if utils.is_rmd(noteinfo.path):
                start_attachment_selector(noteinfo, config)
            else:
                print('[cancel]: "{}" not a resourced note.'.format(
                    noteinfo.title))
            return False
        return True

    return IS.Item(text=text_func, run_func=run_func)


def start_note_selector(note_items, config):
    usage = (
        '\n'
        'How to use\n'
        '=================================================\n'
        '## Open a note ##\n'
        '    <number>\n'
        '    <number> @\n'
        '        - open file with default editor\n'
        '    <number> @ <editor>\n'
        '        - open file with special editor\n'
        '\n'
        '## Open a note directory ##\n'
        '    <number> /\n'
        '        - open folder with default filebrowser\n'
        '    <number> / <file_browser>\n'
        '        - open folder with special filebrowser\n'
        '\n'
        '## Open attachment selector ##\n'
        '    <number> .\n'
        '        - view attachments of one of note\n'
        '\n'
        '## Example ##\n'
        '    5\n'
        '    5@gedit\n'
        '    5/\n'
        '    5/nautilus\n')
    prompt = 'note> '
    intro = ('Select a Item (press "help" for usage)\n'
             '===========================================\n')

    def note_kwargs_gen_func(line):
        kwargs = {}
        match = re.search(r'^([@/.])(.*)', line.strip())
        if match is None:
            kwargs['task'] = 'open'
            kwargs['opener'] = None
        else:
            kwargs['opener'] = match.group(2)
            if match.group(1) == '@':
                kwargs['task'] = 'open'
            elif match.group(1) == '/':
                kwargs['task'] = 'file_browsing'
            elif match.group(1) == '.':
                kwargs['task'] = 'attachment_browsing'
        return kwargs

    return IS.start_selector(
        note_items,
        kwargs_gen_func=note_kwargs_gen_func,
        usage=usage,
        prompt=prompt,
        intro=intro,
        page_size=int(config['selector'].get('page_size')),
        reverse=config['selector'].getboolean('reverse'))


def start_attachment_selector(noteinfo, config):
    usage = (
        'How to use\n'
        '=================================================\n'
        '## Open a attach ##\n'
        '    <number>\n'
        '    <number> @\n'
        '        - open file with system default program\n'
        '    <number> @ <opener>\n'
        '        - open file with special program\n'
        '\n'
        '## Example ##\n'
        '    5\n'
        '    5@firefox\n')
    prompt = 'attachment> '
    intro = ('Select a Item (press "help" for usage)\n'
             '===========================================\n')

    def note_kwargs_gen_func(line):
        kwargs = {}
        match = re.search(r'^([@])(.*)', line.strip())
        if match is None:
            kwargs['opener'] = utils.get_default_opener()
        elif match.group(2):
            kwargs['opener'] = match.group(2)
        return kwargs

    def attachment_item_factory(res_path):
        def run_func(opener):
            try:
                subprocess.call([opener, str(res_path)])
            except FileNotFoundError:
                print('opener: "{}" not found. cancel.'.format(opener))

        return IS.Item(text=res_path.name,
                       run_func=run_func)

    items = [attachment_item_factory(res_path) for res_path
             in sorted(utils.get_resource_paths(noteinfo.path))]

    return IS.start_selector(
        items,
        kwargs_gen_func=note_kwargs_gen_func,
        usage=usage,
        prompt=prompt,
        intro=intro,
        page_size=int(config['selector'].get('page_size')),
        reverse=config['selector'].getboolean('reverse'))