import os

#SECRET_KEY is a series of cryptographically secure random bytes
#generated with os.urandom(16)

#the secret key previously generated and used for testing (shall be changed
#at the end).
mySecret=b"\xbe3_\xccn\x81\x06_y^1\xf16\x8e\x08\x14"

class Config(object):
    #gets secret from environment variable, or sets it if it is not
    #already available.
    SECRET_KEY = os.environ.get("SECRET_KEY") or mySecret
    #gets the path for where the SQL database file will be saved
    DATABASE = os.path.join(os.getcwd(), "app.db")
