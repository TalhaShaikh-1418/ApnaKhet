import smtplib
import os
from email.message import EmailMessage
from flask import Blueprint, render_template, request
from dotenv import load_dotenv

load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

common_bp = Blueprint("common", __name__)


@common_bp.route("/trusted_market")
def trusted_market():
    return render_template("trusted_market.html")


@common_bp.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        mobile = request.form["mobile"]
        message = request.form["message"]

        msg = EmailMessage()
        msg["Subject"] = "New Contact Message - ApnaKhet"
        msg["From"] = EMAIL_USER
        msg["To"] = EMAIL_USER

        msg.set_content(f"""
New Message from ApnaKhet Contact Form

Name: {name}
Email: {email}
Mobile: {mobile}

Message:
{message}
""")

        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)
            server.quit()

            return "Message sent successfully! We'll contact you soon."

        except Exception as e:
            return f"Error sending message: {e}"

    return render_template("contact.html")