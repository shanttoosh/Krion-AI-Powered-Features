import sys
import os
import sqlite3

# 🔧 Fix import path for standalone script
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

print("📁 Current working directory:", os.getcwd())
print("📄 DB file exists:", os.path.exists("comments.db"))

conn = sqlite3.connect("comments.db")
cursor = conn.cursor()

# -------------------------
# LIST TABLES
# -------------------------
print("\n📌 Tables:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
print(cursor.fetchall())

# -------------------------
# COMMENT REQUESTS
# -------------------------
print("\n📌 comment_requests rows:")
cursor.execute("SELECT * FROM comment_requests")
print(cursor.fetchall())

# -------------------------
# COMMENT SUGGESTIONS
# -------------------------
print("\n📌 comment_suggestions rows:")
cursor.execute("SELECT * FROM comment_suggestions")
print(cursor.fetchall())

# -------------------------
# ✅ COMMENT FEEDBACK (ADD HERE)
# -------------------------
print("\n📌 comment_feedback rows:")
cursor.execute("SELECT * FROM comment_feedback")
print(cursor.fetchall())

conn.close()
