import sys, os, random, datetime, json, getpass # in python library
import bcrypt, pyotp, qrcode # external
from Crypto.Hash import SHA256
from Crypto.Cipher import AES


class AccessControl:
    def __init__(self, sourceDir):
        self._config = {}
        if not os.path.isdir(sourceDir):
            self.error("Directory doesn't exist")
        elif os.listdir(sourceDir) == []:
            self.new_fs(sourceDir)
        elif not os.path.exists(os.path.join(sourceDir, "config.json")):
            self.error("Incorrect filesystem type")
        else:
            with open(os.path.join(sourceDir, "config.json"), "r") as xfile:
                self._config = json.load(xfile)

    def new_fs(self, sourceDir):
        os.mkdir(os.path.join(sourceDir, "root"))
        self._config["password"] = bcrypt.hashpw(self.new_password().encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        self._config["creation"] = str(datetime.datetime.now())
        self._config["status"] = "decrypted"
        self.setup_2fa()
        with open(os.path.join(sourceDir, "config.json"), "w+") as xfile:
            json.dump(self._config, xfile)
        # self.doTestLoop()

    def new_password(self):
        match = False
        while (not match):
            pword = input("Enter a password: ")
            pword2 = input("           Again: ")
            if pword == pword2:
                match = True
            else:
                print("Passwords don't match!")
        self._pword = pword
        return pword

    def setup_2fa(self):
        self._config["otpKey"] = pyotp.random_base32()
        self.totp = pyotp.TOTP(self._config["otpKey"])
        uri = self.totp.provisioning_uri(input("Enter Email: "))
        qr = qrcode.QRCode()
        qr.add_data(uri)
        qr.make()
        qr.print_tty()
        # print("Your secret 2FA key: {}".format(otpHash))

    def doTestLoop(self):
        while (True):
            x = input("Enter a key: ")
            print(self.totp.verify(x))

    def login(self):
        prompt = "Enter Password (attempt {} of 3): "
        for i in range(3):
            p = getpass.getpass(prompt.format(i+1))
            p = p.encode("utf-8")
            r = bcrypt.checkpw(p, self._config["password"].encode("utf-8"))
            if r:
                return p
        return False

    def error(self, message):
        print("Error: {}".format(message))
        sys.exit()

    def _encryptFile(self, fileName):
        encryptedFileName = os.path.basename(fileName) + ".uufs"
        outFile = os.path.join(os.path.dirname(fileName), encryptedFileName)
        fileSize = str(os.path.getsize(fileName)).zfill(16)
        chunkSize = 64 * 1024
        IV = ''

        for i in range(16):
            IV += chr(random.randint(0, 0xFF))

        encryptor = AES.new(self._pw, AES.MODE_CBC, IV)

        with open(fileName, "rb") as inFile:
            with open(outFile, "wb") as outFile:
                outFile.write(fileSize)
                outFile.write(IV)
                while True:
                    chunk = inFile.read(chunkSize)
                    chunkLength = len(chunk)

                    if chunkLength == 0:
                        break
                    elif chunkLength % 16 != 0:
                        chunk += ' ' * (16 - (len(chunk) % 16))

                    outFile.write(encryptor.encrypt(chunk))

    def _decryptFile(self, fileName):
        decryptedFileName = os.path.basename(fileName)[:-5]
        outFile = os.path.join(os.path.dirname(fileName), decryptedFileName)
        chunkSize = 64 * 1024
        with open(fileName, "rb") as inFile:
            fileSize = inFile.read(16)
            IV = inFile.read(16)
            decryptor = AES.new(self._pw, AES.MODE_CBC, IV)

            with open(outFile, "wb") as outFile:
                while True:
                    chunk = inFile.read(chunkSize)
                    if len(chunk) == 0:
                        break

                    outFile.write(decryptor.decrypt(chunk))
                outFile.truncate(int(fileSize))
