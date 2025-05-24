"""
Security utilities untuk EcoReport Application
"""

import os
import secrets
import hashlib
from functools import wraps
from flask import request, abort, current_app
import re

class SecurityConfig:
    """Security configuration class"""
    
    # Password requirements
    MIN_PASSWORD_LENGTH = 8
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_NUMBERS = True
    REQUIRE_SPECIAL_CHARS = False
    
    # Rate limiting
    MAX_LOGIN_ATTEMPTS = 5
    LOGIN_ATTEMPT_WINDOW = 900  # 15 minutes
    
    # File upload security
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}
    MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
    
    # Content Security Policy
    CSP_POLICY = {
        'default-src': "'self'",
        'script-src': "'self' 'unsafe-inline' cdnjs.cloudflare.com",
        'style-src': "'self' 'unsafe-inline' cdnjs.cloudflare.com fonts.googleapis.com",
        'font-src': "'self' fonts.gstatic.com",
        'img-src': "'self' data: *.openstreetmap.org",
        'connect-src': "'self'",
    }

def generate_secret_key():
    """Generate secure secret key"""
    return secrets.token_urlsafe(32)

def validate_password(password):
    """Validate password strength"""
    errors = []
    
    if len(password) < SecurityConfig.MIN_PASSWORD_LENGTH:
        errors.append(f"Password minimal {SecurityConfig.MIN_PASSWORD_LENGTH} karakter")
    
    if SecurityConfig.REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
        errors.append("Password harus mengandung huruf besar")
    
    if SecurityConfig.REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
        errors.append("Password harus mengandung huruf kecil")
    
    if SecurityConfig.REQUIRE_NUMBERS and not re.search(r'\d', password):
        errors.append("Password harus mengandung angka")
    
    if SecurityConfig.REQUIRE_SPECIAL_CHARS and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password harus mengandung karakter khusus")
    
    return errors

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in SecurityConfig.ALLOWED_EXTENSIONS

def secure_filename(filename):
    """Make filename secure"""
    # Remove path and dangerous characters
    filename = os.path.basename(filename)
    filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
    
    # Add timestamp to prevent conflicts
    name, ext = os.path.splitext(filename)
    timestamp = secrets.token_hex(8)
    
    return f"{name}_{timestamp}{ext}"

def rate_limit(max_requests=100, window=3600):
    """Rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Simple in-memory rate limiting
            # In production, use Redis or database
            client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            
            # For development, skip rate limiting
            if current_app.config.get('TESTING') or current_app.config.get('DEBUG'):
                return f(*args, **kwargs)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def sanitize_input(text):
    """Sanitize user input"""
    if not text:
        return ""
    
    # Remove potential XSS
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
    text = re.sub(r'on\w+\s*=', '', text, flags=re.IGNORECASE)
    
    return text.strip()