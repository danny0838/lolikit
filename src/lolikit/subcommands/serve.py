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
import functools
import mimetypes
import pathlib
import datetime as DT
import logging

import bottle
import mako.lookup as ML
import CommonMark

from .. import command


mimetypes.types_map['.md'] = 'text/x-markdown'


class ServeCommand(command.Command):
    def get_name(self):
        return 'serve'

    def register_parser(self, subparsers):
        parser = subparsers.add_parser(
            self.get_name(),
            formatter_class=argparse.RawTextHelpFormatter,
            help='start a web server allow to remote access',
            description=(
                'start a web server allow to remote access'
                ' current lolinote project.\n\n'
                'The following options will overwrite the current config'
                ' settings.\n'
                'Use "loli config" to check the current config value.'))

        parser.add_argument(
            '-p', '--port', dest='port', metavar='PORT', type=str,
            help='assign a port for lolinote server')

        parser.add_argument(
            '-r', '--remote', dest='remote', action='store_true',
            help='allow remote access. make sure you really want to\n'
                 'expose your data server on network')

        parser.add_argument(
            '-d', '--debug', dest='debug', action='store_true',
            help='show more debug messages in browser.')

    def run(self, args):
        self.require_rootdir()
        webapp = WebApp(loliconf=self.config, cmd=self)
        port = args.port or self.config[self.get_name()]['port']
        if args.remote or self.config[
                self.get_name()].getboolean('allow_remote_access'):
            host = '0.0.0.0'
        else:
            host = '127.0.0.1'
        debug = args.debug or self.config[self.get_name()].getboolean('debug')
        print('Lolinote server starting up...')
        print('Listening on http://{host}:{port}'.format(host=host, port=port))
        print("Hit Ctrl-C to quit.\n")
        bottle.run(app=webapp.bottleapp,
                   host=host, port=port, quiet=True, debug=debug)


def mroute(path, method='GET'):
    """"use: @mroute('xx', 'GET')"""
    def decorator(func):
        func.route = {}
        func.route['path'] = path
        func.route['method'] = method
        return func
    return decorator


def mauth(method):
    """use: @mauth"""
    def decorator(self, *args, **kwargs):
        def pass_checker(username, password):
            cfg_users = self._cmd.config['serve']['users']
            if cfg_users == '':
                return True
            else:
                for up in cfg_users.split('\n'):
                    u, p = up.split(':')
                    if u == username:
                        if p == password:
                            return True
                return False

        @functools.wraps(method)
        @bottle.auth_basic(pass_checker)
        def wrapper(*args, **kwargs):
            return method(*args, **kwargs)

        return wrapper(self, *args, **kwargs)

    return decorator


