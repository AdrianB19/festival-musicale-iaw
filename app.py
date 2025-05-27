from flask import Flask, render_template, request, redirect, url_for

from flask_login import LoginManager, login_user, login_required, current_user

app = Flask(__name__)
app.config["SECRET_KEY"] = "secretpass"

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login")
def login():
    return render_template("login.html")