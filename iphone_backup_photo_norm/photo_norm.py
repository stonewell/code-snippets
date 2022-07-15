import sys
import pathlib
import hashlib
import subprocess

from collections import deque

BUILTIN_IGNORE = set(
    ['.git', '.svn', 'CVS', '.hg', '.gitignore', '__pycache__', '.MISC'])


def walk_directory(path):
  children = deque([path])

  while len(children) > 0:
    cur_entry = children.popleft()

    for child in cur_entry.iterdir():
      if child.name in BUILTIN_IGNORE or child.name.startswith('.'):
        continue

      if child.is_file():
        yield child
      elif child.is_dir():
        children.append(child)


if __name__ == '__main__':
  for p in walk_directory(pathlib.Path(sys.argv[1]).cwd()):
    if p.suffix == '.HEIC':
      md5 = hashlib.md5(p.read_bytes()).hexdigest()

      p_mov = p.with_suffix('.MOV')

      p_jpeg = p.with_stem(f'{p.stem}_{ md5}').with_suffix('.jpeg')

      if not p_jpeg.exists():
        subprocess.run(['/usr/bin/convert',
                        p.as_posix(),
                        p_jpeg.as_posix()])

      print(f'processed {p.as_posix()}')

      if p_mov.exists():
        p_mov_bak = p_mov.with_suffix(f'.{md5}')

        try:
          p_mov.rename(p_mov_bak)
          pass
        except(FileExistsError):
          pass

        p_mov.unlink(True)
