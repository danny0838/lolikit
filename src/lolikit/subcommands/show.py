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


import argparse

from .. import command


class ShowCommand(command.Command):
    def get_name(self):
        return 'show'

    def register_parser(self, subparsers):
        subparsers.add_parser(
            self.get_name(),
            formatter_class=argparse.RawTextHelpFormatter,
            help='show current project\'s info',
            description='show current project\'s info')

    def run(self, args):
        self.require_rootdir()
        info = (
            ' - Current Project Folder:  "{rootdir}"'
            ).format(rootdir=self.rootdir)
        print(info)
