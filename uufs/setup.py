import sys, os, bcrypt, datetime, pyotp, qrcode, hashlib, base64

class Setup:
    def __init__(self, sourceDir):
        self._config = {}
        if not os.path.isdir(sourceDir):
            self.exit("Directory doesn't exist")
        elif os.listdir(sourceDir) == []:
            self.new_fs(sourceDir)
        elif not os.path.exists(os.path.join(sourceDir, "config.json")):
            self.exit("Incorrect filesystem type")

    def new_fs(self, sourceDir):
        #os.mkdir(os.path.join(sourceDir, "root"))
        self._config["password"] = bcrypt.hashpw(self.new_password().encode('utf-8'), bcrypt.gensalt())
        self._config["creation"] = datetime.datetime.now()
        self.setup_2fa()
        self.doTestLoop()

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
        otpHash = hashlib.sha256(str(self._pword + str(self._config["password"])).encode('utf-8')).digest()
        print(otpHash)
        otpHash = base64.b32encode(otpHash)
        print(otpHash)
        self.totp = pyotp.TOTP(otpHash)
        uri = self.totp.provisioning_uri(input("Enter Email: "))
        qr = qrcode.QRCode()
        qr.add_data(uri)
        qr.make()
        qr.print_tty()
        #print("Your secret 2FA key: {}".format(otpHash))

    def doTestLoop(self):
        while (True):
            x = input("Enter a key: ")
            print(self.totp.verify(x))

    def exit(self, message):
        print("Error: {}".format(message))
        sys.exit()
