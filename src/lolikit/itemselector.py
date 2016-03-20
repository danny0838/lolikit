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

"""
How to Use:


import itemselector

def run_func_factory(x):
    def run_func(quiet):  # Closure
        if quiet:
            print(x**2)
        else:
            print("{}**2 = {}".format(x, x**2))
        return True  # stop after run
    return run_func

items = [itemselector.Item(
            text="{}**2 = ?".format(i),
            run_func=run_func_factory(i)
            )
         for i in range(1, 100)]

IS = itemselector.ItemSelector(
    items = items,
    kwargs_gen_func=lambda after: {'quiet': True if 'q' in after else False},
    )
IS.cmdloop()
"""


import cmd
import math
import re


class Item():
    def __init__(self, text, run_func):
        """
        run_func = do anything when run()
                   return True can cause ItemSelector.cmdloop() stop.
        text  = function without args and return item text
                or
                a str object
        """
        self.run_func = run_func
        self.text = text

    def run(self, **kwargs):
        return self.run_func(**kwargs)

    def get_text(self):
        return self.text if type(self.text) is str else self.text()


class ItemSelector(cmd.Cmd):
    def __init__(self,
                 items,
                 kwargs_gen_func=lambda follow_str: {'follow_str': follow_str},
                 usage='Enter a cmd starts with digit then item will be ran.',
                 prompt='> ',
                 intro=('Item Selector (press "help" for usage)\n'
                        '===========================================\n'),
                 page_size=10,
                 reverse=False):
        """
        items = A list of Item object
        kwargs_gen_func = A function process the "after" string and
                          return a dict form kwargs for Item.run() function.
                          if not return a dict, mean the "after" are invalid.
        config = A dict of configuration
        """
        super().__init__()

        self.items = items
        self.kwargs_gen_func = kwargs_gen_func

        self.page = 1
        self.page_size = page_size
        self.reverse = reverse

        self.prompt = prompt
        self.intro = intro + self.get_page_content()
        self.usage = usage

    def get_page_count(self):
        return math.ceil(len(self.items) / self.page_size)

    def set_page(self, page):
        def restrict_page(want_page):
            max_page = self.get_page_count()
            min_page = 1
            return min(max(min_page, want_page), max_page)

        self.page = restrict_page(page)

    def set_page_size(self, page_size):
        def restrict_page_size(want_page_size):
            min_page_size = 1
            return max(want_page_size, min_page_size)

        page_size = restrict_page_size(page_size)
        first_item_number = self.page_size * (self.page - 1) + 1
        new_page = math.ceil(first_item_number / page_size)
        self.page_size = page_size
        self.set_page(new_page)

    def get_items_in_page(self):
        startindex = (self.page - 1) * self.page_size
        endindex = self.page * self.page_size
        return self.items[startindex:endindex]

    def get_item_in_page(self, number):
        items = self.get_items_in_page()
        index = number - 1
        if index >= 0:
            return items[index]
        else:
            raise IndexError('index < 0')

    # extra tools for subclass

    def get_number_and_after(self, line):
        """analyze cmd starts with number"""
        try:
            match = re.search("^(\d+)(.*)", line)
            number = match.group(1)
            after = match.group(2)
            return int(number), after
        except:
            return None, None

    def run_item(self, number, **kwargs):
        return self.get_item_in_page(number).run(**kwargs)

    def get_page_content(self):
        items = self.get_items_in_page()
        items_with_number = list(enumerate(items, start=1))

        page_info = '[page {}/{}]'.format(self.page, self.get_page_count())
        texts = ['{index:>2}) {item_text}'.format(
                 index=index, item_text=item.get_text())
                 for index, item
                 in (items_with_number if self.reverse is False else reversed(
                     items_with_number))]
        if self.reverse:
            texts.insert(0, page_info)
        else:
            texts.append(page_info)

        return '\n'.join(line for line in texts)

    def print_page(self):
        print(self.get_page_content())

    # implemented method

    def postcmd(self, stop, line):
        if not stop:
            parts = line.split()
            if len(parts):
                if all([parts[0] not in ('help', ),
                        not line.startswith('?'),
                        not line.startswith('!')]):
                    print()
                    self.print_page()
        return stop

    def emptyline(self):
        return True

    def do_exit(self, arg):
        return True

    def do_next(self, arg):
        '''Go to next page(s)
        example: next [page_count]'''
        try:
            number = max(int(arg), 1)
        except:
            number = 1
        self.set_page(self.page + number)

    def do_prev(self, arg):
        '''Go to previous page(s)
        example: previous [page_count]'''
        try:
            number = max(int(arg), 1)
        except:
            number = 1
        self.set_page(self.page - number)

    def do_first(self, arg):
        '''Go to first page
        example: first'''
        self.set_page(1)

    def do_last(self, arg):
        '''Go to last page
        example: last'''
        self.set_page(99999999)

    def do_goto(self, arg):
        '''Go to a special page.
        example: goto <page_number>'''
        try:
            number = max(int(arg), 1)
        except:
            return
        self.set_page(number)

    def do_size(self, arg):
        '''Set the page size.
        It's will change page and try to keep first item still in list.
        example: size <item_count>'''
        try:
            number = max(int(arg), 1)
        except:
            return
        self.set_page_size(number)

    def do_reverse(self, arg):
        '''Toggle reverse display mode.
        example: reverse'''
        self.reverse = not self.reverse

    def do_show(self, arg):
        '''Show current page
        example: show'''
        pass

    # subclass usually should override following method

    def default(self, line):
        number, after = self.get_number_and_after(line)
        if number is not None:
            kwargs = self.kwargs_gen_func(after)
            try:
                return self.run_item(int(number), **kwargs)
            except IndexError:
                print('[cancel]: index "{}" out of range,'
                      ' please try again.'.format(number))
        else:
            print('[cancel]: command "{}" not found.'.format(line))

    def help_usage(self):
        print(self.usage)


def start_selector(*args, **kwargs):
    selector = ItemSelector(*args, **kwargs)
    selector.cmdloop()
