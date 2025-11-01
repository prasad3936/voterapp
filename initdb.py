# init_db.py
import sqlite3, os

os.makedirs("static/photos", exist_ok=True)

conn = sqlite3.connect("voters.db")
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS voters (
 id INTEGER PRIMARY KEY AUTOINCREMENT,

 serial TEXT,          -- मतदार अनुक्रमांक
 name TEXT,            -- मतदाराचे नाव
 relation TEXT,        -- वडील/पतीचे नाव
 house_no TEXT,        -- घर क्रमांक
 age TEXT,             -- वय (keep text because Marathi digits possible)
 gender TEXT,          -- लिंग (पुरुष/स्त्री)
 epic TEXT,            -- EPIC / Voter ID

 ward_no TEXT,         -- प्रभाग क्र
 booth_no TEXT,        -- यादी भाग क्र

 address TEXT,         -- पत्ता (if needed later)
 photo TEXT            -- फोटो (default photo)
)
""")

conn.commit()
conn.close()
print("✅ DB Table Ready: voters")
