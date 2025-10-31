# init_db.py
import sqlite3, os

os.makedirs("static/photos", exist_ok=True)
DB = "voters.db"
conn = sqlite3.connect(DB)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS voters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    voter_serial TEXT,
    voter_id TEXT,
    ward_no TEXT,
    booth_no TEXT,
    gender TEXT,
    age INTEGER,
    caste TEXT,
    address TEXT,
    mobile TEXT,
    relative_name TEXT,
    photo TEXT
)
""")

# wipe sample rows each run (safe for dev)
c.execute("DELETE FROM voters")

sample = [
    ("अश्विनी अविनाश भदाने", "001", "NQW3425030", "9", "1", "Female", 37, "GEN", "घर नं 12, गाव", "9876543210", "अविनाश भदाने", "static/photos/1.jpg"),
    ("रसूल रशीद खान", "002", "ABX1234001", "9", "1", "Male", 45, "OBC", "घर नं 7, गाव", "9876500001", "रशीद खान", "static/photos/2.jpg"),
    ("फारुख रशीद खान", "003", "ABX1234002", "9", "1", "Male", 30, "OBC", "घर नं 8, गाव", "9876500002", "रशीद खान", "static/photos/3.jpg"),
    ("सुनिल चंदू कोंडिया", "004", "ABX1234003", "9", "1", "Male", 40, "SC", "घर नं 19, गाव", "9876500003", "चंदू कोंडिया", "static/photos/4.jpg"),
    ("भरत साहेब राव कोसोदे", "005", "ABX1234004", "9", "1", "Male", 50, "GEN", "घर नं 21, गाव", "9876500004", "साहेब राव कोसोदे", "static/photos/5.jpg"),
    ("कुलदीप भरत कोसोदे", "006", "ABX1234005", "9", "1", "Male", 25, "GEN", "घर नं 23, गाव", "9876500005", "भरत कोसोदे", "static/photos/6.jpg"),
    ("सोनीला विश्वनाथ पाटील", "007", "ABX1234006", "9", "1", "Female", 29, "GEN", "घर नं 33, गाव", "9876500006", "विश्वनाथ पाटील", "static/photos/7.jpg"),
    ("विजय राजे शिंदे", "008", "ABX1234007", "9", "1", "Male", 60, "OBC", "घर नं 41, गाव", "9876500007", "राजे शिंदे", "static/photos/8.jpg"),
    ("नीलम अरविंद देशमुख", "009", "ABX1234008", "9", "1", "Female", 34, "GEN", "घर नं 52, गाव", "9876500008", "अरविंद देशमुख", "static/photos/9.jpg"),
    ("मनीष कुमार", "010", "ABX1234009", "9", "1", "Male", 22, "SC", "घर नं 61, गाव", "9876500009", "कुमार", "static/photos/10.jpg"),
]

c.executemany("""
INSERT INTO voters (name, voter_serial, voter_id, ward_no, booth_no, gender, age, caste, address, mobile, relative_name, photo)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", sample)

conn.commit()
conn.close()
print("✅ voters.db created with sample data. Place 1.jpg..10.jpg into static/photos/")
