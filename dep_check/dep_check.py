import os


def get_str_after_first_nondrive_colon(line):
    if line.find(":") >= 0:
        # find first : not followed by / or \
        start = 0
        while True:
            pos = line.find(":", start)

            if pos < 0:
                start = 0
                break

            if (pos + 1 < len(line)
                and line[pos + 1] != '\\'
                and line[pos + 1] != '/'):
                start = pos + 1
                break

            start = pos + 1

        if start > 0:
            line = line[start + 1:]

    return line


def remove_all_double_backslash(line):
    old_len = 0

    if len(line) == 0:
        return line

    while old_len != len(line):
        old_len = len(line)
        line = line.replace('\\\\', '\\')

    return line


def get_files_from_line(line):
    start = 0

    parts = []
    for i in range(len(line)):
        if (line[i] == ' '):
            if (i > 0 and line[i - 1] == '\\'):
                # remove the backslash
                parts.append(line[start:i - 1])
            else:
                # find a valid file name
                parts.append(line[start:i])
                yield ' '.join(parts)
                parts = []
            start = i + 1

    if start < len(line):
        parts.append(line[start:])

    if len(parts) > 0:
        yield ' '.join(parts)


def read_dep_file(dep_file):
    dep_file_list = []

    with open(dep_file) as f:
        for line in f:
            line = line.replace('\n', '')
            line = line.replace('\r', '')
            line = line.strip()

            # remove trail backslash
            if line[-1] == '\\':
                line = line[:-1].strip()

            line = get_str_after_first_nondrive_colon(line)
            line = remove_all_double_backslash(line)

            dep_file_list.extend(get_files_from_line(line))

    return dep_file_list


def get_last_change_time(file_path):
    if not os.path.isfile(file_path):
        return 0

    return os.stat(file_path).st_mtime


def need_recreate_target(src_list, dep_file, target_file_list):
    if (not all(map(os.path.isfile, target_file_list))
            or (dep_file is not None and not os.path.isfile(dep_file))):
        return True

    dep_file_list = read_dep_file(dep_file) if dep_file is not None else []

    src_latest_time = max(max(map(get_last_change_time, src_list)) if len(src_list) > 0 else 0,
                          max(map(get_last_change_time, dep_file_list)) if len(dep_file_list) > 0 else 0)
    target_oldest_time = min(map(get_last_change_time, target_file_list)) if len(target_file_list) > 0 else 0

    return src_latest_time > target_oldest_time


if __name__ == '__main__':
    # print need_recreate_target(['d:\\depot_cp3_trunk\\cp3\\staged\\trunk\\2.3.0\\1\\data\\utils\\cp3_instrument.exe'],
    #                            r'd:\depot_cp3_trunk\cp3\staged\trunk\2.3.0\1\intermediate_files\test_timeout\x64-windows-clang\release\foo.Po',
    #                            [u'd:\\depot_cp3_trunk\\cp3\\staged\\trunk\\2.3.0\\1\\intermediate_files\\test_timeout\\x64-windows-clang\\release\\foo.ll',
    #                             u'd:\\depot_cp3_trunk\\cp3\\staged\\trunk\\2.3.0\\1\\intermediate_files\\test_timeout\\x64-windows-clang\\release\\foo_instrumented.ll',
    #                             u'd:\\depot_cp3_trunk\\cp3\\staged\\trunk\\2.3.0\\1\\intermediate_files\\test_timeout\\x64-windows-clang\\release\\foo_instrumented.o'])

    # print read_dep_file(r'd:\depot_cp3_trunk\cp3\staged\trunk\2.3.0\1\1')
    # print map(os.path.isfile, read_dep_file(r'd:\depot_cp3_trunk\cp3\staged\trunk\2.3.0\1\1'))
    # print all(map(os.path.isfile, read_dep_file(r'd:\depot_cp3_trunk\cp3\staged\trunk\2.3.0\1\1')))

    print read_dep_file(r'1')
    print map(os.path.isfile, read_dep_file(r'1'))
    print all(map(os.path.isfile, read_dep_file(r'1')))
