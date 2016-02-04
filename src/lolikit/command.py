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


import abc
import re
import sys


class CanNotDetectEncodingError(Exception):
    pass


class Command(metaclass=abc.ABCMeta):
    def __init__(self, config, rootdir):
        self.rootdir = rootdir
        self.config = config

    @abc.abstractmethod
    def get_name(self):
        """
        return name
        """

    @abc.abstractmethod
    def register_parser(self, subparsers):
        """
        Register a parser to subparsers object.
        You MUST use self.get_name() to register the subparsers.add_parser()

        return:
            None

        Example:

        parser = subparsers.add_parser(
            self.get_name(),
            formatter_class=argparse.RawTextHelpFormatter,
            help='find a string / regex pattern in which files.',
            description='...')

        parser.add_argument(
            'lo3', metavar='LO3FILE', type=str, nargs='+',
            help='lonote 3 data file')

        parser.add_argument(
            '-l', '--list', dest='list_analyzers', action='store_true',
            help='List all analyzers and checking they are on or off.')
        """

    @abc.abstractmethod
    def run(self, args):
        '''
        do something when this command be trigger.
        '''
        pass

    def ignore_filter(self, paths):
        ignore_progs = [
            re.compile(pattern.strip()) for pattern
            in self.config['default']['ignore_patterns'].split('\n')
            if pattern.strip()]
        return [path for path in paths
                if not any(
                    prog.search(str(path.relative_to(self.rootdir)))
                    for prog in ignore_progs)]

    def get_all_dir_paths(self):
        paths = self.rootdir.rglob('**')
        return self.ignore_filter(paths)

    def get_all_md_paths(self):
        paths = [p for p in self.rootdir.rglob('*.md') if p.is_file()]
        return self.ignore_filter(paths)

    def get_all_resourced_md_paths(self):
        paths = [p for p in self.rootdir.rglob('*.md')
                 if all((
                     p.is_file(),
                     all(False for p2 in p.parent.rglob('*.md') if p2 != p),
                     any(True for p2 in p.parent.glob('*')
                         if p2 != p and p2.is_file())
                     ))]
        return self.ignore_filter(paths)

    def require_rootdir(self):
        if self.rootdir is None:
            print(
                'abort: This command should run within a loli directory.\n'
                '  Which defined by a ".loli" folder in project root dir.\n'
                '  If no exists yet, you may want to create a empty one.')
            sys.exit(0)

    # def get_content_and_encoding(self, path):
    #     with open(str(path), mode='rb') as f:
    #         binary = f.read()
    #     encoding = chardet.detect(binary)['encoding']
    #     if encoding is None:
    #         raise CanNotDetectEncodingError(
    #             'Encoding Not found: "{}"'.format(str(path)))
    #     else:
    #         content = binary.decode(encoding)
    #         return content, encoding
