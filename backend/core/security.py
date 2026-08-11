"""
文件路径: /backend/core/security.py
功能描述: 安全工具模块
主要功能:
    - 密码哈希（bcrypt）
    - 密码验证
"""
import bcrypt
import re


def hash_password(password: str) -> str:
    """哈希密码"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'), 
            hashed_password.encode('utf-8')
        )
    except Exception:
        return False


def validate_password(password: str) -> tuple[bool, str]:
    """
    验证密码强度
    
    返回：(是否有效，错误信息)
    """
    if len(password) < 8:
        return False, "密码长度至少 8 位"
    
    if not re.search(r"[a-zA-Z]", password):
        return False, "密码必须包含字母"
    
    if not re.search(r"\d", password):
        return False, "密码必须包含数字"
    
    return True, ""
