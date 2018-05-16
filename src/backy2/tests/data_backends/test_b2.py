import unittest

from . import DatabackendTestCase


class test_b2(DatabackendTestCase, unittest.TestCase):
    CONFIG = """
        configurationVersion: '1.0.0'
        logFile: /dev/stderr
        lockDirectory: {testpath}/lock
        hashFunction: blake2b,digest_size=32
        dataBackend:
          type: b2
          b2:
             accountId: ********
             applicationKey: *******************************
             bucketName: backy2
             accountInfoFile: {testpath}/b2_account_info
             compression:
               - name: zstd
                 materials:
                   level: 1
                 active: true
              
             encryption:
               - name: aws_s3_cse
                 materials:
                   masterKey: !!binary |
                     e/i1X4NsuT9k+FIVe2kd3vtHVkzZsbeYv35XQJeV8nA=
                 active: true       
             consistencyCheckWrites: True      
          simultaneousWrites: 5
          simultaneousReads: 5
          bandwidthRead: 0
          bandwidthWrite: 0
        """

if __name__ == '__main__':
    unittest.main()
