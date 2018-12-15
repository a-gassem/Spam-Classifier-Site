import sqlite3 as sql

conn = sql.connect("..\\app.db")
c = conn.cursor()
c.execute("SELECT * FROM Registrants;")
print("Registrants:")
lst = c.fetchall()
print(lst)
print(len(lst))
c.execute("SELECT * FROM Codes;")
print("Codes:")
lst = c.fetchall()
print(lst)
if lst[0][1] == lst[1][1]:
    print("IDs are equal")
else:
    print("IDs are different")
conn.commit()
conn.close()

##from passlib.hash import pbkdf2_sha512 as passHash
##
##myHash = passHash.hash("test")
##tup = ("12345", "test", myHash)
##
##conn = sql.connect("..\\app.db")
##c = conn.cursor()
##c.execute("INSERT INTO Registrants(UserID, Email, PasswordHash) VALUES(?, ?, ?)", tup)
##c.execute("SELECT * FROM Registrants;")
##print(c.fetchone())
##conn.commit()
##conn.close()
