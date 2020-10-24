import argparse
import logging
import os
import sys
import subprocess
import tempfile
import json


def args_parser():
    parser = argparse.ArgumentParser(prog='run_thumbsup',
                                     description='generate static site for photo gallery')
    parser.add_argument('-c', '--config', type=argparse.FileType('r'), help='config file to generate photo gallery', required=False)
    parser.add_argument('-i', '--input', type=str, help='config file to generate photo gallery', required=False)
    parser.add_argument('-o', '--output', type=str, help='config file to generate photo gallery', required=False)
    parser.add_argument('-v', '--verbose', action='count', help='print debug information', required=False, default=0)

    return parser

def run_main(parser):
    config = {}

    if parser.config:
        config.update(json.load(parser.config))

    if parser.input:
        config["input"] = parser.input

    if parser.output:
        config["output"] = parser.output

    if "input" not in config or len(config["input"]) == 0:
        logging.error('invalid input directory:[%s]', config["input"] if "input" in config else "")
        sys.exit(1)

    if "output" not in config or len(config["output"]) == 0:
        logging.error('invalid output directory:[%s]', config["output"] if "output" in config else "")
        sys.exit(1)

    input_dir = os.path.abspath(os.path.expanduser(os.path.expandvars(config["input"])))
    output_dir = os.path.abspath(os.path.expanduser(os.path.expandvars(config["output"])))

    if not os.path.isdir(input_dir):
        logging.error('invalid input directory:[%s]', config["input"])
        sys.exit(1)

    if not os.path.isdir(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    logging.debug("generate config file, replace input and output")
    config["input"] = "/input"
    config["output"] = "/output"

    fd, config_file = tempfile.mkstemp('.json', 'gallery_config')

    try:
        with os.fdopen(fd, 'w') as f:
            json.dump(config, f)

        run_docker(input_dir, output_dir, config_file)
    except:
        os.remove(config_file)
        logging.exception('error running thumsup docker')

def run_docker(input_dir, output_dir, config_file):
    cmd_args = [
        'docker', 'run', '-t',
        '-v', ':'.join([input_dir, '/input', 'ro']),
        '-v', ':'.join([output_dir, '/output']),
        '-v', ':'.join([config_file, '/gallery.json']),
        '-u', ':'.join([str(os.getuid()), str(os.getgid())]),
        'thumbsupgallery/thumbsup',
        'thumbsup',
        '--config', '/gallery.json'
    ]

    proc = subprocess.run(cmd_args,
                          capture_output=False)

    proc.check_returncode()

    return proc

if __name__ == '__main__':
    parser = args_parser().parse_args()

    if parser.verbose >= 1:
        logging.getLogger('').setLevel(logging.DEBUG)

    run_main(parser)