class WebApp:
    def __init__(self, loliconf, cmd):
        def get_logger():
            logger = logging.getLogger('loliserve')

            log_dirpath = cmd.rootdir / '.loli' / 'lolikit'
            if not log_dirpath.exists():
                log_dirpath.mkdir(parents=True)
            log_filepath = log_dirpath / 'serve.log'

            logger.setLevel(logging.INFO)
            file_handler = logging.FileHandler(str(log_filepath))
            formatter = logging.Formatter('%(msg)s')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            return logger

        def get_log_to_logger(logger):
            def log_to_logger(fn):
                @functools.wraps(fn)
                def _log_to_logger(*args, **kwargs):
                    request_time = DT.datetime.now()
                    actual_response = fn(*args, **kwargs)
                    logger.info(
                        ('{addr} - - [{time}]'
                         ' - {method} {status} {req_url}').format(
                            addr=bottle.request.remote_addr,
                            time=request_time,
                            method=bottle.request.method,
                            status=actual_response.status,
                            req_url=bottle.request.url))
                    return actual_response
                return _log_to_logger
            return log_to_logger

        def route_init(webapp, bottleapp):
            for kw in dir(webapp):
                attr = getattr(webapp, kw)
                if hasattr(attr, 'route') and type(attr.route) == dict:
                    bottleapp.route(
                        attr.route['path'],
                        attr.route['method'],
                        attr)

        def error_handle(bottleapp):
            @bottleapp.error(404)
            def error404(error):
                return '404 Not Found'

        self.bottleapp = bottle.Bottle()
        self._logger = get_logger()
        self.bottleapp.install(get_log_to_logger(self._logger))
        route_init(self, self.bottleapp)
        error_handle(self.bottleapp)

        self._loliconf = loliconf
        self._cmd = cmd
        self._mako_lookup = ML.TemplateLookup(
            directories=[
                str(pathlib.Path(__file__).parent / 'servedata' / 'mako')],
            input_encoding='utf-8')
        self._staticdir = pathlib.Path(
            __file__).parent / 'servedata' / 'static'

    def __check_ignore_filepath(self, filepath):
        if len(self._cmd.filted_ignore([filepath])) == 0:
            raise bottle.HTTPError(404)

    def __url2filepath(self, relative_url):
        """ convert url 'aaa/bbb/ccc' to '/.../rootdir/aaa/bbb/ccc' """
        filepath = self._cmd.rootdir / pathlib.Path(relative_url)
        self.__check_ignore_filepath(filepath)
        return filepath

    def __get_dir(self, filepath):
        if filepath.is_dir():
            return filepath
        elif filepath.exists():
            return filepath.parent
        else:
            return None

    def __get_base_data(
            self, filepath, current_mode, page_title='', description=''):
        def get_page_title(filepath, current_mode, page_title):
            if page_title:
                return page_title
            else:
                return '{stem}{mode_string}- Lolinote'.format(
                    stem=filepath.stem,
                    mode_string=(
                        ' (source mode) ' if current_mode == 'source' else ''))

        rel_filepath = str(filepath.relative_to(self._cmd.rootdir))
        dirmark = '/' if filepath.is_dir() else ''
        page_title = get_page_title(filepath, current_mode, page_title)
        description = description or page_title
        return {'page_title': page_title,
                'description': description,
                'current_mode': current_mode,
                'item_title': filepath.name.rstrip('.md'),
                'rel_filepath': rel_filepath,
                'dirmark': dirmark}

    def __get_dir_content_data(self, dirpath, prepend_url):
        """return a list of filepaths
            return {prepend_url: prepend_url,
                    array: [
                        (name, baseon_rootdir, dirmark, glyphicon),
                        ...
                    ]}
        """
        paths = sorted(list(dirpath.glob('*')),
                       key=lambda p: (
                           not p.is_dir(), not p.name.endswith('.md'), str(p)))
        paths = self._cmd.filted_ignore(paths)
        array = list(
            zip([p.name for p in paths],
                [str(p.relative_to(self._cmd.rootdir)) for p in paths],
                ['/' if p.is_dir() else '' for p in paths]))
        return {'prepend_url': prepend_url,
                'array': array}

    def __get_dir_bread_data(self, filepath, prepend_url):
        """return a list of parents paths
            return {prepend_url: prepend_url,
                    array: [
                        (name, baseon_rootdir, dirmark),
                        ...
                    ]}
        """
        paths = [p for p in reversed(filepath.parents)
                 if self._cmd.rootdir in p.parents or self._cmd.rootdir == p]
        paths.append(filepath)
        paths = self._cmd.filted_ignore(paths)
        array = list(
            zip([p.name for p in paths],
                [str(p.relative_to(self._cmd.rootdir)) for p in paths],
                ['/' if p.is_dir() else '' for p in paths]))
        return {'prepend_url': prepend_url,
                'array': array}

    def __get_note_data(self, filepath, render):
        with open(str(filepath), mode='r', encoding='utf8') as f:
            content = f.read()
        if render:
            content = CommonMark.commonmark(content)
        return {'title': filepath.stem,
                'content': content,
                'render': render}

    def __get_dir_result(self, filepath, prepend_url):
        current_mode = prepend_url.split('/')[1]
        return self._mako_lookup.get_template(
            'directory.mako').render(
                base_data=self.__get_base_data(filepath, current_mode),
                dir_content_data=self.__get_dir_content_data(
                    filepath, prepend_url=prepend_url),
                dir_bread_data=self.__get_dir_bread_data(
                    filepath, prepend_url=prepend_url))

    def __get_note_result(self, filepath, prepend_url, render):
        current_mode = prepend_url.split('/')[1]
        return self._mako_lookup.get_template(
            'note.mako').render(
                base_data=self.__get_base_data(filepath, current_mode),
                dir_bread_data=self.__get_dir_bread_data(
                    filepath, prepend_url=prepend_url),
                note_data=self.__get_note_data(filepath, render))

    def __get_mix_result(self, urlpath, prepend_url):
        filepath = self.__url2filepath(urlpath)
        if filepath is None:
            raise bottle.HTTPError(404)
        elif filepath.is_dir():
            return self.__get_dir_result(filepath, prepend_url=prepend_url)
        else:
            if filepath.name.endswith('.md'):
                return self.__get_note_result(
                    filepath,
                    prepend_url=prepend_url,
                    render=True if prepend_url == '/note/' else False)
            else:
                relstr_filepath = str(filepath.relative_to(self._cmd.rootdir))
                return bottle.static_file(
                    relstr_filepath, root=str(self._cmd.rootdir),
                    mimetype=mimetypes.guess_type(filepath.name)[0])

    @mroute('/static/<path:path>', 'GET')
    @mauth
    def static(self, path):
        return bottle.static_file(path, root=str(self._staticdir),
                                  mimetype=mimetypes.guess_type(path)[0])

    @mroute('/source/', 'GET')
    @mauth
    def source_root(self):
        return bottle.HTTPResonse(
            self.__get_mix_result('', prepend_url='/source/'))

    @mroute('/source/<path:path>', 'GET')
    @mauth
    def source(self, path):
        return bottle.HTTPResponse(
            self.__get_mix_result(path, prepend_url='/source/'))

    @mroute('/note/', 'GET')
    @mauth
    def note_root(self):
        return bottle.HTTPResponse(
            self.__get_mix_result('', prepend_url='/note/'))

    @mroute('/note/<path:path>', 'GET')
    @mauth
    def note(self, path):
        return bottle.HTTPResponse(
            self.__get_mix_result(path, prepend_url='/note/'))

    @mroute('/', 'GET')
    @mauth
    def index(self):
        return bottle.redirect('/note/')
