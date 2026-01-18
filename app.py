
from flask import Flask, render_template, request, redirect, session
import mysql.connector
import random


import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

import smtplib
from email.message import EmailMessage





app = Flask(__name__)
app.secret_key = "apnakhet_secret"

# MySQL connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1418",   # yaha apna MySQL password daal
    database="apnakhet_db"
)
cursor = db.cursor()

# ---------------- HOME ----------------
@app.route("/")
def home():
    return redirect("/login")

# ---------------- SIGNUP ----------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        mobile = request.form["mobile"]
        password = request.form["password"]
        role = request.form["role"]

        otp = random.randint(100000, 999999)

        session["otp"] = otp
        session["temp_user"] = {
            "name": name,
            "mobile": mobile,
            "password": password,
            "role": role
        }

        print("OTP:", otp)   # OTP terminal pe dikhega
        return redirect("/verify_otp")

    return render_template("signup.html")

# ---------------- OTP Verification Route ----------------
@app.route("/verify_otp", methods=["GET", "POST"])
def verify_otp():
    if request.method == "POST":
        entered_otp = request.form["otp"]

        if int(entered_otp) == session.get("otp"):
            user = session.get("temp_user")

            cursor.execute("""
                INSERT INTO users (name, mobile, password, role)
                VALUES (%s, %s, %s, %s)
            """, (user["name"], user["mobile"], user["password"], user["role"]))
            db.commit()

            session.pop("otp")
            session.pop("temp_user")

            return redirect("/login")
        else:
            return "Invalid OTP"

    return render_template("verify_otp.html")



# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        mobile = request.form["mobile"]
        password = request.form["password"]

        query = """
        SELECT * FROM users 
        WHERE mobile=%s AND password=%s
        """
        cursor.execute(query, (mobile, password))
        user = cursor.fetchone()

        if user:
            session["user_id"] = user[0]
            session["role"] = user[4]

            if user[4] == "admin":
                return redirect("/admin")
            elif user[4] == "farmer":
                return redirect("/farmer")
            else:
                return redirect("/user")
        else:
            return "Invalid mobile or password"

    return render_template("login.html")

