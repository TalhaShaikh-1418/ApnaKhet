import smtplib
from email.message import EmailMessage
from flask import Blueprint, render_template, request

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
        msg["From"] = email
        msg["To"] = "talhashaikh3408@gmail.com"

        msg.set_content(f"""
New Message from ApnaKhet Contact Form

Name: {name}
Email: {email}
Mobile: {mobile}

Message:
{message}
""")

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login("talhashaikh3408@gmail.com", "ljiwkhqqjscqtirl")
        server.send_message(msg)
        server.quit()

        return "Message sent successfully! We'll contact you soon."

    return render_template("contact.html")