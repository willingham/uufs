import sys, os, errno
from fuse import FUSE, FuseOSError, Operations
from simplecrypt import encrypt, decrypt


def decryptFile(pw, inFile, outFile):
    print("### decryptfile")
    with open(inFile, 'rb') as xfile:
        ciphertext = xfile.read()
    print("### decryptfile - Plaintext start")
    plaintext = decrypt(pw, ciphertext)
    print("### decryptfile - Plaintext 1")
    print(plaintext)
    with open(outFile, 'wb+') as yfile:
        yfile.write(plaintext)


def encryptFile(pw, inFile, outFile):
    print("### encryptFile - inFile:  " + inFile)
    print("                - outFile: " + outFile)
    # print("  ### encryptFile - outFile: " + outFile)
    with open(inFile, 'rb') as xfile:
        plaintext = xfile.read()
    print("  ###  - read plaintext")
    # print("  ###  - Plaintext - " + str(plaintext))
    ciphertext = encrypt(pw, plaintext)
    print("  ###  - encrypted plaintext")
    # print("  ###  - ciphertext - " + str(ciphertext))
    with pyopen(outFile, 'wb+') as yfile:
        yfile.write(ciphertext)
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

    def _full_shadow_path(self, partial):
        basename = os.path.basename(partial)
        dirname = os.path.dirname(partial)
        shadow = os.path.join(dirname, "." + basename + ".uufs")
        return self._full_path(shadow)

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
        return os.unlink(self._full_path(path))

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
        fullShadowPath = self._full_shadow_path(path)
        fullPath = self._full_path(path)
        encryptFile(self._pw, fullShadowPath, fullPath)
        ret = os.close(fh)
        print("### release done")
        return ret

    def open(self, path, flags):
        print("### open - " + path)
        base = os.path.basename(path)
        if base.startswith(".") and base.endswith(".uufs"):
            pass
        fullShadowPath = self._full_shadow_path(path)
        fullPath = self._full_path(path)
        isDotFile = os.path.basename(path).startswith(".")
        shadowExists = os.path.isfile(fullShadowPath)
        fileExists = os.path.isfile(fullPath)
        if fileExists and not shadowExists and not path.endswith(".uufs") and not isDotFile: 
            decryptFile(self._pw, fullPath, fullShadowPath)
        if isDotFile:
            ret = os.open(fullPath, flags)
            print("### open done - dotfile")
        ret = os.open(fullShadowPath, flags)
        print("### open done")
        return ret

    def create(self, path, mode, fi=None):
        print("### Create - " + path)
        fullPath = self._full_path(path)
        fullShadowPath = self._full_shadow_path(path)
        print("  ###  - opening")
        fd = os.open(fullPath, os.O_WRONLY | os.O_CREAT, mode)
        print("  ###  - opened, closing")
        os.close(fd)
        print("  ###  - closed")
        ret = os.open(fullShadowPath, os.O_WRONLY | os.O_CREAT, mode)
        print("### - create done")
        return ret

    def read(self, path, length, offset, fh):
        print("### read")
        os.lseek(fh, offset, os.SEEK_SET)
        return os.read(fh, length)

    def write(self, path, buf, offset, fh):
        print("### write")
        print("  ###  - " + path)
        print("  ### " + str(buf))
        os.lseek(fh, offset, os.SEEK_SET)
        ret = os.write(fh, buf)
        print("### write done")
        return ret

    def truncate(self, path, length, fh=None):
        print("### Truncate - " + path)
        fullPath = self._full_path(path)
        fullShadowPath = self._full_shadow_path(path)
        with open(fullShadowPath, 'r+') as xfile:
            xfile.truncate(length)

    def flush(self, path, fh):
        print("### flush")
        ret = os.fsync(fh)
        print("### flush done")

    def fsync(self, path, fdatasync, fh):
        print("### fsync")
        return self.flushk(path, fh)
