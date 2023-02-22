import hashlib

def hash_function(string):
    return hashlib.sha256(string.encode()).hexdigest()