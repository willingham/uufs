import sys, os
from filesystem import UUFS
import filesystem
from setup import Setup
from accesscontrol import AccessControl
from fuse import FUSE


def encryptAll(top, pw):
    print("### encrypt all files")
    for root, dirs, files in os.walk(top):
        path = root.split(os.sep)
        for fil in files:
            filesystem.encryptFile(pw, os.path.join(top, fil))
    print("### encrypt done")

def main():
    if (len(sys.argv) != 3):
        print("Usage: uufs <root> <mountpoint>")
        sys.exit()

    root = sys.argv[1]
    mountpoint = sys.argv[2]
    s = AccessControl(root)
    pw = s.login()
    if pw:
        print("Login Successful!")
        print("Mounting filesystem... ", end='')
        FUSE(UUFS(root, pw), mountpoint, nothreads=True, foreground=True)
        encryptAll(root + "/root", pw)


if __name__ == '__main__':
    main()
