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


import subprocess
import datetime as DT
import cmd


class Note():
    """A note info warper"""
    def __init__(self, path, rootpath):
        self.path = path
        self.rootpath = rootpath

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
    def root_relative_path(self):
        return str(self.path.relative_to(self.rootpath))

    @property
    def root_relative_dirname(self):
        return str(self.path.relative_to(self.rootpath).parent)

    @property
    def top_dirname(self):
        return self.path.relative_to(self.rootpath).parts[0]

    @property
    def mtime(self):
        return DT.datetime.fromtimestamp(self.path.stat().st_mtime)

    @property
    def atime(self):
        return DT.datetime.fromtimestamp(self.path.stat().st_atime)

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
            }


class NoteListSelector():
    def __init__(self, notes, show_reverse,
                 editor_command, page_size, output_format):
        self.notes = notes
        self.show_reverse = show_reverse
        self.editor_command = editor_command
        self.page_size = page_size
        self.output_format = output_format

    def get_notes_in_page(self, page):
        startindex = (page - 1) * self.page_size
        endindex = ((page - 1) + 1) * self.page_size
        return self.notes[startindex:endindex]

    def print(self, page):
        page = self.restrict_page(page)
        notes = self.get_notes_in_page(page)
        notes_with_index = list(enumerate(notes, start=1))
        if self.show_reverse:
            notes_with_index.reverse()
        for index, note in notes_with_index:
            print(('{index:>2}) ' + self.output_format).format(
                index=index, **note.get_properties()))

    def open_editor(self, note, executable=None):
        if executable:
            try:
                subprocess.call([executable, note.absolute_path])
            except FileNotFoundError:
                print('executable: "{}" not found. cancel.'.format(executable))
        else:
            cmd_str = self.editor_command.format(note.absolute_path)
            subprocess.call(cmd_str, shell=True)

    def get_page_count(self):
        return int(len(self.notes) / self.page_size) + 1

    def restrict_page(self, want_page):
        max_page = self.get_page_count()
        min_page = 1
        return min(max(min_page, want_page), max_page)

    def print_and_open(self, page):
        def print_help():
            print('=========================================================\n'
                  '  How to use:\n'
                  '    * <number>    - open one item\n'
                  '    * <number> @ <executable>\n'
                  '                  - open one item with special executable\n'
                  '    * n           - next page\n'
                  '    * p           - previous page\n'
                  '    * f           - first page\n'
                  '    * l           - last page\n'
                  '    * ?, h, help  - show this help message\n'
                  '    * <else>      - exit\n'
                  '=========================================================')
            # input('press enter to continue> ')

        def get_input(page):
            if page == 1:
                prompt = "open> "
            else:
                prompt = "[page {}/{}] open> ".format(
                    page, self.get_page_count())
            user_input = input(prompt)
            return user_input

        def get_selected_note(page):
            def get_open_note(number_str, notes):
                try:
                    open_number = int(number_str)
                    if open_number <= 0 or open_number > len(notes):
                        return None
                    return notes[open_number - 1]
                except:
                    return None

            page = self.restrict_page(page)
            notes = self.get_notes_in_page(page)
            user_input = get_input(page)

            if user_input:
                if user_input == 'n':
                    return self.print_and_open(page + 1)
                elif user_input == 'p':
                    return self.print_and_open(page - 1)
                elif user_input == 'f':
                    return self.print_and_open(1)
                elif user_input == 'l':
                    return self.print_and_open(self.get_page_count())
                elif user_input in ('h', 'help', '?'):
                    print_help()
                    return self.print_and_open(page)
                else:
                    result = user_input.split('@', 1)
                    result = [item.strip() for item in result]
                    open_note = get_open_note(result[0], notes)
                    executable = None
                    if len(result) == 2:
                        executable = result[1]
                    return open_note, executable

        self.print(page)
        result = get_selected_note(page)
        if result:
            note, executable = result
            if note:
                self.open_editor(note, executable)
