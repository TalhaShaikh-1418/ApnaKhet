import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1418",
    database="apnakhet_db"
)

cursor = db.cursor()