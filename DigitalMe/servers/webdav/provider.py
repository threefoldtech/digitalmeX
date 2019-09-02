# -*- coding: utf-8 -*-
# (c) 2009-2019 Martin Wendt and contributors; see WsgiDAV https://github.com/mar10/wsgidav
# Original PyFileServer (c) 2005 Ho Chun Wei.
# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license.php
"""
Implementation of a DAV provider that serves resource from a file system.

:class:`~wsgidav.fs_dav_provider.FilesystemProvider` implements a DAV resource
provider that publishes a file system.

If ``readonly=True`` is passed, write attempts will raise HTTP_FORBIDDEN.

This provider creates instances of :class:`~wsgidav.fs_dav_provider.FileResource`
and :class:`~wsgidav.fs_dav_provider.FolderResource` to represent files and
directories respectively.
"""
from wsgidav import compat, util
from wsgidav.dav_error import DAVError, HTTP_FORBIDDEN
from wsgidav.dav_provider import DAVCollection, DAVNonCollection, DAVProvider

import os
import sys

from Jumpscale import j

__docformat__ = "reStructuredText"

_logger = util.get_module_logger(__name__)

BUFFER_SIZE = 8192


class IOInterface(object):
    def __init__(self, db, filename):
        self.db = db
        self.filename = filename

    def tell(self):
        raise NotImplementedError

    def read(self, size=-1):
        raise NotImplementedError

    def seek(self, offset, whence=0):
        raise NotImplementedError

    @property
    def name(self):
        raise NotImplementedError

    def write(self, data):
        self.db.file_write(self.filename, data)

    def truncate(self, size=None):
        raise NotImplementedError

    def flush(self):
        raise NotImplementedError

    def fileno(self):
        raise NotImplementedError

# ========================================================================
# FileResource
# ========================================================================


class FileResource(DAVNonCollection):
    def __init__(self, path, environ, file_path):
        super(FileResource, self).__init__(path, environ)
        self._file_path = file_path
        self.name = os.path.basename(self._file_path)
        self.name = compat.to_native(self.name)
        self.db = j.sal.bcdbfs
        self.obj = self.db._file_model.get_by_name(name=self._file_path)[0]

    def get_content_length(self):
        return self.obj.size_bytes

    def get_content_type(self):
        return self.obj.content_type

    def get_creation_date(self):
        return self.obj.epoch

    def get_display_name(self):
        return self.name

    def get_etag(self):
        return '{0}-{1}'.format(self.obj.epoch, self.obj.size_bytes)

    def get_last_modified(self):
        return self.obj.epoch

    def support_etag(self):
        return True

    def support_ranges(self):
        return True

    def get_content(self):
        assert not self.is_collection
        return self.db._file_model.filestream_get(self.obj).read_stream_get()

    def begin_write(self, content_type=None):
        return self.db._file_model.filestream_get(self.obj)

    def delete(self):
        if self.provider.readonly:
            raise DAVError(HTTP_FORBIDDEN)
        self.db.file_delete(self._file_path)

    def copy_move_single(self, dest_path, is_move):
        """See DAVResource.copy_move_single() """
        if self.provider.readonly:
            raise DAVError(HTTP_FORBIDDEN)
        fpDest = self.provider._loc_to_file_path(dest_path, self.environ)
        assert not util.is_equal_or_child_uri(self.path, dest_path)
        self.db.file_copy_form_bcdbfs(self._file_path, fpDest)
        if is_move:
            self.db.file_delete(self._file_path)

    def support_recursive_move(self, dest_path):
        return True

    def move_recursive(self, dest_path):
        if self.provider.readonly:
            raise DAVError(HTTP_FORBIDDEN)
        fpDest = self.provider._loc_to_file_path(dest_path, self.environ)
        assert not util.is_equal_or_child_uri(self.path, dest_path)
        _logger.debug("move_recursive({}, {})".format(self._file_path, fpDest))
        self.db.file_copy_form_bcdbfs(self._file_path, fpDest)
        self.db.file_delete(self._file_path)


    def set_last_modified(self, dest_path, time_stamp, dry_run):
        """Set last modified time for destPath to timeStamp on epoch-format"""
        # Translate time from RFC 1123 to seconds since epoch format
        secs = util.parse_time_string(time_stamp)
        if not dry_run:
            self.obj.epoch = int(secs)
        return True


