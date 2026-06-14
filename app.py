from flask import Flask
from routes.auth import auth_bp
from routes.farmer import farmer_bp
from routes.user import user_bp
from routes.admin import admin_bp
from routes.common import common_bp

app = Flask(__name__)
app.secret_key = "apnakhet_secret"

app.register_blueprint(auth_bp)
app.register_blueprint(farmer_bp)
app.register_blueprint(user_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(common_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)