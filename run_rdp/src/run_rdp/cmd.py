'''
run_rdp: help tool to run freerdp
'''

import argparse
import logging
import subprocess

FREERDP_ARGS = [
    '/network:broadband-high',
    '/rfx',
    '/f',
    '/gdi:hw',
    '/sound',
    '/cert:ignore',
    '/bpp:32',
    '+compression',
    '/compression-level:2',
    '/rfx-mode:video',
    '/cache:bitmap,codec:rfx,glyph:on,offscreen:on',
]


def parse_arguments():
  '''
  parse command line arguments
  '''
  parser = argparse.ArgumentParser(prog='run_rdp')
  parser.add_argument('--version', action='version', version='%(prog)s 1.0')

  parser.add_argument("-d",
                      "--debug",
                      help="print debug information",
                      action="count",
                      default=0)
  parser.add_argument("--server",
                      help="remote server name to connect to",
                      type=str,
                      required=False,
                      default=None)
  parser.add_argument("--user", help="Username", type=str, required=False)
  parser.add_argument("--passwd", help="Password", type=str, required=False)
  parser.add_argument("--executable",
                      help="Password",
                      type=str,
                      choices=['xfreerdp', 'wlfreerdp', 'sdl-freerdp'],
                      required=False,
                      default='wlfreerdp')
  parser.add_argument("--proxy",
                      help="socks5 proxy address",
                      type=str,
                      required=False,
                      default='')
  parser.add_argument("--gfx",
                      help="gfx parameters",
                      type=str,
                      choices=['AVC444', 'AVC420', 'RFX'],
                      required=False,
                      default='RFX')
  parser.add_argument('--args-file',
                      type=argparse.FileType('r'),
                      help='plain text file contains argument for freerdp',
                      required=False)

  return parser.parse_args()


def main():
  args = parse_arguments()

  if args.debug > 0:
    logging.getLogger('').setLevel(logging.DEBUG)
  else:
    logging.getLogger('').setLevel(logging.INFO)

  cmd_line = [
      f'/u:{args.user}' if args.user else '',
      f'/p:{args.passwd}' if args.passwd else '',
      f'/v:{args.server}' if args.server else '',
      f'/gfx:{args.gfx},thinclient,progressive',
  ]

  if len(args.proxy) > 0:
    cmd_line.append(f'/proxy:{args.proxy}')

  _args = FREERDP_ARGS[:]

  if args.args_file:
    _args = merge_args(_args, args.args_file.readlines())

  cmd_line = merge_args(_args, cmd_line)

  cmd_line.insert(0, args.executable)

  logging.debug('running cmd line:%s' % cmd_line)

  subprocess.run(cmd_line, check=True, shell=False)


def merge_args(args, new_args):
  args_map = args_to_map(args)
  new_args_map = args_to_map(new_args)

  result = {}
  result.update(args_map)
  result.update(new_args_map)

  logging.debug(f'merge {args_map}, {new_args_map}, result:{result}')
  return [result[k] for k in result]


def args_to_map(args):
  args_map = {}

  for arg in args:
    arg = arg.strip()
    if len(arg) == 0:
      continue
    if not arg[0] in ['/', '+', '-']:
      raise ValueError(f'invalid arg:{arg}')

    key = arg.split(':')[0] if arg[0] == '/' else arg[1:]

    args_map[key] = arg

  return args_map


if __name__ == '__main__':
  main()
