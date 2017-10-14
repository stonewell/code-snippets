import os
import string
import shutil

import argparse
import logging
import zipfile


logging.getLogger('').setLevel(logging.INFO)


def __extract_member(zf, member, target_path, new_fn):
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

    if member.filename[-1] == '/':
        if not os.path.isdir(targetpath):
            os.mkdir(targetpath)
        return targetpath

    with zf.open(member) as source, file(targetpath, "wb") as target:
        shutil.copyfileobj(source, target)

    return targetpath


def unzip(file_path, f_e, t_e, target_path, password):
    logging.info('unzip {} with encoding from:{}, to:{}'.format(file_path,
                                                                f_e,
                                                                t_e))

    with zipfile.ZipFile(open(file_path, 'r')) as zf:
        if password:
            zf.setpassword(password)

        if f_e is None and t_e is None:
            zf.extractall(target_path)
            return

        for f_info in zf.infolist():
            new_fn = f_info.filename

            if f_e:
                new_fn = new_fn.decode(f_e)

            if t_e:
                new_fn = new_fn.encode(t_e)

            logging.info(u'unzip file:{}'.format(new_fn))
            __extract_member(zf, f_info, target_path, new_fn)


def args_parser():
    parser = argparse.ArgumentParser(prog='pyunzip-iconv',
                                     description='unzip file with encoding for file name in python')
    parser.add_argument('-f', '--from_encoding',
                        type=str, help='convert file name from encoding',
                        required=False)
    parser.add_argument('-t', '--to_encoding',
                        type=str, help='convert file name to encoding',
                        required=False)
    parser.add_argument('-p', '--password',
                        type=str, help='password to decrept the zip file',
                        required=False)
    parser.add_argument('-o', '--target_path',
                        type=str, help='extract files to the target path',
                        required=False,
                        default='.')
    parser.add_argument(metavar='zip file', type=str,
                        help='file to unzip', dest='file_path')

    return parser


if __name__ == '__main__':
    args = args_parser().parse_args()
    unzip(args.file_path,
          args.from_encoding,
          args.to_encoding,
          args.target_path,
          args.password)
