from flask import Blueprint, render_template, request, redirect, session
from utils.db import cursor

user_bp = Blueprint("user", __name__)


# ---------------- USER DASHBOARD ----------------
@user_bp.route("/user")
def user():
    if "user_id" not in session or session.get("role") != "user":
        return redirect("/login")

    cursor.execute("SELECT COUNT(*) FROM users WHERE role='farmer'")
    total_farmers = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users WHERE role='user'")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM crops")
    total_crops = cursor.fetchone()[0]

    cursor.execute("SELECT * FROM crops ORDER BY id DESC LIMIT 4")
    recent_crops = cursor.fetchall()

    return render_template(
        "user.html",
        total_farmers=total_farmers,
        total_users=total_users,
        total_crops=total_crops,
        recent_crops=recent_crops
    )


# ---------------- VIEW CROPS ----------------
@user_bp.route("/view_crops")
def view_crops():
    if "user_id" not in session or session.get("role") != "user":
        return redirect("/login")

    keyword = request.args.get("search")

    if keyword:
        cursor.execute(
            """
            SELECT crops.*, users.name, users.mobile
            FROM crops
            JOIN users ON crops.farmer_id = users.id
            WHERE crops.crop_name LIKE %s
            """,
            ('%' + keyword + '%',)
        )
    else:
        cursor.execute(
            """
            SELECT crops.*, users.name, users.mobile
            FROM crops
            JOIN users ON crops.farmer_id = users.id
            """
        )

    crops = cursor.fetchall()
    return render_template("view_crops.html", crops=crops)


# ---------------- CONTACT FARMERS ----------------
@user_bp.route("/contact_farmers")
def contact_farmers():
    if "user_id" not in session or session.get("role") != "user":
        return redirect("/login")

    cursor.execute(
        """
        SELECT DISTINCT users.name, users.mobile, users.address
        FROM users
        JOIN crops ON users.id = crops.farmer_id
        """
    )

    farmers = cursor.fetchall()
    return render_template("contact_farmers.html", farmers=farmers)