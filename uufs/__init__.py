import sys
from filesystem import UUFS
from setup import Setup
from fuse import FUSE


def main():
    if (len(sys.argv) != 3):
        print("Usage: uufs <root> <mountpoint>")
        sys.exit()

    root = sys.argv[1]
    mountpoint = sys.argv[2]
    s = Setup(root)
    pw = s.login()
    if pw:
        print("Login Successful!")
        print("Mounting filesystem... ", end='')
        FUSE(UUFS(root, pw), mountpoint, nothreads=True, foreground=True)


if __name__ == '__main__':
    main()
