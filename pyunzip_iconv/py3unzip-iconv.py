import os
import string
import shutil

import argparse
import logging
import zipfile
from archive_exception import ArchiveException

logging.getLogger('').setLevel(logging.INFO)

class BuildinZipImpl(object):
    def __init__(self, file_path, password):
        self.zf = zf = zipfile.ZipFile(open(file_path, 'r'))

        if password:
            zf.setpassword(password)

    def entires(self):
        for f_info in zf.infolist():
            yield f_info

    def extract_entry(self, e, target_path):
        with zf.open(member) as source, file(target_path, "wb") as target:
            shutil.copyfileobj(source, target)

    def entry_fullpath(self, e):
        return e.filename


def __extract_member(entry, target_path, new_fn, helper):
    # build the destination pathname, replacing
    # forward slashes to platform specific separators.
    arcname = new_fn.replace('/', os.path.sep)

    if os.path.altsep:
        arcname = arcname.replace(os.path.altsep, os.path.sep)
    # interpret absolute pathname as relative, remove drive letter or
    # UNC path, redundant separators, "." and ".." components.
    arcname = os.path.splitdrive(arcname)[1]
    arcname = os.path.sep.join(x for x in arcname.split(os.path.sep)
                               if x not in ('', os.path.curdir,
                                            os.path.pardir))
    if os.path.sep == '\\':
        # filter illegal characters on Windows
        illegal = ':<>|"?*'
        if isinstance(arcname, unicode):
            table = {ord(c): ord('_') for c in illegal}
        else:
            table = string.maketrans(illegal, '_' * len(illegal))
        arcname = arcname.translate(table)
        # remove trailing dots
        arcname = (x.rstrip('.') for x in arcname.split(os.path.sep))
        arcname = os.path.sep.join(x for x in arcname if x)

    targetpath = os.path.join(target_path, arcname)
    targetpath = os.path.normpath(targetpath)

    # Create all upper directories if necessary.
    upperdirs = os.path.dirname(targetpath)
    if upperdirs and not os.path.exists(upperdirs):
        os.makedirs(upperdirs)

    if helper.entry_fullpath(entry)[-1] == '/':
        if not os.path.isdir(targetpath):
            os.mkdir(targetpath)
        return targetpath

    helper.extract_entry(entry, targetpath)

    return targetpath


def unzip(file_path, f_e, target_path, helper):
    logging.info('unzip {} with encoding from:{}'.format(file_path,
                                                                f_e))
    for e in helper.entries():
        new_fn = helper.entry_fullpath(e)

        if not f_e:
            f_e = 'utf-8'

        new_fn = bytearray(new_fn, 'iso8859-1').decode(f_e, 'ignore')

        logging.info('unzip file:{}'.format(new_fn))
        __extract_member(e,target_path, new_fn, helper)


def args_parser():
    parser = argparse.ArgumentParser(prog='pyunzip-iconv',
                                     description='unzip file with encoding for file name in python')
    parser.add_argument('-f', '--from_encoding',
                        type=str, help='convert file name from encoding',
                        required=False)
    parser.add_argument('-p', '--password',
                        type=str, help='password to decrept the zip file',
                        required=False)
    parser.add_argument('-o', '--target_path',
                        type=str, help='extract files to the target path',
                        required=False,
                        default='.')
    parser.add_argument('--use_libarchive',
                        action='store_true', help='use pylibarchive instead of buildin zip',
                        required=False)
    parser.add_argument(metavar='zip file', type=str,
                        help='file to unzip', dest='file_path')

    return parser


if __name__ == '__main__':
    args = args_parser().parse_args()

    helper = None
    if args.use_libarchive:
        logging.info('use pylibarchive for unzip')
        from libarchive_impl import LibArchiveImpl
        helper = LibArchiveImpl(args.file_path, args.password)
    else:
        logging.info('use buildin zipfile for unzip')
        helper = BuildinZipImpl(args.file_path, args.password)

    unzip(args.file_path,
          args.from_encoding,
          args.target_path,
          helper)
