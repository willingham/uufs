import sys, os, errno
from fuse import FUSE, FuseOSError, Operations
from simplecrypt import encrypt, decrypt


class UUFS(Operations):
    def __init__(self, root, pw):
        self.root = root + '/root'
        self._pw = pw
        print("Done")

    def _full_path(self, partial):
        if partial.startswith("/"):
            partial = partial[1:]
        path = os.path.join(self.root, partial)
        return path

    def access(self, path, mode):
        fullPath = self._full_path(path)
        if not os.access(fullPath, mode):
            raise FuseOSError(errno.EACCES)

    def chmod(self, path, mode):
        fullPath = self._full_path(path)
        return os.chmod(fullPath, mode)

    def chown(self, path, uid, gid):
        fullPath = self._full_path(path)
        return os.chown(fullPath, uid, gid)

    def getattr(self, path, fh=None):
        fullPath = self._full_path(path)
        st = os.lstat(fullPath)
        return dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime', 'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))

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

    def rmdir(self, path):
        fullPath = self._full_path(path)
        return os.rmdir(fullPath)

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
        return os.rename(self._full_path(old), self._full_path(new))

    def link(self, target, name):
        return os.link(self._full_path(target), self._full_path(name))

    def utimens(self, path, times=None):
        return os.utime(self._full_path(path), times)

    def encryptFile(self, inFile, outFile):
        with open(inFile, 'rb') as xfile:
            plaintext = xfile.read()
        ciphertext = encrypt(self._pw, plaintext)
        with open(outFile, 'wb+') as yfile:
            yfile.write(iv + cipher.encrypt(plaintext))

    def decryptFile(self, inFile, outFile):
        with open(inFile, 'rb') as xfile:
            ciphertext = xfile.read()
        plaintext = decrypt(self._pw, ciphertext)
        with open(outFile, 'wb+') as yfile:
            yfile.write(plaintext.rstrip(b"\0"))

    def open(self, path, flags):
        print(path)
        temp = list(os.path.split(path))
        temp[-1] = "{}{}".format(temp[-1], '.uufs')
        shaddow = os.path.join(*temp)
        fullShaddowPath = self._full_path(shaddow)
        fullPath = self._full_path(path)
        if not os.path.isfile(fullShaddowPath):
            self.decryptFile(fullPath, fullShaddowPath)
        
        return os.open(fullShaddowPath, flags)

    def create(self, path, mode, fi=None):
        fullPath = self._full_path(path)
        return os.open(fullPath, os.O_WRONLY | os.O_CREAT, mode)

    def read(self, path, length, offset, fh):
        os.lseek(fh, offset, os.SEEK_SET)
        return os.read(fh, length)

    def write(self, path, buf, offset, fh):
        os.lseek(fh, offset, os.SEEK_SET)
        return os.write(fh, buf)

    def truncate(self, path, length, fh=None):
        fullPath = self._full_path(path)
        with open(fullPath, 'r+') as xfile:
            xfile.truncate(length)

    def flush(self, path, fh):
        return os.fsync(fh)

    def release(self, path, fh):
        ret = os.close(fh)
        print("### Close: " + path)


    def fsync(self, path, fdatasync, fh):
        return self.flush(path, fh)