# ---------------- ADD CROPS ----------------
@app.route("/add_crop", methods=["GET", "POST"])
def add_crop():
    if "user_id" not in session or session["role"] != "farmer":
        return redirect("/login")

    upload_folder = "static/uploads"
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)


    if request.method == "POST":
        crop_name = request.form["crop_name"]
        price = request.form["price"]
        quantity = request.form["quantity"]

        image = request.files["image"]
        video = request.files["video"]

        image_name = secure_filename(image.filename)
        video_name = secure_filename(video.filename)

        image_path = "static/uploads/" + image_name
        video_path = "static/uploads/" + video_name

        image.save(image_path)
        if video_name != "":
            video.save(video_path)

        farmer_id = session["user_id"]

        query = """
        INSERT INTO crops (farmer_id, crop_name, price_per_kg, quantity, image, video)
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        cursor.execute(query, (farmer_id, crop_name, price, quantity, image_path, video_path))
        db.commit()

        return redirect("/farmer")

    return render_template("add_crop.html")

# ---------------- FARMER DASHBOARD ----------------
@app.route("/farmer")
def farmer():
    if "user_id" not in session or session["role"] != "farmer":
        return redirect("/login")

    farmer_id = session["user_id"]

    # farmer profile data
    cursor.execute("SELECT * FROM users WHERE id=%s", (farmer_id,))
    user = cursor.fetchone()

    # farmer crops data
    cursor.execute("SELECT * FROM crops WHERE farmer_id=%s", (farmer_id,))
    crops = cursor.fetchall()

    total_crops = len(crops)

    return render_template("farmer.html",
                           crops=crops,
                           total_crops=total_crops,
                           user=user)


@app.route("/user")
def user():
    if "user_id" not in session or session["role"] != "user":
        return redirect("/login")

    # Live Stats
    cursor.execute("SELECT COUNT(*) FROM users WHERE role='farmer'")
    total_farmers = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users WHERE role='user'")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM crops")
    total_crops = cursor.fetchone()[0]

    # Recent Crops
    cursor.execute("SELECT * FROM crops ORDER BY id DESC LIMIT 4")
    recent_crops = cursor.fetchall()

    return render_template(
        "user.html",
        total_farmers=total_farmers,
        total_users=total_users,
        total_crops=total_crops,
        recent_crops=recent_crops
    )



# ---------------- VIEW CROPS (BUYER) ----------------
@app.route("/view_crops", methods=["GET"])
def view_crops():
    if "user_id" not in session or session["role"] != "user":
        return redirect("/login")

    keyword = request.args.get("search")

    if keyword:
        cursor.execute("""
            SELECT crops.*, users.name, users.mobile
            FROM crops
            JOIN users ON crops.farmer_id = users.id
            WHERE crops.crop_name LIKE %s
        """, ('%' + keyword + '%',))
    else:
        cursor.execute("""
            SELECT crops.*, users.name, users.mobile
            FROM crops
            JOIN users ON crops.farmer_id = users.id
        """)

    crops = cursor.fetchall()
    return render_template("view_crops.html", crops=crops)

# ---------------- MY CROPS (FARMER) ----------------
@app.route("/my_crops")
def my_crops():
    if "user_id" not in session or session["role"] != "farmer":
        return redirect("/login")

    farmer_id = session["user_id"]

    cursor.execute("SELECT * FROM crops WHERE farmer_id=%s", (farmer_id,))
    crops = cursor.fetchall()

    return render_template("my_crops.html", crops=crops)

# ---------------- EDIT CROP ----------------
@app.route("/edit_crop/<int:crop_id>", methods=["GET", "POST"])
def edit_crop(crop_id):
    if "user_id" not in session or session["role"] != "farmer":
        return redirect("/login")

    if request.method == "POST":
        crop_name = request.form["crop_name"]
        price = request.form["price"]
        quantity = request.form["quantity"]

        cursor.execute("""
            UPDATE crops 
            SET crop_name=%s, price_per_kg=%s, quantity=%s 
            WHERE id=%s
        """, (crop_name, price, quantity, crop_id))
        db.commit()

        return redirect("/my_crops")

    cursor.execute("SELECT * FROM crops WHERE id=%s", (crop_id,))
    crop = cursor.fetchone()

    return render_template("edit_crop.html", crop=crop)

# ---------------- DELETE CROP ----------------
@app.route("/delete_crop/<int:crop_id>")
def delete_crop(crop_id):
    if "user_id" not in session or session["role"] != "farmer":
        return redirect("/login")

    cursor.execute("DELETE FROM crops WHERE id=%s", (crop_id,))
    db.commit()

    return redirect("/my_crops")

# ---------------- PROFILE FOR FARMER ----------------
@app.route("/profile", methods=["GET","POST"])
def profile():
    if "user_id" not in session:
        return redirect("/login")

    uid = session["user_id"]

    if request.method == "POST":
        name = request.form["name"]
        address = request.form["address"]
        photo = request.files["photo"]

        photo_path = None
        if photo.filename != "":
            filename = secure_filename(photo.filename)
            photo_path = "static/uploads/" + filename
            photo.save(photo_path)

            cursor.execute("UPDATE users SET name=%s, address=%s, photo=%s WHERE id=%s",
                           (name, address, photo_path, uid))
        else:
            cursor.execute("UPDATE users SET name=%s, address=%s WHERE id=%s",
                           (name, address, uid))

        db.commit()
        return redirect("/farmer")

    cursor.execute("SELECT * FROM users WHERE id=%s", (uid,))
    user = cursor.fetchone()

    return render_template("profile.html", user=user)

# ---------------- CONTACT FARMERS ----------------


@app.route("/contact_farmers")
def contact_farmers():
    if "user_id" not in session or session["role"] != "user":
        return redirect("/login")

    cursor.execute("""
        SELECT DISTINCT users.name, users.mobile, users.address
        FROM users
        JOIN crops ON users.id = crops.farmer_id
    """)
    farmers = cursor.fetchall()

    return render_template("contact_farmers.html", farmers=farmers)

# ---------------- TRUSTED MARKET ----------------
@app.route("/trusted_market")
def trusted_market():
    return render_template("trusted_market.html")

# ---------------- Create Admin Dashboard Route ----------------
@app.route("/admin")
def admin():
    if "user_id" not in session or session["role"] != "admin":
        return redirect("/login")

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM crops")
    total_crops = cursor.fetchone()[0]

    return render_template("admin.html", total_users=total_users, total_crops=total_crops)

# ---------------- MANAGE USERS ----------------
@app.route("/manage_users")
def manage_users():
    if "user_id" not in session or session["role"] != "admin":
        return redirect("/login")

    cursor.execute("SELECT id, name, mobile, role FROM users")
    users = cursor.fetchall()

    return render_template("manage_users.html", users=users)

# -------- DELETE USER --------
@app.route("/delete_user/<int:user_id>")
def delete_user(user_id):
    if "user_id" not in session or session["role"] != "admin":
        return redirect("/login")

    cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))
    db.commit()
    return redirect("/manage_users")


# -------- SEARCH USERS --------
@app.route("/manage_users_search")
def manage_users_search():
    if "user_id" not in session or session["role"] != "admin":
        return redirect("/login")

    keyword = request.args.get("search")

    if keyword:
        cursor.execute("""
            SELECT id, name, mobile, role
            FROM users
            WHERE name LIKE %s OR mobile LIKE %s
        """, ('%' + keyword + '%', '%' + keyword + '%'))
    else:
        cursor.execute("SELECT id, name, mobile, role FROM users")

    users = cursor.fetchall()
    return render_template("manage_users.html", users=users)

# ---------------- ADMIN: MANAGE CROPS ----------------
@app.route("/manage_crops")
def manage_crops():
    if "user_id" not in session or session["role"] != "admin":
        return redirect("/login")

    cursor.execute("""
        SELECT crops.*, users.name
        FROM crops
        JOIN users ON crops.farmer_id = users.id
    """)
    crops = cursor.fetchall()

    return render_template("manage_crops.html", crops=crops)


# -------- DELETE CROP --------
@app.route("/admin_delete_crop/<int:crop_id>")
def admin_delete_crop(crop_id):
    if "user_id" not in session or session["role"] != "admin":
        return redirect("/login")

    cursor.execute("DELETE FROM crops WHERE id=%s", (crop_id,))
    db.commit()
    return redirect("/manage_crops")


# -------- CONTACT ME  --------
@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        mobile = request.form["mobile"]
        message = request.form["message"]

# -------- Email contact --------
        msg = EmailMessage()
        msg["Subject"] = "New Contact Message - ApnaKhet"
        msg["From"] = email
        msg["To"] = "talhashaikh3408@gmail.com"   # <-- APNA GMAIL DAAL

        msg.set_content(f"""
        New Message from ApnaKhet Contact Form

        Name: {name}
        Email: {email}
        Mobile: {mobile}

        Message:
        {message}
        """)

# -------- Send email via Gmail  --------
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login("talhashaikh3408@gmail.com", "ljiwkhqqjscqtirl")
        server.send_message(msg)
        server.quit()

        return "Message sent successfully! We'll contact you soon."

    return render_template("contact.html")



# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")



# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)

