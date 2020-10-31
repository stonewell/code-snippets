import argparse
import logging
import os
import sys
import tempfile
import json
import re

from epub_builder import EPubBuilder


def args_parser():
    parser = argparse.ArgumentParser(prog='txt2epub',
                                     description='generate epub from txt, generate toc based on regex text')
    parser.add_argument('-c', '--config', type=argparse.FileType('r'), help='config file', required=False)
    parser.add_argument('-i', '--input', type=str, help='input text file', required=False)
    parser.add_argument('-o', '--output', type=str, help='output epub directory', required=False, default=".")
    parser.add_argument('-v', '--verbose', action='count', help='print debug information', required=False, default=0)

    return parser

def run_main(opts):
    config = {}

    if opts.config:
        data = opts.config.read()
        logging.debug('config data:[%s]', data)
        config.update(json.loads(data))

    if opts.input:
        config["input"] = opts.input

    if opts.output:
        config["output"] = opts.output

    if 'input' not in config or 'output' not in config:
        args_parser().print_help()
        sys.exit(1)

    content = process_input(config)

    generate_epub(config, content)

class Volume(object):
    def __init__(self, title):
        self._title = title
        logging.debug('create new volume:[%s]', title)

        self.parent_volume = None

        self._chapters = [Chapter('')]
        self._default_chapter = None

    def add_line(self, line):
        if line == '\n' or line == '\r' or line == '\r\n':
            return

        logging.debug('volume add line:[%s]', line)

        self._chapters[-1].add_line(line)

    def append(self, obj):
        self._chapters.append(obj)
        obj.parent_volume = self

    def build_epub(self, builder):
        has_chapter = False
        for c in self._chapters:
            if c.valid():
                has_chapter = True
                break

        builder.new_volume(self._title)

        if not has_chapter:
            c = Chapter('')
            c.add_line('')
            c.build_epub(builder)

        for c in self._chapters:
            c.build_epub(builder)

        builder.end_volume(self._title)

    def valid(self):
        for c in self._chapters:
            if c.valid():
                return True

        return False

class Chapter(object):
    def __init__(self, title):
        logging.debug('create new Chapter:[%s]', title)
        self._title = title
        self._content = []
        self._parent_volume = None

    def __get_parent(self):
        return self._parent_volume

    def __set_parent(self, v):
        logging.debug('update %s \'s parent volume %s', self._title, v._title)
        self._parent_volume = v

    parent_volume = property(__get_parent, __set_parent)

    def add_line(self, line):
        self._content.append(line)

    def append(self, obj):
        self.parent_volume.append(obj)

    def build_epub(self, builder):
        if len(self._content) > 0:
            builder.new_chapter(self._title, self._content)

    def valid(self):
        return len(self._content) > 0

def process_input(config):
    with open(config['input'], 'r') as f_in:
        content = Volume('')
        current = content

        for line in f_in:
            obj = match_volume(config, line)

            if obj:
                content.append(obj)
            else:
                obj = match_chapter(config, line)
                if obj:
                    current.append(obj)

            if obj:
                current = obj
            else:
                current.add_line(line)

        return content

def match_volume(config, line):
    return __match(config, line, 'volume_regex', 'volume_expand', Volume)


def match_chapter(config, line):
    return __match(config, line, 'chapter_regex', 'chapter_expand', Chapter)


def __match(config, line, re_key, expand_key, kcls):
    if re_key not in config:
        return None

    m = re.match(config[re_key], line)

    if m:
        if expand_key in config:
            return kcls(m.expand(config[expand_key]))

        return kcls(m.group(0))

    return None

def generate_epub(config, content):
    EPubBuilder(config, content).build()

if __name__ == '__main__':
    parser = args_parser().parse_args()

    if parser.verbose >= 1:
        logging.getLogger('').setLevel(logging.DEBUG)

    run_main(parser)
