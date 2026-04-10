import os
from flask import Blueprint, render_template, request, redirect, session
from werkzeug.utils import secure_filename
from utils.db import cursor, db

farmer_bp = Blueprint("farmer", __name__)


# ---------------- FARMER DASHBOARD ----------------
@farmer_bp.route("/farmer")
def farmer():
    if "user_id" not in session or session.get("role") != "farmer":
        return redirect("/login")

    farmer_id = session["user_id"]

    cursor.execute("SELECT * FROM users WHERE id=%s", (farmer_id,))
    user = cursor.fetchone()

    cursor.execute("SELECT * FROM crops WHERE farmer_id=%s", (farmer_id,))
    crops = cursor.fetchall()

    total_crops = len(crops)

    return render_template(
        "farmer.html",
        crops=crops,
        total_crops=total_crops,
        user=user
    )


# ---------------- ADD CROP ----------------
@farmer_bp.route("/add_crop", methods=["GET", "POST"])
def add_crop():
    if "user_id" not in session or session.get("role") != "farmer":
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
        video_path = ""

        image.save(image_path)

        if video_name != "":
            video_path = "static/uploads/" + video_name
            video.save(video_path)

        farmer_id = session["user_id"]

        cursor.execute(
            """
            INSERT INTO crops (farmer_id, crop_name, price_per_kg, quantity, image, video)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (farmer_id, crop_name, price, quantity, image_path, video_path)
        )
        db.commit()

        return redirect("/farmer")

    return render_template("add_crop.html")


# ---------------- MY CROPS ----------------
@farmer_bp.route("/my_crops")
def my_crops():
    if "user_id" not in session or session.get("role") != "farmer":
        return redirect("/login")

    farmer_id = session["user_id"]

    cursor.execute("SELECT * FROM crops WHERE farmer_id=%s", (farmer_id,))
    crops = cursor.fetchall()

    return render_template("my_crops.html", crops=crops)


# ---------------- EDIT CROP ----------------
@farmer_bp.route("/edit_crop/<int:crop_id>", methods=["GET", "POST"])
def edit_crop(crop_id):
    if "user_id" not in session or session.get("role") != "farmer":
        return redirect("/login")

    if request.method == "POST":
        crop_name = request.form["crop_name"]
        price = request.form["price"]
        quantity = request.form["quantity"]

        cursor.execute(
            """
            UPDATE crops
            SET crop_name=%s, price_per_kg=%s, quantity=%s
            WHERE id=%s
            """,
            (crop_name, price, quantity, crop_id)
        )
        db.commit()

        return redirect("/my_crops")

    cursor.execute("SELECT * FROM crops WHERE id=%s", (crop_id,))
    crop = cursor.fetchone()

    return render_template("edit_crop.html", crop=crop)


# ---------------- DELETE CROP ----------------
@farmer_bp.route("/delete_crop/<int:crop_id>")
def delete_crop(crop_id):
    if "user_id" not in session or session.get("role") != "farmer":
        return redirect("/login")

    cursor.execute("DELETE FROM crops WHERE id=%s", (crop_id,))
    db.commit()

    return redirect("/my_crops")


# ---------------- PROFILE ----------------
@farmer_bp.route("/profile", methods=["GET", "POST"])
def profile():
    if "user_id" not in session:
        return redirect("/login")

    uid = session["user_id"]

    if request.method == "POST":
        name = request.form["name"]
        address = request.form["address"]
        photo = request.files["photo"]

        if photo and photo.filename != "":
            filename = secure_filename(photo.filename)
            photo_path = "static/uploads/" + filename
            photo.save(photo_path)

            cursor.execute(
                "UPDATE users SET name=%s, address=%s, photo=%s WHERE id=%s",
                (name, address, photo_path, uid)
            )
        else:
            cursor.execute(
                "UPDATE users SET name=%s, address=%s WHERE id=%s",
                (name, address, uid)
            )

        db.commit()
        return redirect("/farmer")

    cursor.execute("SELECT * FROM users WHERE id=%s", (uid,))
    user = cursor.fetchone()

    return render_template("profile.html", user=user)