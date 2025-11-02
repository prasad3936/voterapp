import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, g
import mysql
import pymysql, math, urllib.parse
from urllib.parse import urlparse, unquote

app = Flask(__name__)
app.secret_key = "verysecretkey_local"

DB_URL = "mysql://USER:PASSWORD@mysql-1f761a7d-prasadcpatil246-f8f0.b.aivencloud.com:14627/voterdb"  # mysql://user:pass@host:port/dbname

if not DB_URL:
    raise Exception("❌ DATABASE_URL environment variable not set!")

# ---- Parse DB URI ----
url = urlparse(DB_URL)

DB_CONFIG = {
    "host": url.hostname,
    "port": url.port,
    "user": url.username,
    "password": url.password,
    "database": url.path.lstrip('/'),
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
    "ssl": {
        "ca": os.path.join(os.path.dirname(__file__), "ca.pem")
    }
}

def get_db():
    """ Reuse connection across Lambda invocations """
    if "db" not in g:
        g.db = pymysql.connect(**DB_CONFIG, connect_timeout=8)
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop("db", None)
    if db:
        db.close()


# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form.get("username")
        p = request.form.get("password")
        if u == "admin" and p == "admin":
            session["user"] = "admin"
            return redirect(url_for("dashboard"))
        flash("❌ चुकीचे Username/Password", "danger")

    return render_template("login.html")

# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    q = request.args.get("q", "").strip()
    gender = request.args.get("gender", "")
    page = int(request.args.get("page", 1))

    per_page = 20
    offset = (page - 1) * per_page

    query = "FROM voters WHERE name IS NOT NULL AND name != ''"
    params = []

    if q:
        query += " AND (name LIKE %s OR serial LIKE %s OR epic LIKE %s OR relation LIKE %s OR house LIKE %s)"
        like = f"%{q}%"
        params += [like] * 5

    if gender:
        query += " AND gender=%s"
        params.append(gender)

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) " + query, params)
    total = cur.fetchone()["COUNT(*)"]
    total_pages = math.ceil(total / per_page)

    sql = f"SELECT * {query} ORDER BY serial*1 ASC LIMIT %s OFFSET %s"
    cur.execute(sql, params + [per_page, offset])
    voters = cur.fetchall()

    return render_template("dashboard.html", voters=voters, q=q, gender=gender, page=page, total_pages=total_pages)

# ---------------- VOTER DETAIL ----------------
@app.route("/voter/<int:vid>")
def voter_detail(vid):
    if "user" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM voters WHERE id=%s", (vid,))
    v = cur.fetchone()

    if not v:
        return "❌ Voter Not Found", 404

    text = f"मतदार माहिती:\nनाव: {v['name']}\nEPIC: {v['epic']}\nक्रमांक: {v['serial']}"
    wa_url = "https://wa.me/?text=" + urllib.parse.quote(text)

    return render_template("card.html", v=v, wa_url=wa_url)

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)