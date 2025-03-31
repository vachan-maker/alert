import base64
import ecdsa

private_key = ecdsa.SigningKey.generate(curve=ecdsa.NIST256p)
public_key = private_key.get_verifying_key()

vapid_private_key = base64.urlsafe_b64encode(private_key.to_string()).decode("utf-8").strip("=")
vapid_public_key = base64.urlsafe_b64encode(b"\x04" + public_key.to_string()).decode("utf-8").strip("=")

print("Private Key:", vapid_private_key)
print("Public Key:", vapid_public_key)