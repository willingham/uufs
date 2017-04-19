import pyotp, qrcode

key = pyotp.random_base32()
totp = pyotp.TOTP(key)
uri = totp.provisioning_uri(input("Enter Email: "))
qr = qrcode.QRCode()
qr.add_data(uri)
qr.make()
qr.print_tty()
print("Key: " + str(key))


while (True):
    x = input("Enter a key: ")
    print(totp.verify(x))
