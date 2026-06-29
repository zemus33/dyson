"""Get your Dyson device credentials for config.json.

Run this once to get your serial, credential, and device_type.
Then fill them into config.json along with your device's local IP.
"""
from getpass import getpass
from libdyson.cloud import DysonAccount

print("This will log into your Dyson account to retrieve device credentials.")
print("You'll receive a one-time verification code via email.\n")

region = input("Country code (e.g. US, GB, DE): ")
account = DysonAccount()
email = input("Dyson account email: ")
verify = account.login_email_otp(email, region)
password = getpass("Dyson account password: ")
otp = input("Verification code (check email): ")
verify(otp, password)

devices = account.devices()
for i, d in enumerate(devices):
    print(f"\n--- Device {i+1} ---")
    print(f"  Name: {d.name}")
    print(f"  Serial: {d.serial}")
    print(f"  Device Type: {d.product_type}")
    print(f"  Credential: {d.credential}")

print("\nCopy these values into config.json (see config.example.json)")
