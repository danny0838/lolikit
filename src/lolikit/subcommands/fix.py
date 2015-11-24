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
import itertools
import os
import shutil

from .. import command
from .. import utils


class FixCommand(command.Command):
    def get_name(self):
        return 'fix'

    def register_parser(self, subparsers):
        parser = subparsers.add_parser(
            self.get_name(),
            formatter_class=argparse.RawTextHelpFormatter,
            help='point out & help to fix the project defect',
            description='point out & help to fix the project defect\n\n'
                        'Support auto fixing:\n'
                        '  - rename unsafe pathname\n'
                        '  - remove empty note and directory\n'
                        '  - fix inconsistent newline\n\n'
                        'fix tool can also detect a part of non-utf8'
                        ' files (but maybe not all) and cannot fix it'
                        ' automatically.')

        parser.add_argument(
            '-v', dest='verbose', action='store_true',
            help='print information verbosely')

        parser.add_argument(
            '-r', dest='resolve', action='store_true',
            help='try to resolve all problem interactively')

        parser.add_argument(
            '-y', dest='always_yes', action='store_true',
            help='auto resolve problems without confirm')

    def run(self, args):
        enc_error_paths = self.__get_encoding_error_files()
        if enc_error_paths:
            print('ALERT: Following files are *NOT* encoding as utf8.\n'
                  'You should fix it manually as soon as possible'
                  ' before doing anything else.\n')
            for path in enc_error_paths:
                print(str(path))
        else:
            self.__deal_empty_notes(args)
            self.__deal_empty_dirs(args)
            self.__deal_danger_paths(args)
            self.__deal_inconsistent_newline_paths(args)

    def __get_encoding_error_files(self):
        files = []
        for path in self.get_all_md_paths():
            try:
                with open(str(path), encoding='utf8') as f:
                    f.read()
            except UnicodeDecodeError:
                files.append(path)
        return files

    def __verbose_paths_print(self, paths):
        print('  include:')
        for path in paths:
            print('    "{}"'.format(path))
        print()

    def __deal(self, args, paths,
               detected_message, confirm_message, resolve_func):
        how_much = len(paths)
        if how_much:
            print(detected_message.format(how_much))
            paths = sorted(paths, reverse=True)
            if args.verbose:
                self.__verbose_paths_print(paths)
            if args.resolve:
                if args.always_yes:
                    resolve_func(paths, args.verbose)
                elif utils.confirm(confirm_message):
                    resolve_func(paths, args.verbose)

    def __get_small_size_paths(self):
        small_size = int(self.config[self.get_name()]['small_size'])
        small_size_path = [path for path in self.get_all_md_paths()
                           if path.stat().st_size < small_size]
        return small_size_path

    def __get_empty_content_paths(self):
        small_size_paths = self.__get_small_size_paths()
        empty_content_paths = []
        for path in small_size_paths:
            with open(str(path), encoding='utf8') as f:
                content = f.read()
            if len(content.strip()) == 0:
                empty_content_paths.append(path)
        return empty_content_paths

    def __rm_paths(self, paths, verbose):
        count = 0
        print('  deleteing...')
        for path in paths:
            if path.is_file():
                os.remove(str(path))
                if verbose:
                    print('    "{}"'.format(path))
                count += 1
            elif path.is_dir():
                shutil.rmtree(str(path))
                if verbose:
                    print('   "{}"'.format(path))
                count += 1
        print('\n  [RESOLVED] Deleted: {}'.format(count))

    def __deal_empty_notes(self, args):
        paths = self.__get_empty_content_paths()
        self.__deal(args=args,
                    paths=paths,
                    detected_message='[DETECTED] Empty notes: {}',
                    confirm_message='remove empty notes? (y/n)> ',
                    resolve_func=self.__rm_paths)

    def __get_empty_dirs(self):
        empty_child_dirs = [d for d in self.get_all_dir_paths()
                            if len(tuple(d.iterdir())) == 0]
        return empty_child_dirs

    def __deal_empty_dirs(self, args):
        paths = self.__get_empty_dirs()
        self.__deal(args=args,
                    paths=paths,
                    detected_message='[DETECTED] Empty directories: {}',
                    confirm_message='remove empty directories? (y/n)> ',
                    resolve_func=self.__rm_paths)

    def __get_danger_paths(self):
        all_paths = itertools.chain(
            self.get_all_dir_paths(), self.get_all_md_paths())
        d_chars = self.config[self.get_name()]['danger_pathname_chars']
        d_paths = [path for path in all_paths
                   if any(True for c in d_chars if c in path.name)]
        return d_paths

    def __rename_danger_paths(self, paths, verbose):
        d_chars = self.config[self.get_name()]['danger_pathname_chars']
        f_char = self.config[
            self.get_name()]['danger_pathname_chars_fix_to']
        count = 0
        print('  renaming...')
        for path in paths:
            new_name = path.name
            for d_char in d_chars:
                new_name = new_name.replace(d_char, f_char)
            new_path = path.with_name(new_name)
            if new_path.exists():
                print('    [ABOUT]: "{}" be occupied!'.format(new_path))
                continue
            else:
                path.rename(new_path)
            if verbose:
                print('    "{}"  >>  "{}"'.format(path, new_path.name))
            count += 1
        print('\n  [RESOLVED] Renamed: {}'.format(count))

    def __deal_danger_paths(self, args):
        paths = self.__get_danger_paths()
        self.__deal(args=args,
                    paths=paths,
                    detected_message=('[DETECTED] Pathname has danger chars:'
                                      ' {}'),
                    confirm_message='Rename those pathnames? (y/n)> ',
                    resolve_func=self.__rename_danger_paths)

    def __get_newline_mode(self, path):
        with open(str(path), newline='', encoding='utf8') as f:
            content = f.read()
        if '\r\n' in content:
            return 'windows'
        elif '\r' in content:
            return 'mac'
        elif '\n' in content:
            return 'posix'
        else:  # no any newline mark
            return None

    def __get_inconsistent_newline_paths(self):
        want_newline_mode = self.config['default']['newline_mode']
        paths = [path for path in self.get_all_md_paths()
                 if self.__get_newline_mode(path) not in (
                     want_newline_mode, None)]
        return paths

    def __universalize_newline(self, paths, verbose):
        def convert_newline(content, from_mode, to_mode):
            if from_mode == 'windows':
                from_newline = '\r\n'
            elif from_mode == 'mac':
                from_newline = '\r'
            elif from_mode == 'posix':
                from_newline = '\n'
            else:
                raise RuntimeError(
                    'from_mode "{}" not defined'.format(from_mode))
            if to_mode == 'windows':
                to_newline = '\r\n'
            elif to_mode == 'mac':
                to_newline = '\r'
            elif to_mode == 'posix':
                to_newline = '\n'
            else:
                raise RuntimeError(
                    'to_mode "{}" not defined'.format(to_mode))
            return content.replace(from_newline, to_newline)

        want_newline_mode = self.config['default']['newline_mode']
        count = 0
        print('  changing newline...')
        for path in paths:
            newline_mode = self.__get_newline_mode(path)
            with open(str(path), encoding='utf8') as f:
                content = f.read()
            new_content = convert_newline(
                content, newline_mode, want_newline_mode)
            with open(str(path), mode='w', encoding='utf8') as f:
                f.write(new_content)
            if verbose:
                print('    "{}"'.format(path))
            count += 1
        print('\n  [RESOLVED] Changed files: {}'.format(count))

    def __deal_inconsistent_newline_paths(self, args):
        want_newline_mode = self.config['default']['newline_mode']
        paths = self.__get_inconsistent_newline_paths()
        self.__deal(args=args,
                    paths=paths,
                    detected_message=('[DETECTED] Newline mode inconsistent'
                                      ' (setting is "' +
                                      want_newline_mode + '"):'
                                      ' {}'),
                    confirm_message='Change newline mode of files? (y/n)> ',
                    resolve_func=self.__universalize_newline)
