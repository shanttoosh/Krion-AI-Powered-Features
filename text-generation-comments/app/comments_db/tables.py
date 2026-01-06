import sys
import os

# 🔴 FIX PYTHON PATH FIRST (THIS MUST BE AT TOP)
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ✅ NOW imports will work
from app.comments_db.base import Base
from app.comments_db.session import sync_engine

# 🚨 CRITICAL: import models so SQLAlchemy registers tables
import app.comments_db.models


def create_tables():
    print("📌 Tables BEFORE:", Base.metadata.tables.keys())
    Base.metadata.create_all(bind=sync_engine)
    print("✅ Tables AFTER:", Base.metadata.tables.keys())


if __name__ == "__main__":
    create_tables()
