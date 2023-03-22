'''
run_rdp: help tool to run freerdp
'''
import os
import sys

import argparse
import logging
import pathlib
import subprocess

FREERDP_ARGS = [
    '/network:lan',
    '/rfx',
    '/f',
    '/gfx:AVC420,thinclient,progressive',
    '/gdi:hw',
    '/sound',
    '/cert:ignore',
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
                      required=True,
                      default=None)
  parser.add_argument("--user", help="Username", type=str, required=True)
  parser.add_argument("--passwd", help="Password", type=str, required=True)
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
  return parser.parse_args()


def main():
  args = parse_arguments()

  if args.debug > 0:
    logging.getLogger('').setLevel(logging.DEBUG)
  else:
    logging.getLogger('').setLevel(logging.INFO)

  cmd_line = [
    args.executable,
    f'/u:{args.user}',
    f'/p:{args.passwd}',
    f'/v:{args.server}',
  ]

  if len(args.proxy) > 0:
    cmd_line.append(f'/proxy:{args.proxy}')

  cmd_line.extend(FREERDP_ARGS)

  logging.debug('running cmd line:%s' % cmd_line)
  subprocess.run(cmd_line, check=True, shell=False)


if __name__ == '__main__':
  main()
