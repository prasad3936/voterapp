from flask import Flask, render_template, request, redirect, url_for, session, flash
import pymysql, math, urllib.parse

app = Flask(__name__)
app.secret_key = "verysecretkey_local"

# ---------------- DB CONNECTION ----------------
def get_db():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="root",
        database="voterdb",
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )

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

    query = "FROM voters WHERE 1=1"
    params = []

    # Search box
    if q:
        query += " AND (name LIKE %s OR serial LIKE %s OR epic LIKE %s OR relation LIKE %s OR house LIKE %s)"
        like = f"%{q}%"
        params += [like, like, like, like, like]

    # Gender Filter
    if gender:
        query += " AND gender=%s"
        params.append(gender)

    conn = get_db()
    cur = conn.cursor()

    # Total count for pagination
    cur.execute("SELECT COUNT(*) " + query, params)
    total = cur.fetchone()["COUNT(*)"]
    total_pages = math.ceil(total / per_page)

    # Fetch page data
    sql = f"SELECT * {query} ORDER BY serial*1 ASC LIMIT %s OFFSET %s"
    cur.execute(sql, params + [per_page, offset])
    voters = cur.fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        voters=voters,
        q=q,
        gender=gender,
        page=page,
        total_pages=total_pages
    )


# ---------------- VOTER DETAIL ----------------
@app.route("/voter/<int:vid>")
def voter_detail(vid):
    if "user" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM voters WHERE id=%s", (vid,))
    v = cur.fetchone()
    conn.close()

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

# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(debug=True)
