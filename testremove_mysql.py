import mysql

from learn_mysql.testquery_mysql import server, port, database, username, password

#Xóa Student có ID=14:
conn = mysql.connector.connect(
                host=server,
                port=port,
                database=database,
                user=username,
                password=password)
cursor = conn.cursor()
sql="DELETE from student where ID=14"
cursor.execute(sql)

conn.commit()

print(cursor.rowcount," record(s) affected")

#Xóa Student có ID=13 với SQL Injection:
conn = mysql.connector.connect(
                host=server,
                port=port,
                database=database,
                user=username,
                password=password)
cursor = conn.cursor()
sql = "DELETE from student where ID=%s"
val = (13,)

cursor.execute(sql, val)

conn.commit()

print(cursor.rowcount," record(s) affected")