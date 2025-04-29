import mysql.connector

mydb = mysql.connector.connect(
      host="homelander.cjysa866ww26.us-east-2.rds.amazonaws.com",
      user="admin",
      password="Mustard99!",
      database="Health" 
    )
mycursor = mydb.cursor()

# Example: Select data


mycursor.execute("""INSERT INTO rls VALUES 
(2, '2025-04-01',70, 0, 1, 400, .5, 'walked', 'frog', 2, 9, 'minimal')""")

mycursor.execute("SELECT * FROM rls")
myresult = mycursor.fetchall()
for x in myresult:
    print(x)