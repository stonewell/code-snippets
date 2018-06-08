import re
from pathlib import Path
import subprocess


prog = re.compile('(?P<track>[0-9][0-9])\s(?P<name>\w+)（(?P<author>[\w\s]+)）')

p = Path('.')

for f in p.glob('*.wav'):
    m = prog.match(str(f))

    args = ['flac',
            '-o', '%s.%s-%s.flac' % (m.group('track'), m.group('author').replace(' ', '_'), m.group('name')),
            '-T', 'TITLE=%s' % m.group('name'),
            '-T', 'TRACKNUMBER=%s' % m.group('track')]

    for author in m.group('author').split(' '):
        args.extend(['-T', 'ARTIST=%s' % author])

    args.append(str(f))

    subprocess.run(args)
