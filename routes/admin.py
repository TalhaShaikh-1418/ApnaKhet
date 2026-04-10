from flask import Blueprint, render_template, request, redirect, session
from utils.db import cursor, db

admin_bp = Blueprint("admin", __name__)


# ---------------- ADMIN DASHBOARD ----------------
@admin_bp.route("/admin")
def admin():
    if "user_id" not in session or session.get("role") != "admin":
        return redirect("/login")

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM crops")
    total_crops = cursor.fetchone()[0]

    return render_template("admin.html", total_users=total_users, total_crops=total_crops)


# ---------------- MANAGE USERS ----------------
@admin_bp.route("/manage_users")
def manage_users():
    if "user_id" not in session or session.get("role") != "admin":
        return redirect("/login")

    cursor.execute("SELECT id, name, mobile, role FROM users")
    users = cursor.fetchall()

    return render_template("manage_users.html", users=users)


# ---------------- SEARCH USERS ----------------
@admin_bp.route("/manage_users_search")
def manage_users_search():
    if "user_id" not in session or session.get("role") != "admin":
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


# ---------------- DELETE USER ----------------
@admin_bp.route("/delete_user/<int:user_id>")
def delete_user(user_id):
    if "user_id" not in session or session.get("role") != "admin":
        return redirect("/login")

    cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))
    db.commit()

    return redirect("/manage_users")


# ---------------- MANAGE CROPS ----------------
@admin_bp.route("/manage_crops")
def manage_crops():
    if "user_id" not in session or session.get("role") != "admin":
        return redirect("/login")

    cursor.execute("""
        SELECT crops.*, users.name
        FROM crops
        JOIN users ON crops.farmer_id = users.id
    """)

    crops = cursor.fetchall()

    return render_template("manage_crops.html", crops=crops)


# ---------------- DELETE CROP ----------------
@admin_bp.route("/admin_delete_crop/<int:crop_id>")
def admin_delete_crop(crop_id):
    if "user_id" not in session or session.get("role") != "admin":
        return redirect("/login")

    cursor.execute("DELETE FROM crops WHERE id=%s", (crop_id,))
    db.commit()

    return redirect("/manage_crops")