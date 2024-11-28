import fcntl
import datetime
import os
import logging
import subprocess
import random
import pathlib
import shutil
import sys


random.seed()

run_file = '/tmp/setwall.run'
open_mode = os.O_RDWR | os.O_CREAT
interval = datetime.timedelta(hours=1)
image_directory = '/media/share/linux/wallpapers'
set_wall_cmd = [os.path.expanduser('~/.setwall')]
wallpaper_path = os.path.expanduser('~/Pictures/wal.jpg')

def do_logging():
  if len(sys.argv) <= 1:
    return False

  for v in sys.argv:
    if v == '-d':
      return True

  return False

def read_last_set_time(fd):

  try:
    line = fd.readline()

    return datetime.datetime.fromisoformat(line)
  except:
    if do_logging():
      logging.exception('unable to read last set time')
    return None

def open_lock_file():
  try:
    return open(run_file, 'r+', encoding='utf-8')
  except:
    return open(run_file, 'w', encoding='utf-8')

def write_last_set_time(job):
  with open_lock_file() as fd:
    try:
       fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)

       last_run = read_last_set_time(fd)

       force_run = (len(sys.argv) > 1 and sys.argv[1] == '1')
       if last_run is None or last_run + interval <  datetime.datetime.now() or force_run:
         job()

         fd.seek(0)
         fd.write(datetime.datetime.now().isoformat())
    except:
      if do_logging():
        logging.exception('unable to lock file to write')
    finally:
       fcntl.flock(fd, fcntl.LOCK_UN | fcntl.LOCK_NB)

def get_wallpaper_file():
  image_files = []

  for root, _, files in pathlib.Path(image_directory).walk(on_error=print):
    image_files.extend(map(lambda p: (root / p), files))

  return random.choice(image_files)

def print_output(r):
  if not do_logging():
    return

  try:
    o = r.stdout.decode('UTF-8')
    e = r.stderr.decode('UTF-8')

    if len(o) > 0:
      print(o)

    if len(e) > 0:
      print(e)
  except:
    logging.exception('decode output failed')

def set_wall():
  new_wallpaper_file = get_wallpaper_file()
  r = subprocess.run(['convert', new_wallpaper_file.as_posix(), wallpaper_path], check=True, capture_output=True)

  print_output(r)

  r = subprocess.run(set_wall_cmd, check=True, capture_output=True)

  print_output(r)

def main():
  write_last_set_time(set_wall)


if __name__ == '__main__':
  main()
