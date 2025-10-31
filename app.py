from flask import Flask, render_template, request, redirect, url_for, session, send_file, flash
import sqlite3, math, io, os, urllib.parse
import imgkit
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from PIL import Image, ImageDraw, ImageFont

import time



app = Flask(__name__)
app.secret_key = "verysecretkey_local"
DB = "voters.db"

# DB Connection
def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

# ------------------- LOGIN -------------------
@app.route("/", methods=["GET","POST"])
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        u = request.form.get("username")
        p = request.form.get("password")
        if u == "admin" and p == "admin":
            session["user"] = "admin"
            return redirect(url_for("dashboard"))
        flash("चुकीचे क्रेडेन्शियल्स — Username/Password तपासा", "danger")
    return render_template("login.html")

# ------------------- DASHBOARD LIST -------------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    q = request.args.get("q", "").strip()
    gender = request.args.get("gender", "")
    caste = request.args.get("caste", "")
    page = int(request.args.get("page", 1))
    per_page = 10
    offset = (page - 1) * per_page

    base = " FROM voters WHERE 1=1"
    params = []
    cond = ""

    if q:
        cond += " AND (name LIKE ? OR voter_serial LIKE ? OR voter_id LIKE ? OR address LIKE ?)"
        like = f"%{q}%"
        params.extend([like, like, like, like])

    if gender:
        cond += " AND gender = ?"; params.append(gender)

    if caste:
        cond += " AND caste = ?"; params.append(caste)

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) " + base + cond, params)
    total = cur.fetchone()[0]
    total_pages = math.ceil(total / per_page)

    sql = "SELECT * " + base + cond + " ORDER BY id ASC LIMIT ? OFFSET ?"
    cur.execute(sql, params + [per_page, offset])
    voters = cur.fetchall()

    conn.close()

    return render_template("dashboard.html",
        voters=voters, q=q, gender=gender, caste=caste,
        page=page, total_pages=total_pages
    )

# ------------------- VOTER DETAIL CARD -------------------
@app.route("/voter/<int:vid>")
def voter_detail(vid):
    if "user" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM voters WHERE id=?", (vid,))
    v = cur.fetchone()
    conn.close()

    if not v:
        return "Voter not found",404

    # WhatsApp message text
    text = f"मतदार माहिती:\nनाव: {v['name']}\nID: {v['voter_id']}\nक्रमांक: {v['voter_serial']}"
    wa_url = "https://wa.me/?text=" + urllib.parse.quote(text)

    return render_template("card.html", v=v, wa_url=wa_url)

    

# ------------------- LOGOUT -------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# -------------------
if __name__ == "__main__":
    app.run(debug=True)
