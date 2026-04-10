from flask import Blueprint, render_template, request, redirect, session
from utils.db import cursor, db
import random

# Blueprint create
auth_bp = Blueprint("auth", __name__)


# ---------------- HOME ----------------
@auth_bp.route("/")
def home():
    return redirect("/login")


# ---------------- SIGNUP ----------------
@auth_bp.route("/signup", methods=["GET", "POST"])
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

        print("OTP:", otp)  # OTP terminal me dikhega
        return redirect("/verify_otp")

    return render_template("signup.html")


# ---------------- OTP VERIFY ----------------
@auth_bp.route("/verify_otp", methods=["GET", "POST"])
def verify_otp():
    if request.method == "POST":
        entered_otp = request.form["otp"]

        if int(entered_otp) == session.get("otp"):
            user = session.get("temp_user")

            cursor.execute(
                """
                INSERT INTO users (name, mobile, password, role)
                VALUES (%s, %s, %s, %s)
                """,
                (user["name"], user["mobile"], user["password"], user["role"])
            )
            db.commit()

            session.pop("otp", None)
            session.pop("temp_user", None)

            return redirect("/login")
        else:
            return "Invalid OTP"

    return render_template("verify_otp.html")


# ---------------- LOGIN ----------------
@auth_bp.route("/login", methods=["GET", "POST"])
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


# ---------------- LOGOUT ----------------
@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/login")
