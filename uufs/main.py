import sys, os
from fuse import FUSE, FuseOSError, Operations

class UUFS(Operations):
    def __init__(self, root):
        self.root = root + '/root'

    def _full_path(self, partial):
        if partial.startswith("/"):
            partial = partial[1:]
        path = os.path.join(self.root, partial)
        return path

    def access(self, path, mode):
        fullPath = self._full_path(path)
        if not os.access(fullPath, mode):
            raise FuseOSError(errno.EACCESS)

    def chmod(self, path, mode):
        fullPath = self._full_path(path)
        return os.chmod(fullPath, mode)

    def chown(self, path, uid, gid):
        fullPath = self._full_path(path)
        return os.chown(fullPath, uid, gid)

    def getattr(self, path, fh=None):
        fullPath = self._full_path(path)
        st = os.lstat(fullPath)
        return dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime', 'st_grid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))

    def readdir(self, path, fh):
        fullPath = self._full_path(path)
        dirents = ['.', '..']
        if os.path.isdir(fullPath):
            dirents.extend(os.listdir(fullPath))
        for item in dirents:
            yield item

    def readlink(self, path):
        pathname = os.readlink(self._full_path(path))
        if pathname.startswith("/"):
            return os.path.relpath(pathname, self.root)
        else:
            return pathname

    def mknod(self, path, mode, dev):
        return os.mknod(self._full_path(path), mode, dev)

    def rmdir(self.path):
        fullPath = self._full_path(path)
        return os.rmdir(full_path)

    def mkdir(self, path, mode):
        return os.mkdir(self._full_path(path), mode)

    def statfs(self, path):
        fullPath = self._full_path(path)
        stv = os.statvfs(fullPath)
        return dict((key, getattr(stv, key)) for key in ('f_bavail', 'f_bfree', 'f_blocks',
            'f_bsize', 'f_favail', 'f_ffree', 'f_files', 'f_flag', 'f_frsize', 'f_namemax'))

        def unlink(self, path):
            return os.unlink(self._full_path(path))

        def symlink(self, name, target):
            return os.symlink(name, self._full_path(target))

        def rename(self, old, new):


        
