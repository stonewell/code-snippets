import archive
from archive_exception import ArchiveException


class LibArchiveImpl(object):
    def __init__(self, file_path, password):
        self.a, err = archive.open_archive(file_path, archive.ARCHIVE_RDONLY)

        if self.a is None:
            raise ArchiveException('unable to open archive {}, error:{}'.format(file_path, err))

        if password:
            err = archive.archive_set_password(self.a, password)

            if e != archive.ARCHIVE_SUCCESS:
                raise ArchiveException('unable to set password, error:{}'.format(err))

    def entries(self):
        count, err = archive.archive_get_entry_count(self.a)

        if err != archive.ARCHIVE_SUCCESS:
            raise ArchiveException('unable to get entry count, error:{}'.format(err))

        for index in range(count):
            e, err = archive.archive_open_entry(self.a, index)

            if err != archive.ARCHIVE_SUCCESS:
                raise ArchiveException('unable to open entry:{}, error:{}'.format(index, err))

            yield e

    def extract_entry(self, e, target_path):
        err = archive.archive_extract_entry(self.a, e, target_path)

        if err != archive.ARCHIVE_SUCCESS:
            raise ArchiveException('unable to extract entry, error:{}'.format(err))

    def entry_fullpath(self, e):
        new_fn, err = archive.entry_get_fullpath(e)

        if err != archive.ARCHIVE_SUCCESS:
            raise ArchiveException('unable to get entry fullpath:{}, error:{}'.format(err))

        return new_fn
