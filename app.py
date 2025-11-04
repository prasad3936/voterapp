from flask import Flask, render_template, request, redirect, url_for, session, flash
import json, math, urllib.parse

app = Flask(__name__)
app.secret_key = "verysecretkey_local"

# ✅ Toggle testing mode here
TEST_MODE = False   # False for production

# ---------------- LOAD JSON DATA ----------------
def load_voters():
    with open("voters.json", "r", encoding="utf-8") as f:
        return json.load(f)

# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if TEST_MODE:
        session["user"] = "admin"
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        u = request.form.get("username")
        p = request.form.get("password")
        if u == "admin" and p == "admin":
            session["user"] = "admin"
            return redirect(url_for("dashboard"))
        flash("❌ चुकीचे Username/Password", "danger")
    return render_template("login.html")

# ---------------- LOGIN CHECK ----------------
def require_login():
    if TEST_MODE:
        session["user"] = "admin"
        return None
    if "user" not in session:
        return redirect(url_for("login"))
    return None

# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    auth = require_login()
    if auth: return auth

    q = request.args.get("q", "").strip().lower()
    gender = request.args.get("gender", "")
    page = int(request.args.get("page", 1))

    per_page = 20
    voters = load_voters()

    results = []
    for v in voters:
        if v.get("name"):
            match = True

            # Search text
            if q:
                match = False
                for key, val in v.items():
                    if val and q in str(val).lower():
                        match = True
                        break

            # Gender filter
            if gender and v.get("gender") != gender:
                match = False

            if match:
                results.append(v)

    # Pagination
    total = len(results)
    start = (page - 1) * per_page
    end = start + per_page
    page_data = results[start:end]
    total_pages = math.ceil(total / per_page)

    return render_template(
        "dashboard.html",
        voters=page_data,
        q=q,
        gender=gender,
        page=page,
        total_pages=total_pages
    )

# ---------------- VOTER DETAIL ----------------
@app.route("/voter/<int:serial>")
def voter_detail(serial):
    auth = require_login()
    if auth: return auth

    voters = load_voters()
    voter = next((v for v in voters if v["serial"] == serial), None)
    if not voter:
        return "❌ Voter Not Found", 404

    text = f"मतदार माहिती:\nनाव: {voter['name']}\nEPIC: {voter['epic']}\nक्रमांक: {voter['serial']}"
    wa_url = "https://wa.me/?text=" + urllib.parse.quote(text)

    return render_template("card.html", v=voter, wa_url=wa_url)

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
