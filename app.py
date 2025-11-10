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

@app.route('/send', methods=['POST'])
def send_enquiry():
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    message = request.form.get('message')

    if not (name and email and phone and message):
        flash("⚠️ Please fill all the fields before submitting.")
        return redirect(url_for('home'))

    try:
        msg = Message(
            subject=f"New Enquiry from {name}",
            recipients=["zpglobalsystems@gmail.com"]
        )
        msg.body = f"""
        📩 New Enquiry Received

        Name: {name}
        Email: {email}
        Phone: {phone}

        Message:
        {message}
        """
        mail.send(msg)
        flash("✅ Your enquiry has been sent successfully!")
    except Exception as e:
        print("Error:", e)
        flash("❌ Sorry, there was a problem sending your enquiry. Try again later.")
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
