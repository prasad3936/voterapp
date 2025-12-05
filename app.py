from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mail import Mail, Message
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Change this in production

# ----------------------------
# Flask-Mail configuration
# ----------------------------
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USER', 'yourgmail@gmail.com')  # your Gmail
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASS', 'your-app-password')    # app password (not Gmail password)
app.config['MAIL_DEFAULT_SENDER'] = ('Mission ZP Enquiry', app.config['MAIL_USERNAME'])

mail = Mail(app)

# ----------------------------
# Routes
# ----------------------------
@app.route('/')
def home():
    return render_template('index.html')
@app.route('/success')
def success():
    return render_template('success.html')


@app.route('/help')
def slides():
    total_slides = 11
    return render_template("help.html", total=total_slides)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
