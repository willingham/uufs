import sys, os, datetime, json, getpass # in python library
import bcrypt, pyotp, qrcode # external


class Setup:
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
        for i in range(3):
            #p = getpass.getpass("Enter Password (attempt {} of 3): ".format(i+1))
            p = "asdf"
            r = bcrypt.checkpw(p.encode("utf-8"), self._config["password"].encode("utf-8"))
            if r:
                return p
        return False

    def error(self, message):
        print("Error: {}".format(message))
        sys.exit()
