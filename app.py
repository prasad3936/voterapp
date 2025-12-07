from flask import Flask, render_template, request, redirect, url_for, session, flash
import json, math, urllib.parse, re, os
from uuid import uuid4
import qrcode
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "verysecretkey_local"

TEST_MODE = False

# ---------------------------------------------------
#  FILES & FOLDERS
# ---------------------------------------------------
EVM_FILE = "evm_sessions.json"
USER_FILE = "users.json"

os.makedirs("static/symbols", exist_ok=True)
os.makedirs("static/qr", exist_ok=True)


# ---------------------------------------------------
#  USER SYSTEM
# ---------------------------------------------------
def load_users():
    if not os.path.exists(USER_FILE):
        return []
    with open(USER_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_users(users):
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()

        if not username or not password:
            flash("❌ कृपया सर्व माहिती भरा", "danger")
            return redirect(url_for("register"))

        users = load_users()

        if any(u["username"] == username for u in users):
            flash("⚠️ Username आधीपासून वापरलेले आहे", "warning")
            return redirect(url_for("register"))

        hashed = generate_password_hash(password)
        users.append({"username": username, "password": hashed})
        save_users(users)

        flash("✅ User created successfully!", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if TEST_MODE:
        session["user"] = "admin"
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()

        users = load_users()
        user = next((u for u in users if u["username"] == username), None)

        if not user or not check_password_hash(user["password"], password):
            flash("❌ चुकीचे Username/Password", "danger")
            return redirect(url_for("login"))

        session["user"] = username
        flash("✅ Login successful!", "success")
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("👋 Logged out successfully!", "info")
    return redirect(url_for("login"))


def require_login():
    if TEST_MODE:
        session["user"] = "admin"
        return None
    if "user" not in session:
        flash("⚠️ कृपया लॉगिन करा", "warning")
        return redirect(url_for("login"))
    return None


# ---------------------------------------------------
#  LOAD & SAVE EVM SESSIONS
# ---------------------------------------------------
def load_evm():
    if not os.path.exists(EVM_FILE):
        return {}
    with open(EVM_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_evm(data):
    with open(EVM_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


EVM_SESSIONS = load_evm()


# ---------------------------------------------------
#  QR Generator
# ---------------------------------------------------
def generate_qr(session_id):
    url = f"http://{request.host}/evm/{session_id}"
    img = qrcode.make(url)
    path = f"static/qr/{session_id}.png"
    img.save(path)
    return "/" + path


# ---------------------------------------------------
#  LOAD VOTERS JSON
# ---------------------------------------------------
def load_voters():
    with open("voters.json", "r", encoding="utf-8") as f:
        raw = json.load(f)

    voters = []
    for item in raw:
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
            or item.get("मतदार_क्रमांक")
            or item.get("epic")
            or "NA"
        )

        booth_ref = (
            item.get("भाग क्रमांक")
            or item.get("भाग_क्रमांक")
            or item.get("page_numbers")
            or "NA"
        )

        if not serial:
            serial = len(voters) + 1

        voters.append({
            "serial": serial,
            "name": name or "NA",
            "relation": relation or "NA",
            "house_number": house_number,
            "age": age,
            "gender": gender,
            "epic": epic,
            "booth_reference": booth_ref
        })

    return voters


def normalize_house_number(value):
    if not value:
        return "NA"
    marathi_to_english = str.maketrans("०१२३४५६७८९", "0123456789")
    return str(value).translate(marathi_to_english)


def safe_int(x):
    if not x:
        return None
    try:
        x = str(x).translate(str.maketrans("०१२३४५६७८९", "0123456789"))
        x = re.sub(r"[^\d]", "", x)
        return int(x)
    except:
        return None


# ---------------------------------------------------
#  DASHBOARD
# ---------------------------------------------------
@app.route("/dashboard")
def dashboard():
    auth = require_login()
    if auth:
        return auth

    q = request.args.get("q", "").lower()
    page = int(request.args.get("page", 1))
    gender = request.args.get("gender", "")
    per_page = 20

    voters = load_voters()
    total_voters_all = len(voters)

    latest_session_id = list(EVM_SESSIONS.keys())[-1] if EVM_SESSIONS else None

    results = []
    for v in voters:
        match = True

        if q:
            match = any(q in str(val).lower() for val in v.values())

        if gender and gender.lower() not in str(v.get("gender", "")).lower():
            match = False

        if match:
            results.append(v)

    total_pages = math.ceil(len(results) / per_page)
    start = (page - 1) * per_page
    end = start + per_page

    return render_template(
        "dashboard.html",
        voters=results[start:end],
        q=q,
        gender=gender,
        page=page,
        total_pages=total_pages,
        total_voters=total_voters_all,
        latest_session_id=latest_session_id
    )


# ---------------------------------------------------
#  VOTER DETAIL PAGE
# ---------------------------------------------------
@app.route("/voter/<int:serial>")
def voter_detail(serial):
    auth = require_login()
    if auth:
        return auth

    voters = load_voters()
    voter = next((v for v in voters if v["serial"] == serial), None)
    if not voter:
        return "❌ मतदार सापडला नाही"

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

    return render_template("card.html", v=voter, wa_url=wa_url, hide_total=True)


# ---------------------------------------------------
#  CREATE / EDIT EVM
# ---------------------------------------------------
@app.route("/evm/create", methods=["GET", "POST"])
def evm_create():
    auth = require_login()
    if auth:
        return auth

    session_id = request.args.get("session_id")
    existing = EVM_SESSIONS.get(session_id) if session_id else None

    if request.method == "POST":
        candidates = []

        for i in range(1, 10 + 1):
            name = request.form.get(f"name_{i}", "").strip()
            file = request.files.get(f"symbol_{i}")

            if not name:
                continue

            symbol_path = ""

            if file and file.filename:
                filename = f"{uuid4().hex}_{file.filename}"
                save_path = os.path.join("static/symbols", filename)
                file.save(save_path)
                symbol_path = "/" + save_path.replace("\\", "/")

            else:
                if existing and i <= len(existing["candidates"]):
                    symbol_path = existing["candidates"][i-1]["symbol"]

            candidates.append({
                "id": i,
                "name": name,
                "symbol": symbol_path,
                "votes": 0
            })

        if session_id:
            EVM_SESSIONS[session_id]["candidates"] = candidates
        else:
            session_id = uuid4().hex[:8]
            EVM_SESSIONS[session_id] = {"candidates": candidates}

        save_evm(EVM_SESSIONS)

        flash("✅ EVM Updated Successfully!", "success")
        return redirect(url_for("evm_page", session_id=session_id))

    return render_template("evm_create.html", session_id=session_id, existing=existing)


# ---------------------------------------------------
#  VIEW EVM
# ---------------------------------------------------
@app.route("/evm/<session_id>")
def evm_page(session_id):
    if session_id not in EVM_SESSIONS:
        return "Invalid EVM ID"

    qr = generate_qr(session_id)

    return render_template(
        "evm_page.html",
        session_id=session_id,
        candidates=EVM_SESSIONS[session_id]["candidates"],
        qr=qr
    )


# ---------------------------------------------------
#  RECORD VOTE
# ---------------------------------------------------
@app.route("/evm/vote/<session_id>/<int:cid>", methods=["POST"])
def evm_vote(session_id, cid):
    if session_id not in EVM_SESSIONS:
        return "Invalid EVM session"

    for c in EVM_SESSIONS[session_id]["candidates"]:
        if c["id"] == cid:
            c["votes"] += 1
            break

    save_evm(EVM_SESSIONS)
    return "OK"


# ---------------------------------------------------
#  DELETE EVM
# ---------------------------------------------------
@app.route("/evm/delete/<session_id>")
def evm_delete(session_id):
    if session_id in EVM_SESSIONS:
        EVM_SESSIONS.pop(session_id)
        save_evm(EVM_SESSIONS)
        flash("🗑 EVM deleted successfully!", "danger")
    else:
        flash("❌ EVM not found!", "warning")

    return redirect(url_for("dashboard"))


# ---------------------------------------------------
#  RESET VOTES
# ---------------------------------------------------
@app.route("/evm/reset/<session_id>")
def evm_reset(session_id):
    if session_id not in EVM_SESSIONS:
        return "Invalid EVM ID"

    for c in EVM_SESSIONS[session_id]["candidates"]:
        c["votes"] = 0

    save_evm(EVM_SESSIONS)

    flash("🔄 All votes reset!", "warning")
    return redirect(url_for("evm_page", session_id=session_id))


@app.route('/help')
def slides():
    total_slides = 11
    return render_template("help.html", total=total_slides)


# ---------------------------------------------------
#  SERVER START
# ---------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
