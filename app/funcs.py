import re
import uuid
from time import time
from . import db
from . import gmail
from passlib.hash import pbkdf2_sha512 as passHash

#set time for emailsSent to 'reset' in seconds
RESET_TIME = 60*60
#set max number of emailsSent in one window of RESET_TIME
LIMIT = 3
#set time for token to expire in seconds
EXPIRY_TIME = 30*60

#given an email, returns the userID - does not need to close DB since it is never used
#by itself - also does not make any changes to DB.
def getID(email):
    conn = db.get_db()
    cur = conn.cursor()
    cur.execute("SELECT UserID FROM Registrants WHERE Email = (?)",
                (email,))
    return cur.fetchone()[0]

#takes an email and returns whether or not it exists in the database.
def emailExists(email):
    #connect to database
    conn = db.get_db()
    cur = conn.cursor()
    #query the email from the database
    cur.execute("SELECT Email FROM Registrants WHERE Email = (?);",
                (email,))
    storedEmail = cur.fetchone()
    #ensure to close connection
    db.close_db()
    #if it does not exist, it is None (evaluates to False)
    return storedEmail

#takes an email and password and returns whether the password matches the hash for that email.
def checkPassword(email, password):
    conn = db.get_db()
    cur = conn.cursor()
    cur.execute("SELECT PasswordHash FROM Registrants WHERE Email = (?);",
                (email,))
    #get hash from tuple
    storedHash = cur.fetchone()[0]
    db.close_db()
    #check if hashes match
    return passHash.verify(password, storedHash)

#takes an email and returns whether it ends in @gmail.com or in @googlemail.com
def isGmail(email):
    return re.search(r'@gmail\.com\Z$', email) or \
           re.search(r'@googlemail\.com\Z$', email)

#creates a new user record in Registrants, given their email.
def createUser(email):
    userID = str(uuid.uuid4())
    conn = db.get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO Registrants (UserID, Email, EmailsSent) VALUES (?, ?, ?);",
                (userID, email, 0))
    #cur.commit()
    updateResetTime(email)
    db.close_db()

#takes an email and returns whether its user can send another email.
def checkNumEmails(email):
    conn = db.get_db()
    cur = conn.cursor()
    cur.execute("SELECT EmailsSent, ResetTime FROM Registrants WHERE Email = (?);",
                (email,))
    tup = cur.fetchone()
    db.close_db()
    numSent = tup[0]
    resetTime = tup[1]
    #user reached the email limit.
    if numSent >= LIMIT:
        currentTime = time()
        difference = resetTime - currentTime
        #check if they have waited enough to reset the number of emails.
        if difference>0:
            return False
        #renew reset time since we have gone past it.
        updateResetTime(email)
    #returns True otherwise
    return True

#takes an email and resets its ResetTime (for emails sent for registering).
def updateResetTime(email):
    newTime = int(time() + RESET_TIME)
    conn = db.get_db()
    cur = conn.cursor()
    cur.execute("UPDATE Registrants SET ResetTime = ? WHERE Email = ?",
                (newTime, email))
    db.close_db()

#takes an email and returns the token assigned for them after inserting it
#into the database.
def createToken(email):
    #generates token and hash.
    token = str(uuid.uuid4())
    tokenHash = passHash.hash(token)
    #gets current time and expiry time.
    currentTime = time()
    expiryTime = int(currentTime + EXPIRY_TIME)
    conn = db.get_db()
    cur = conn.cursor()
    userID = getID(email)
    cur.execute("INSERT INTO Codes(TokenHash, UserID, ExpirationTime) VALUES (?, ?, ?);",
                (tokenHash, userID, expiryTime))
    db.close_db()
    return token

#takes a code and email, and returns whether the code is valid.
def checkToken(code, email):
    conn = db.get_db()
    cur = conn.cursor()
    userID = getID(email)
    cur.execute("SELECT TokenHash FROM Codes WHERE UserID = (?);",
                (userID,))
    #get all codes stored for user
    storedHashList = cur.fetchall()
    db.close_db()
    #check all hashes for validity
    for storedHash in storedHashList:
        if passHash.verify(code, storedHash[0]):
            return True
    return False

#takes a code and email, and returns whether a code has expired or not.
def isValid(code, email):
    currentTime = time()
    conn = db.get_db()
    cur = conn.cursor()
    userID = getID(email)
    cur.execute("SELECT ExpirationTime FROM Codes WHERE UserID = (?);",
                (userID,))
    expirationTime = cur.fetchone()[0]
    db.close_db()
    #still before the expiry time?
    return currentTime < expirationTime

#takes an email and deletes all of that user's tokens saved in the database.
def clearTokens(email):
    conn = db.get_db()
    cur = conn.cursor()
    userID = getID(email)
    cur.execute("DELETE FROM Codes WHERE UserID = (?);",
                (userID,))
    db.close_db()

def lengthCheck(password, MIN_LENGTH):
    return len(password) >= MIN_LENGTH

def lowerCheck(password, MIN_LOWER):
    return len(re.findall(r'[a-z]', password)) >= MIN_LOWER

def upperCheck(password, MIN_UPPER):
    return len(re.findall(r'[A-Z]', password)) >= MIN_UPPER

def numCheck(password, MIN_NUM):
    return len(re.findall(r'[0-9]', password)) >= MIN_NUM

def symbolCheck(password, MIN_SYMBOL):
    return len(re.findall(r'[^a-zA-Z0-9]', password)) >= MIN_SYMBOL

#check if a password has already been used by the user
def newCheck(password, email):
    conn = db.get_db()
    cur = conn.cursor()
    userID = getID(email)
    cur.execute("SELECT PasswordHash FROM PasswordPairs WHERE UserID = (?)",
                (userID,))
    tup = cur.fetchall()
    db.close_db()
    #no previous passwords?
    if len(tup) == 0:
        return True
    #check all previous passwords against new one
    for storedHash in tup:
        if passHash.verify(password, storedHash[0]):
            return False
    return True
    
def sameCheck(password, confirmPassword):
    return password == confirmPassword

#add a new password to the database with the userID and assign it to them in
#the Registrants table.
def addPassword(password, email):
    conn = db.get_db()
    cur = conn.cursor()
    userID = getID(email)
    passwordHash = passHash.hash(password)
    cur.execute("INSERT INTO PasswordPairs (UserID, PasswordHash) VALUES (?, ?)",
                (userID, passwordHash))
    cur.execute("UPDATE Registrants SET PasswordHash = ? WHERE UserID = ?",
                (passwordHash, userID))
    db.close_db()
