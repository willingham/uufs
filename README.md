# UUFS
UUFS is an encrypted FUSE filesystem with 2fa.

## Overview
There are many encrypted filesystems that currently exist, but none of them support two-factor authentication to my knowledge.  UUFS implements a unique encryption strategy along with 2fa, making it the only FUSE filesystem of its kind.

## Implementation
UUFS is implemented using [Filesystem in Userspace (FUSE)](https://github.com/libfuse/libfuse).  This allowed access to system apis, and through the use of [fusepy](https://github.com/terencehonles/fusepy), it allowed access to python cryptographic libraries.

### External Python Modules Used
* [fusepy](https://github.com/terencehonles/fusepy) - Interface to FUSE
* [simple-crypt](https://github.com/andrewcooke/simple-crypt) - Encryption library that uses [pycrypto](https://www.dlitz.net/software/pycrypto/) underneath.
* [pyotp](https://github.com/pyotp/pyotp) - Implements the RFC 6238 TOTP algorithm in python.
* [qrcode](https://pypi.python.org/pypi/qrcode) - Used for generation of qrcodes for TOTP apps.
* [bcrypt](https://pypi.python.org/pypi/bcrypt/3.1.0) - Used for hashing and authenticating passwords.

### Supported Filesystem Operations
The following operations are supported.
* access
* chmod
* chown
* getattr
* readdir
* readlink
* mknod
* rmdir
* mkdir
* statfs
* unlink
* symlink
* rename
* link
* utimens
* release
* open
* create
* read
* write
* truncate
* flush
* fsync

### Unique Encryption Scheme
In today's society there is evermore the need for encryption.  It is not uncommon for the border security of different countries so search the electronic devices of those crossing the border.  In oppressive societies, or those that want to control what the rest of the world sees about them, this can pose an issue for photographers and other media professionals.  This filesystem aims to help with this problem by encrypting one's files.

Many filesystems encrypt and decrypt files blocks at a time while they are being used.  While this strategy works well for many instances, it may drastically hinder performance when working with digital media.  Many media management and editing programs such as Adobe Lightroom and Adobe Photoshop will perform many reads and writes to the system while they are working with files.  Since these files can be extremely large, this can be very costly and time-consuming while one is editing or working with media.

UUFS implements a new strategy such that a file is decrypted in its entirety the first time that is needed.  On each subsequent usage of the file, it can be accessed with no delay from the encryption.  Then, once the filesystem is being unmounted, all of the files that have been unencrypted will be encrypted.  

While this strategy is not perfect for every scenario, it will greatly help those who use software that reads and writes large amounts of data to the disk often.

## Installation
### High level
You will need to install python3 and pip3 to install all the dependencies for UUFS.  It is also beneficial to install and use a virtualenv.  This may make installation more smooth.

### Detailed (MacOS w/ homebrew)
* Install python3 & pip3 `brew install python3`
* Install virtualenv `pip install virtualenv`
* Get a copy of the source code
* From within the top-level source code directory, setup a virtualenv `virtualenv -p python3`
* Activate the virtualenv `source bin/activate`
* Install dependencies `pip3 install -r requirements.txt`
 * If you get an error when pip is trying to install pycrypto, see [this stackoverflow post](http://stackoverflow.com/questions/15375171/pycrypto-install-fatal-error-gmp-h-file-not-found)
* Once the dependencies are installed successfully, run the filesystem with `./run.sh <source directory> <mountpoint>`

## Usage
UUFS takes a directory with the UUFS structure and mounts it on the system.  To create a new filesystem, create an empty directory, then run
'/path/to/run.sh <the empty folder> <the place you want to mount it on>`
UUFS will then prompt you to enter a password for encrypting your filesystem.  Warning: This password cannot be recovered if you lose it, so don't forget it.

Then, UUFS will generate a qrcode for the two-factor authentication.  You can use Google Authenticator, or any other app that supports the RFC 6238 TOTP algorithm.  Scan the qrcode with the app.  Once this happens, you will be prompted for your password again.  Once you have entered it, you will be able to use the filesystem like any other.

When you wish to unmount the filesystem, run `umount <mountpoint>`.  This will encrypt all your data stored in the filesystem.

When you wish to use the filesystem in the future, you can run the same run.sh command.  You will be prompted for your password, and then for a totp key.


