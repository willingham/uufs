import sys, os, errno
from fuse import FUSE, FuseOSError, Operations


def decryptFile(pw, xfile):
    print("### decryptfile")
    with open(xfile, 'rb') as fil:
        ciphertext = fil.read()

    if not ciphertext.startswith(b'enc'):
        return True

    print("### decryptfile - Plaintext start")
    ciphertext = ciphertext[3:]
    plaintext = decrypt(pw, ciphertext)
    print("### decryptfile - Plaintext 1")
    with open(xfile, 'wb+') as yfile:
        yfile.write(plaintext)


def encryptFile(pw, xfile):
    print("### encryptFile - inFile:  " + xfile)
    with open(xfile, 'rb') as fil:
        plaintext = fil.read()
    
    if plaintext.startswith(b'enc'):
        print(plaintext)
        return True
    print("  ###  - read plaintext")
    ciphertext = encrypt(pw, plaintext)
    ciphertext = b'enc' + ciphertext
    print("  ###  - encrypted plaintext")
    print(xfile)
    with open(xfile, 'wb+') as fil:
        fil.write(ciphertext)
    print("### encryptFile done")


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
        print("### chmod")
        fullPath = self._full_path(path)
        return os.chmod(fullPath, mode)

    def chown(self, path, uid, gid):
        print("### chown")
        fullPath = self._full_path(path)
        return os.chown(fullPath, uid, gid)

    def getattr(self, path, fh=None):
        #print("### getattr")
        fullPath = self._full_path(path)
        st = os.lstat(fullPath)
        return dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime', 'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))

    def readdir(self, path, fh):
        print("### readdir")
        fullPath = self._full_path(path)
        dirents = ['.', '..']
        if os.path.isdir(fullPath):
            dirents.extend(os.listdir(fullPath))
        for item in dirents:
            yield item

    def readlink(self, path):
        print("### readlink")
        pathname = os.readlink(self._full_path(path))
        if pathname.startswith("/"):
            return os.path.relpath(pathname, self.root)
        else:
            return pathname

    def mknod(self, path, mode, dev):
        print("### mknod")
        return os.mknod(self._full_path(path), mode, dev)

    def rmdir(self, path):
        print("### rmdir")
        fullPath = self._full_path(path)
        return os.rmdir(fullPath)

    def mkdir(self, path, mode):
        print("### mkdir")
        return os.mkdir(self._full_path(path), mode)

    def statfs(self, path):
        #print("### statfs")
        fullPath = self._full_path(path)
        stv = os.statvfs(fullPath)
        return dict((key, getattr(stv, key)) for key in ('f_bavail', 'f_bfree', 'f_blocks',
            'f_bsize', 'f_favail', 'f_ffree', 'f_files', 'f_flag', 'f_frsize', 'f_namemax'))

    def unlink(self, path):
        print("### unlink")
        fullPath = self._full_path(path)
        return os.unlink(fullPath)

    def symlink(self, name, target):
        print("### symlink")
        return os.symlink(name, self._full_path(target))

    def rename(self, old, new):
        print("### rename")
        return os.rename(self._full_path(old), self._full_path(new))

    def link(self, target, name):
        print("### link")
        return os.link(self._full_path(target), self._full_path(name))

    def utimens(self, path, times=None):
        print("### utimens")
        return os.utime(self._full_path(path), times)

    def release(self, path, fh):
        print("### release: " + path)
        fullPath = self._full_path(path)
        ret = os.close(fh)
        print("### release done")
        return ret


    def open(self, path, flags):
        print("### open - " + path)
        fullPath = self._full_path(path)
        decryptFile(self._pw, fullPath)
        ret = os.open(fullPath, flags)
        print("### open done")
        return ret

    def create(self, path, mode, fi=None):
        print("### Create - " + path)
        fullPath = self._full_path(path)
        ret = os.open(fullPath, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, mode)
        print("### create done")
        return ret

    def read(self, path, length, offset, fh):
        print("### read")
        os.lseek(fh, offset, os.SEEK_SET)
        return os.read(fh, length)

    def write(self, path, buf, offset, fh):
        print("### write")
        print("  ###  - " + path)
        # print("  ### " + str(buf))
        os.lseek(fh, offset, os.SEEK_SET)
        ret = os.write(fh, buf)
        print("### write done")
        return ret

    def truncate(self, path, length, fh=None):
        print("### Truncate - " + path)
        fullPath = self._full_path(path)
        with open(fullPath, 'r+') as xfile:
            xfile.truncate(length)

    def flush(self, path, fh):
        print("### flush")
        print("  ### path - " + path)
        print("  ### fh - " + str(fh))
        ret = os.fsync(fh)
        print("### flush done")
        return ret

    def fsync(self, path, fdatasync, fh):
        print("### fsync")
        if fdatasync != 0:
            return os.fsync(fh)
            return os.fdatasync(fh)
        else:
            return os.fsync(fh)
