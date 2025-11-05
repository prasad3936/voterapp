from flask import Flask, render_template, request, redirect, url_for, session, flash
import json, math, urllib.parse, re

app = Flask(__name__)
app.secret_key = "verysecretkey_local"

# ✅ Toggle testing mode here
TEST_MODE = False   # False for production


# ---------------- LOAD JSON DATA ----------------
def load_voters():
    """Load and normalize Marathi voter JSON to a consistent structure."""
    with open("voters.json", "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    voters = []

    for item in raw_data:
        serial = safe_int(item.get("क्रमांक") or item.get("serial"))
        name = (
            item.get("मतदाराचे पूर्ण नाव")
            or item.get("मतदाराचे_पूर्ण_नाव")
            or item.get("name")
        )
        relation = (
            item.get("वडिलांचे नाव")
            or item.get("वडिलांचे_नाव")
            or item.get("relation")
        )

        # ✅ Updated house_number normalization
        house_number = (
            item.get("घर क्रमांक")
            or item.get("घर_क्रमांक")
            or item.get("house_number")
            or "NA"
        )
        house_number = normalize_house_number(house_number)

        age = item.get("वय") or item.get("age") or "NA"
        gender = item.get("लिंग") or item.get("gender") or "NA"

        epic = (
            item.get("पहचानपत्र क्रमांक")
            or item.get("पहचान_पत्र_क्रमांक")
            or item.get("मतदार_क्रमांक")
            or item.get("epic")
        )
        booth_ref = (
            item.get("भाग क्रमांक")
            or item.get("भाग_क्रमांक")
            or item.get("page_numbers")
            or "NA"
        )

        if not serial:
            serial = len(voters) + 1  # fallback if क्रमांक missing

        voters.append({
            "serial": serial,
            "name": name,
            "relation": relation,
            "house_number": house_number,
            "age": age,
            "gender": gender,
            "epic": epic,
            "booth_reference": booth_ref
        })

    # ✅ Remove records without essential info
    clean_voters = [v for v in voters if v.get("name") and v.get("epic")]
    return clean_voters


def normalize_house_number(value):
    """Cleans house_number and converts Marathi digits if needed."""
    if not value or str(value).strip().lower() in ("na", "none", "-", ""):
        return "NA"

    # Replace Marathi digits with English equivalents
    marathi_to_english = str.maketrans("०१२३४५६७८९", "0123456789")
    cleaned = str(value).strip().translate(marathi_to_english)
    return cleaned


def safe_int(x):
    """Safely convert strings like '2,594' or '३,१४३' to int."""
    if not x:
        return None
    try:
        # Remove commas or Marathi digits
        marathi_to_english = str.maketrans("०१२३४५६७८९", "0123456789")
        x = str(x).translate(marathi_to_english)
        x = re.sub(r"[^\d]", "", x)
        return int(x)
    except Exception:
        return None


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
    if auth:
        return auth

    q = request.args.get("q", "").strip().lower()
    gender = request.args.get("gender", "")
    page = int(request.args.get("page", 1))
    per_page = 20

    voters = load_voters()
    total_voters_all = len(voters)

    results = []
    for v in voters:
        match = True

        # 🔍 Search in any field
        if q:
            match = any(q in str(val).lower() for val in v.values() if val)

        # 🚻 Gender filter
        if gender and v.get("gender") != gender:
            match = False

        if match:
            results.append(v)

    # 📄 Pagination
    total_filtered = len(results)
    start = (page - 1) * per_page
    end = start + per_page
    page_data = results[start:end]
    total_pages = math.ceil(total_filtered / per_page)

    return render_template(
        "dashboard.html",
        voters=page_data,
        q=q,
        gender=gender,
        page=page,
        total_pages=total_pages,
        total_voters=total_voters_all
    )


# ---------------- VOTER DETAIL ----------------
@app.route("/voter/<int:serial>")
def voter_detail(serial):
    auth = require_login()
    if auth:
        return auth

    voters = load_voters()
    voter = next((v for v in voters if v["serial"] == serial), None)
    if not voter:
        return "❌ मतदार सापडला नाही", 404

    text = (
        f"मतदार माहिती:\n"
        f"नाव: {voter['name']}\n"
        f"EPIC: {voter['epic']}\n"
        f"क्रमांक: {voter['serial']}\n"
        f"भाग क्रमांक: {voter['booth_reference']}\n"
        f"घर क्रमांक: {voter['house_number']}\n"
        f"वय: {voter['age']}\n"
        f"लिंग: {voter['gender']}"
    )
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
