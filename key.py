from py_vapid import Vapid

# Create an instance of the Vapid class
vapid = Vapid()

# Generate a new pair of VAPID keys
vapid_keys = vapid.generate_keys()

# Print the generated keys
print("VAPID Keys:", vapid_keys)
