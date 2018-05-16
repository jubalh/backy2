import unittest

from . import DatabackendTestCase


class test_s3(DatabackendTestCase, unittest.TestCase):
    CONFIG = """
        configurationVersion: '1.0.0'
        logFile: /dev/stderr
        lockDirectory: {testpath}/lock
        hashFunction: blake2b,digest_size=32
        dataBackend:
          type: s3
          s3:
            awsAccessKeyId: minio
            awsSecretAccessKey: minio123
            host: 127.0.0.1
            port: 9901
            isSecure: False
            bucketName: backy2
            consistencyCheckWrites: True
          simultaneousWrites: 5
          simultaneousReads: 5
          bandwidthRead: 0
          bandwidthWrite: 0        
        """

if __name__ == '__main__':
    unittest.main()
