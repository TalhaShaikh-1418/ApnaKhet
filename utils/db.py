import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

db = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)

cursor = db.cursor()

# Create users table if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    mobile VARCHAR(15),
    password VARCHAR(255),
    role ENUM('admin','farmer','user'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# Create crops table if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS crops (
    id INT AUTO_INCREMENT PRIMARY KEY,
    farmer_id INT,
    crop_name VARCHAR(100),
    price_per_kg INT,
    quantity INT,
    image VARCHAR(200),
    video VARCHAR(200)
)
""")

# Create admin user if not exists
cursor.execute("SELECT * FROM users WHERE mobile=%s", ("9822481115",))
admin = cursor.fetchone()

if not admin:
    cursor.execute("""
    INSERT INTO users (name, mobile, password, role)
    VALUES (%s, %s, %s, %s)
    """, ("Admin", "9822481115", "admin@123", "admin"))
    db.commit()

db.commit()