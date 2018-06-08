TODOs
=====

Probably soonish
----------------

* Fix timezone problems
* Work an Beji for Rook image
* Fix NBD support
* Standalone Docker image
* Update website
* Make it possible to import all version metadata from the data backend at once
* Redo animated GIFs ("CLI videos")
* Add script to generate hints from LVM usage bitmaps for classic and thin snapshots
* Finish key rotation support
* Reimplement partial full cleanup

Unsorted collection
-------------------

* Reintroduce Debian or RPM packaging or PEX
* Write a new Makefile for build, test and release
* distutils: Create source distribution again
* Write tests for 100% coverage
* Readd documentation for development setup
* Add tests for anything where scrub marks blocks as invalid (source changed,
  bit rot in backup, ...
* Convert tests (back) to py.test or nose2?
* Check if we really should do image.close() ioctx.close() cluster.shutdown() as
  recommended in http://docs.ceph.com/docs/jewel/rbd/librbdpy/
* io._reader, io.get could return checksum in block (block._replace)...
* Support for multiple data backends
* Support for layering data backends to implement things like mirroring
* Native Google Storage backend
* alembic and database migrations probably need some work
* Better NBD server performance (if possible)