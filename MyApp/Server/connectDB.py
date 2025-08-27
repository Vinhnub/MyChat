import pyodbc

#print(pyodbc.drivers()) 

conx = pyodbc.connect(
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=LAPTOP-SUM9877U;"
    "DATABASE=SOCKET;"
    "UID=huyq;"
    "PWD=1234;"
    "Encrypt=yes;"
    "TrustServerCertificate=yes;")

cursor = conx.cursor()

for row in cursor.execute("select * from useraccount where username = 'huyquoc1'"):
    print(row.username)
    print(row[0])
    print(row)

cursor.execute("select * from useraccount ")

data = cursor.fetchall()

print(data)
print(data[1][0])

#username = 'abc'
#pswd = '123'
#cursor.execute("insert useraccount values (?, ?)", username, pswd)
#conx.commit()

conx.close()