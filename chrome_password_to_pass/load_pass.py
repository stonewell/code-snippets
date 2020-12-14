import argparse
import sys
import logging
import csv
import subprocess
from urllib.parse import urlparse


def args_parser():
    parser = argparse.ArgumentParser(prog='load_pass',
                                     description='load chrome password dump file to pass')
    parser.add_argument('-f', '--pass_file', type=argparse.FileType('r'), help='google chrome password dump file', required=True)
    parser.add_argument('-v', '--verbose', action='count', help='print debug information', required=False, default=0)
    return parser

def main():
    parser = args_parser().parse_args()
    if parser.verbose >= 1:
        logging.getLogger('').setLevel(logging.DEBUG)

    reader = csv.reader(parser.pass_file)

    host_pass_map = {}

    for row in reader:
        logging.debug('process pasword:%s', row)

        u = urlparse(row[1])

        if not u.hostname:
            logging.info('skip no hostname password:%s', row)
            continue

        if not row[2]:
            logging.info('skip no username:%s', row)
            continue

        if not row[3]:
            logging.info('skip no password:%s', row)
            continue

        process_password(host_pass_map, u.hostname, row[2], row[3])

    for h, u in host_pass_map:
        logging.info('insert pass for host:%s, user:%s', h, u)
        password = host_pass_map[(h, u)]
        input1 = '%s\n%s\n' % (password, password)

        proc = subprocess.run(['pass', 'insert', '-f', '%s/%s' % (h, u)],
                              input=input1.encode('utf-8'),
                              capture_output=True)

        data = proc.stdout.decode('utf-8', errors='ignore')

        if data:
            logging.info(data)

        data = proc.stderr.decode('utf-8', errors='ignore')

        if data:
            logging.error(data)

        proc.check_returncode()

def process_password(host_pass_map, hostname, username, password):
    logging.debug('process password for host:%s, username:%s', hostname, username)

    hostname = normalize_hostname(hostname)

    exist_host, exist_pass = find_exist(host_pass_map, hostname, username)

    if exist_pass and (exist_pass != password):
        logging.error('found different password %s vs. %s for host:%s, user:%s',
                      exist_pass, password, hostname, username)
        return
    elif exist_pass == password:
        logging.info('skip same password entry for host:%s(%s), username:%s', exist_host, hostname, username)
        return

    host_pass_map[(hostname, username)] = password

def normalize_hostname(hostname):
    parts = hostname.split('.')

    return '.'.join(parts[1:]) if parts[0] == 'www' else '.'.join(parts)

def find_exist(host_pass_map, hostname, username):
    for h, u in host_pass_map:
        if u != username:
            continue

        m_h = match_host(h, hostname)

        if m_h:
            password = host_pass_map[(h, u)]

            if m_h != h:
                del host_pass_map[(h, u)]
                host_pass_map[(m_h, u)] = password

            return m_h, password

    return None, None

def match_host(h1, h2):
    p1 = h1.split('.')
    p2 = h2.split('.')

    len1 = min(len(p1), len(p2))

    for i in range(1, len1+1):
        if p1[-i] != p2[-i]:
            j = i - 1
            if j <= 1:
                return None

            return '.'.join(p1[-j:])

    return '.'.join(p1[-len1:])

if __name__ == '__main__':
    logging.getLogger('').setLevel(logging.INFO)
    main()