# ========================================================================
# FolderResource
# ========================================================================
class FolderResource(DAVCollection):
    """Represents a single existing file system folder DAV resource.

    See also _DAVResource, DAVCollection, and FilesystemProvider.
    """

    def __init__(self, path, environ, file_path):
        super(FolderResource, self).__init__(path, environ)
        self._file_path = file_path
        self.db = j.sal.bcdbfs
        self.obj = self.db._dir_model.get_by_name(name=file_path)[0]
        self.name = os.path.basename(self._file_path)
        self.name = compat.to_native(self.name)  # .encode("utf8")

    # Getter methods for standard live properties
    def get_creation_date(self):
        return self.obj.epoch

    def get_display_name(self):
        return self.name

    def get_directory_info(self):
        return None

    def get_etag(self):
        return None

    def get_last_modified(self):
        return self.obj.epoch

    def get_member_names(self):
        nameList = []
        # self._file_path is unicode, so os.listdir returns unicode as well
        assert compat.is_unicode(self._file_path)
        for name in self.db.list_files_and_dirs(self._file_path):
            if not compat.is_unicode(name):
                name = name.decode(sys.getfilesystemencoding())
            assert compat.is_unicode(name)
            # Skip non files (links and mount points)
            fp = name
            if not self.db.is_dir(fp) and not self.db.is_file(fp):
                _logger.debug("Skipping non-file {!r}".format(fp))
                continue
            # name = name.encode("utf8")
            name = compat.to_native(name)
            nameList.append(name)
        return nameList

    def get_member(self, name):
        assert compat.is_native(name), "{!r}".format(name)
        fp = compat.to_unicode(name)
        #        name = name.encode("utf8")
        path = name
        if self.db.is_dir(fp):
            res = FolderResource(path, self.environ, fp)
        elif self.db.is_file(fp):
            res = FileResource(path, self.environ, fp)
        else:
            _logger.debug("Skipping non-file {}".format(path))
            res = None

        return res

    # --- Read / write -------------------------------------------------------

    def create_empty_resource(self, name):
        assert "/" not in name
        if self.provider.readonly:
            raise DAVError(HTTP_FORBIDDEN)
        path = util.join_uri(self.path, name)
        fp = self.provider._loc_to_file_path(path, self.environ)
        self.db.file_create_empty(fp)
        return self.provider.get_resource_inst(path, self.environ)

    def create_collection(self, name):
        assert "/" not in name
        if self.provider.readonly:
            raise DAVError(HTTP_FORBIDDEN)
        path = util.join_uri(self.path, name)
        fp = self.provider._loc_to_file_path(path, self.environ)
        self.db.dir_create(fp)

    def delete(self):
        if self.provider.readonly:
            raise DAVError(HTTP_FORBIDDEN)
        self.db.dir_remove(self._file_path)

    def copy_move_single(self, dest_path, is_move):
        """See DAVResource.copy_move_single() """
        if self.provider.readonly:
            raise DAVError(HTTP_FORBIDDEN)
        fpDest = self.provider._loc_to_file_path(dest_path, self.environ)
        self.db.dir_copy_from_bcdbfs(self._file_path, dest_path)
        assert not util.is_equal_or_child_uri(self.path, dest_path)
        # Create destination collection, if not exists

        if is_move:
            self.db.dir_remove(self._file_path)



    def support_recursive_move(self, dest_path):
        """Return True, if move_recursive() is available (see comments there)."""
        return True

    def move_recursive(self, dest_path):
        """See DAVResource.move_recursive() """
        if self.provider.readonly:
            raise DAVError(HTTP_FORBIDDEN)
        fpDest = self.provider._loc_to_file_path(dest_path, self.environ)
        assert not util.is_equal_or_child_uri(self.path, dest_path)
        _logger.debug("move_recursive({}, {})".format(self._file_path, fpDest))
        self.db.dir_copy_from_bcdbfs(self._file_path, fpDest)
        self.db.dir_remove(self._file_path)
        # (Live properties are copied by copy2 or copystat)
        # Move dead properties

    def set_last_modified(self, dest_path, time_stamp, dry_run):
        """Set last modified time for destPath to timeStamp on epoch-format"""
        # Translate time from RFC 1123 to seconds since epoch format
        secs = util.parse_time_string(time_stamp)
        if not dry_run:
            obj = self.db._dir_model.get_by_name(name=dest_path)[0]
            obj.epoch = int(secs)
            obj.save()
        return True


# ========================================================================
# FilesystemProvider
# ========================================================================
class BCDBFSProvider(DAVProvider):
    def __init__(self, root_folder_path, readonly=False):
        # Expand leading '~' as user home dir; expand %VAR%, $Var, ..
        root_folder_path = os.path.expandvars(os.path.expanduser(root_folder_path))
        root_folder_path = os.path.abspath(root_folder_path)
        self.db = j.sal.bcdbfs
        if not root_folder_path or not self.db.dir_exists(root_folder_path):
            raise ValueError("Invalid root path: {}".format(root_folder_path))

        super(BCDBFSProvider, self).__init__()

        self.root_folder_path = root_folder_path
        self.readonly = readonly

    def __repr__(self):
        rw = "Read-Write"
        if self.readonly:
            rw = "Read-Only"
        return "{} for path '{}' ({})".format(
            self.__class__.__name__, self.root_folder_path, rw
        )

    def _loc_to_file_path(self, path, environ=None):
        """Convert resource path to a unicode absolute file path.
        Optional environ argument may be useful e.g. in relation to per-user
        sub-folder chrooting inside root_folder_path.
        """
        root_path = self.root_folder_path
        assert root_path is not None
        assert compat.is_native(root_path)
        assert compat.is_native(path)

        path_parts = path.strip("/").split("/")
        file_path = os.path.abspath(os.path.join(root_path, *path_parts))
        if not file_path.startswith(root_path):
            raise RuntimeError(
                "Security exception: tried to access file outside root: {}".format(
                    file_path
                )
            )

        # Convert to unicode
        file_path = util.to_unicode_safe(file_path)
        return file_path.rstrip('/') or '/'

    def is_readonly(self):
        return self.readonly

    def get_resource_inst(self, path, environ):
        """Return info dictionary for path.

        See DAVProvider.get_resource_inst()
        """
        self._count_get_resource_inst += 1
        fp = self._loc_to_file_path(path, environ)
        if not self.db.exists(fp):
            return None

        if self.db.is_dir(fp):
            return FolderResource(path, environ, fp)
        return FileResource(path, environ, fp)