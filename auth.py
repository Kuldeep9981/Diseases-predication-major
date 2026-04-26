import sqlite3
import hashlib
import os
import re
from datetime import datetime

DB_PATH = "users.db"

def hash_password(password: str) -> str:
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
    return salt.hex() + ":" + key.hex()

def verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt_hex, key_hex = stored_hash.split(":")
        salt = bytes.fromhex(salt_hex)
        key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
        return key.hex() == key_hex
    except Exception:
        return False

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT    UNIQUE NOT NULL,
                email    TEXT    UNIQUE NOT NULL,
                password TEXT    NOT NULL,
                created  TEXT    NOT NULL
            )
        """)
        conn.commit()

def signup_user(username: str, email: str, password: str) -> tuple[bool, str]:
    if len(username) < 3:
        return False, "Username must be at least 3 characters."
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return False, "Invalid email address."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."

    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                "INSERT INTO users (username, email, password, created) VALUES (?, ?, ?, ?)",
                (username.strip(), email.strip().lower(), hash_password(password), datetime.now().isoformat())
            )
            conn.commit()
        return True, "Account created successfully!"
    except sqlite3.IntegrityError as e:
        if "username" in str(e):
            return False, "Username already taken."
        if "email" in str(e):
            return False, "Email already registered."
        return False, "Signup failed."

def signin_user(login: str, password: str) -> tuple[bool, str, dict]:
    """login can be username OR email"""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM users WHERE username = ? OR email = ?",
            (login.strip(), login.strip().lower())
        ).fetchone()

    if not row:
        return False, "User not found.", {}
    if not verify_password(password, row["password"]):
        return False, "Incorrect password.", {}

    user_info = {"id": row["id"], "username": row["username"], "email": row["email"]}
    return True, "Signed in successfully!", user_info