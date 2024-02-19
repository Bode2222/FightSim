import hashlib


def string_to_32bit_int(input_string):
    # Use the hashlib library to get a hash object
    hash_object = hashlib.md5(input_string.encode())
    # Get the hexadecimal representation of the hash
    hex_digest = hash_object.hexdigest()
    # Convert the hexadecimal string to a 32-bit integer
    hash_int = int(hex_digest, 16) & 0xFFFFFFFF  # Use bitwise AND to limit to 32 bits
    return hash_int
