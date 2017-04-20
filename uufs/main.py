import sys, os
from fuse import FUSE, FuseOSError, Operations

class UUFS(Operations):
    def __init__(self, root):
        self.root = root + '/root'

    def 
