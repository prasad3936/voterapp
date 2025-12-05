from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mail import Mail, Message
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Change this in production


# ----------------------------
# Routes
# ----------------------------
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/help')
def slides():
    total_slides = 11
    return render_template("help.html", total=total_slides)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
