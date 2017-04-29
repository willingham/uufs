# UUFS
UUFS is an encrypted FUSE filesystem with 2fa.

## Overview
There are many encrypted filesystems that currently exist, but none of them support two-factor authentication to my knowledge.  UUFS implements a unique encryption strategy along with 2fa, making it the only FUSE filesystem of its kind.

## Implementation

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


