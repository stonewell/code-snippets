import argparse
import logging
import os
import sys
import tempfile
import json
import re

from epub_builder import EPubBuilder, Volume, Chapter


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
                current.add_line(norm_line(line))

        return content

def norm_line(line):
  def repl(match_obj):
    return chr(int(match_obj.group(1)))

  return re.sub('&#([0123456789]+);', repl, line)

def match_volume(config, line):
    return __match(config, line, 'volume_regex', 'volume_expand', 'volume_ignore', Volume)


def match_chapter(config, line):
    return __match(config, line, 'chapter_regex', 'chapter_expand', 'chapter_ignore', Chapter)


def __match(config, line, re_key, expand_key, ignore_key, kcls):
    if re_key not in config:
        return None

    if ignore_key in config:
        m = re.match(config[ignore_key], line)

        if m:
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
