import hashlib
import os
import secrets
from database import get_user, add_user

# Global current user session
_current_user = None

def hash_password(password, salt=None):
    """Hashes a password using PBKDF2 with SHA-256 and a random salt."""
    if salt is None:
        salt = secrets.token_hex(16)
    
    # Standard Python hashlib PBKDF2 hash
    pwd_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000  # number of iterations
    ).hex()
    
    # Store salt and hash together split by a colon
    return f"{salt}:{pwd_hash}"

def verify_password(stored_password_hash, provided_password):
    """Verifies a password against its stored hash."""
    try:
        salt, stored_hash = stored_password_hash.split(":")
        provided_hash = hashlib.pbkdf2_hmac(
            'sha256',
            provided_password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        ).hex()
        return secrets.compare_digest(stored_hash, provided_hash)
    except (ValueError, AttributeError):
        return False

def login(username, password):
    """Authenticates a user and sets the current session."""
    global _current_user
    user = get_user(username)
    if not user:
        return False, "المستخدم غير موجود"
        
    if verify_password(user['password_hash'], password):
        _current_user = user
        return True, user
    else:
        return False, "كلمة المرور غير صحيحة"

def logout():
    """Clears the active session."""
    global _current_user
    _current_user = None

def get_current_user():
    """Returns the currently logged-in user dictionary."""
    return _current_user

def create_initial_admin(username="admin", password="admin123", full_name="مدير النظام"):
    """Creates a default admin user if one doesn't exist already."""
    user = get_user(username)
    if not user:
        pwd_hash = hash_password(password)
        add_user(username, pwd_hash, full_name, "admin")
        return True
    return False
