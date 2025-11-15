"""Validation utilities"""
import re
from typing import Optional


def validate_cnp(cnp: str) -> bool:
    """
    Validate Romanian CNP (Personal Numeric Code)
    Returns True if valid, False otherwise
    """
    if not cnp or len(cnp) != 13:
        return False
    
    if not cnp.isdigit():
        return False
    
    # Check control digit
    control_string = "279146358279"
    control_sum = sum(int(cnp[i]) * int(control_string[i]) for i in range(12))
    control_digit = control_sum % 11
    
    if control_digit == 10:
        control_digit = 1
    
    return int(cnp[12]) == control_digit


def validate_phone_number(phone: str) -> bool:
    """
    Validate Romanian phone number
    Accepts formats: 0712345678, +40712345678, 40712345678
    """
    if not phone:
        return False
    
    # Remove spaces and dashes
    phone = re.sub(r'[\s\-]', '', phone)
    
    # Check Romanian mobile patterns
    patterns = [
        r'^07\d{8}$',  # 0712345678
        r'^\+407\d{8}$',  # +40712345678
        r'^407\d{8}$',  # 40712345678
    ]
    
    return any(re.match(pattern, phone) for pattern in patterns)


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal and other issues
    """
    # Remove path separators
    filename = filename.replace('/', '_').replace('\\', '_')
    
    # Remove or replace special characters
    filename = re.sub(r'[<>:"|?*]', '_', filename)
    
    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:250] + ('.' + ext if ext else '')
    
    return filename


def validate_file_extension(filename: str, allowed_extensions: set) -> bool:
    """
    Validate file extension
    """
    if not filename or '.' not in filename:
        return False
    
    ext = '.' + filename.rsplit('.', 1)[1].lower()
    return ext in allowed_extensions
