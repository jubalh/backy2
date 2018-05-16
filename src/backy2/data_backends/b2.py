#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import hashlib
import logging
import urllib

import b2
import b2.api
import b2.file_version
from b2.account_info.exception import MissingAccountData
from b2.account_info.in_memory import InMemoryAccountInfo
from b2.account_info.sqlite_account_info import SqliteAccountInfo
from b2.download_dest import DownloadDestBytes
from b2.exception import B2Error, FileNotPresent, UnknownError
from backy2.data_backends import ReadCacheDataBackend
from backy2.exception import UsageError
from backy2.meta_backends.sql import BlockUid


class DataBackend(ReadCacheDataBackend):
    """ A DataBackend which stores its data in a BackBlaze (B2) file store."""

    NAME = 'b2'

    WRITE_QUEUE_LENGTH = 20
    READ_QUEUE_LENGTH = 20

    SUPPORTS_PARTIAL_READS = False
    SUPPORTS_PARTIAL_WRITES = False
    SUPPORTS_METADATA = True

    def __init__(self, config):
        super().__init__(config)

        our_config = config.get('dataBackend.{}'.format(self.NAME), types=dict)
        account_id = config.get_from_dict(our_config, 'accountId', types=str)
        application_key = config.get_from_dict(our_config, 'applicationKey', types=str)
        bucket_name = config.get_from_dict(our_config, 'bucketName', types=str)
        account_info_file = config.get_from_dict(our_config, 'accountInfoFile', None, types=str)

        if account_info_file is not None:
            account_info = SqliteAccountInfo(file_name=account_info_file)
        else:
            account_info = InMemoryAccountInfo()

        self.service = b2.api.B2Api(account_info)
        if account_info_file is not None:
            try:
                # This temporarily disables all logging as the b2 library does some very verbose logging
                # of the exception we're trying to catch here...
                logging.disable(logging.ERROR)
                _ = self.service.get_account_id()
                logging.disable(logging.NOTSET)
            except MissingAccountData:
                self.service.authorize_account('production', account_id, application_key)
        else:
            self.service.authorize_account('production', account_id, application_key)
            
        self.bucket = self.service.get_bucket_by_name(bucket_name)

    @staticmethod
    def _block_uid_to_key(block_uid):
        key_name = '{:016x}-{:016x}'.format(block_uid.left, block_uid.right)
        hash = hashlib.md5(key_name.encode('ascii')).hexdigest()
        return '{}/{}/{}-{}'.format(hash[0:2], hash[2:4], hash[:8], key_name)

    @staticmethod
    def _key_to_block_uid(key):
        if len(key) != 48:
            raise RuntimeError('Invalid key name {}'.format(key))
        return BlockUid(int(key[15:15 + 16], 16), int(key[32:32 + 16], 16))

    def _write_object(self, key, data, metadata):
        if len(metadata) > 10:
            raise RuntimeError('Maximum number of metadata entries exceed. ' +
                               'Please change your compression or encryption settings for this backend.')
        self.bucket.upload_bytes(data, key, file_infos=metadata)

    def _read_object(self, key, offset=0, length=None):
        data_io = DownloadDestBytes()
        try:
            self.bucket.download_file_by_name(key, data_io)
        except B2Error as e:
            # Currently FileNotPresent isn't always signaled correctly.
            # See: https://github.com/Backblaze/B2_Command_Line_Tool/pull/436
            if isinstance(e, FileNotPresent) or isinstance(e, UnknownError) and "404 not_found" in str(e):
            #if isinstance(e, FileNotPresent):
                raise FileNotFoundError('UID {} not found.'.format(key)) from None
            else:
                raise

        # B2 URL escapes the value so we need to decode it
        metadata = data_io.file_info
        for name in metadata.keys():
            metadata[name] = urllib.parse.unquote(metadata[name])

        return data_io.get_bytes_written(), metadata

    def _file_info(self, key):
        r = self.bucket.list_file_names(key, 1)
        for entry in r['files']:
            file_version_info = b2.file_version.FileVersionInfoFactory.from_api_response(entry)
            if file_version_info.file_name == key:
                return file_version_info

        raise FileNotFoundError('UID {} not found.'.format(key))

    def _rm_object(self, key):
        try:
            file_version_info = self._file_info(key)
            self.bucket.delete_file_version(file_version_info.id_, file_version_info.file_name)
        except B2Error as e:
            # Currently FileNotPresent isn't always signaled correctly.
            # See: https://github.com/Backblaze/B2_Command_Line_Tool/pull/436
            if isinstance(e, FileNotPresent) or isinstance(e, UnknownError) and "404 not_found" in str(e):
            #if isinstance(e, FileNotPresent):
                raise FileNotFoundError('UID {} not found.'.format(key)) from None
            else:
                raise

    def _rm_many_objects(self, keys):
        """ Deletes many keys from the data backend and returns a list
        of keys that couldn't be deleted.
        """
        errors = []
        for key in keys:
            try:
                file_version_info = self._file_info(key)
                self.bucket.delete_file_version(file_version_info.id_, file_version_info.file_name)
            except (B2Error, FileNotFoundError):
                errors.append(key)
        return errors

    def _list_objects(self, prefix=None):
        if prefix:
            raise UsageError('Specifying a prefix isn\t implemented for this backend yet.')
        return [file_version_info.file_name
                for (file_version_info, folder_name) in self.bucket.ls()]

