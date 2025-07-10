"""
暗号化・復号化のためのユーティリティモジュール
ハッシュ化、暗号化、復号化、トークン生成などのセキュリティ機能を提供します。
"""

import os
import base64
import hashlib
import secrets
import logging
from typing import Optional, Union, Dict, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import jwt

# ログ設定
logger = logging.getLogger(__name__)

# 定数定義
DEFAULT_SALT_LENGTH = 32
DEFAULT_TOKEN_LENGTH = 32
DEFAULT_ITERATIONS = 100000
SUPPORTED_HASH_ALGORITHMS = ['md5', 'sha1', 'sha256', 'sha512']


def generate_salt(length: int = DEFAULT_SALT_LENGTH) -> bytes:
    """
    暗号学的に安全なソルトを生成します。
    
    Args:
        length: ソルトの長さ（バイト）
    
    Returns:
        bytes: 生成されたソルト
    """
    salt = os.urandom(length)
    logger.debug(f"ソルト生成完了: 長さ={length}バイト")
    return salt


def generate_secure_token(length: int = DEFAULT_TOKEN_LENGTH, url_safe: bool = True) -> str:
    """
    暗号学的に安全なトークンを生成します。
    
    Args:
        length: トークンの長さ（バイト）
        url_safe: URL安全な文字のみを使用するかどうか
    
    Returns:
        str: 生成されたトークン
    """
    token_bytes = secrets.token_bytes(length)
    
    if url_safe:
        token = base64.urlsafe_b64encode(token_bytes).decode('utf-8').rstrip('=')
    else:
        token = base64.b64encode(token_bytes).decode('utf-8')
    
    logger.debug(f"セキュアトークン生成完了: 長さ={len(token)}文字")
    return token


def hash_password(password: str, salt: Optional[bytes] = None, 
                 iterations: int = DEFAULT_ITERATIONS) -> Dict[str, str]:
    """
    パスワードをハッシュ化します（PBKDF2使用）。
    
    Args:
        password: ハッシュ化するパスワード
        salt: ソルト（Noneの場合は自動生成）
        iterations: 反復回数
    
    Returns:
        Dict[str, str]: ハッシュ値とソルトを含む辞書
    """
    if salt is None:
        salt = generate_salt()
    
    try:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=iterations,
        )
        
        password_bytes = password.encode('utf-8')
        key = kdf.derive(password_bytes)
        
        result = {
            'hash': base64.b64encode(key).decode('utf-8'),
            'salt': base64.b64encode(salt).decode('utf-8'),
            'iterations': str(iterations)
        }
        
        logger.debug("パスワードハッシュ化完了")
        return result
        
    except Exception as e:
        logger.error(f"パスワードハッシュ化エラー: {str(e)}")
        raise


def verify_password(password: str, stored_hash: str, stored_salt: str, 
                   iterations: int = DEFAULT_ITERATIONS) -> bool:
    """
    パスワードを検証します。
    
    Args:
        password: 検証するパスワード
        stored_hash: 保存されたハッシュ値
        stored_salt: 保存されたソルト
        iterations: 反復回数
    
    Returns:
        bool: パスワードが正しい場合True
    """
    try:
        salt = base64.b64decode(stored_salt.encode('utf-8'))
        expected_hash = base64.b64decode(stored_hash.encode('utf-8'))
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=iterations,
        )
        
        password_bytes = password.encode('utf-8')
        derived_key = kdf.derive(password_bytes)
        
        is_valid = secrets.compare_digest(derived_key, expected_hash)
        logger.debug(f"パスワード検証完了: 結果={is_valid}")
        return is_valid
        
    except Exception as e:
        logger.error(f"パスワード検証エラー: {str(e)}")
        return False


def simple_hash(data: Union[str, bytes], algorithm: str = 'sha256') -> str:
    """
    データの簡単なハッシュ値を計算します。
    
    Args:
        data: ハッシュ化するデータ
        algorithm: ハッシュアルゴリズム
    
    Returns:
        str: ハッシュ値（16進数文字列）
    
    Raises:
        ValueError: サポートされていないアルゴリズムの場合
    """
    if algorithm not in SUPPORTED_HASH_ALGORITHMS:
        raise ValueError(f"サポートされていないアルゴリズム: {algorithm}")
    
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    try:
        hash_obj = hashlib.new(algorithm)
        hash_obj.update(data)
        hash_value = hash_obj.hexdigest()
        
        logger.debug(f"ハッシュ計算完了: アルゴリズム={algorithm}")
        return hash_value
        
    except Exception as e:
        logger.error(f"ハッシュ計算エラー: {str(e)}")
        raise


def generate_fernet_key() -> bytes:
    """
    Fernet暗号化用のキーを生成します。
    
    Returns:
        bytes: 生成されたキー
    """
    key = Fernet.generate_key()
    logger.debug("Fernetキー生成完了")
    return key


def encrypt_data(data: Union[str, bytes], key: bytes) -> str:
    """
    データを暗号化します（Fernet使用）。
    
    Args:
        data: 暗号化するデータ
        key: 暗号化キー
    
    Returns:
        str: 暗号化されたデータ（Base64エンコード）
    """
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    try:
        fernet = Fernet(key)
        encrypted_data = fernet.encrypt(data)
        encoded_data = base64.b64encode(encrypted_data).decode('utf-8')
        
        logger.debug("データ暗号化完了")
        return encoded_data
        
    except Exception as e:
        logger.error(f"データ暗号化エラー: {str(e)}")
        raise


def decrypt_data(encrypted_data: str, key: bytes) -> str:
    """
    データを復号化します（Fernet使用）。
    
    Args:
        encrypted_data: 暗号化されたデータ（Base64エンコード）
        key: 復号化キー
    
    Returns:
        str: 復号化されたデータ
    """
    try:
        encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
        fernet = Fernet(key)
        decrypted_data = fernet.decrypt(encrypted_bytes)
        
        result = decrypted_data.decode('utf-8')
        logger.debug("データ復号化完了")
        return result
        
    except Exception as e:
        logger.error(f"データ復号化エラー: {str(e)}")
        raise


def generate_rsa_keypair(key_size: int = 2048) -> Dict[str, bytes]:
    """
    RSA公開鍵・秘密鍵ペアを生成します。
    
    Args:
        key_size: キーサイズ（ビット）
    
    Returns:
        Dict[str, bytes]: 公開鍵と秘密鍵を含む辞書
    """
    try:
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
        )
        
        public_key = private_key.public_key()
        
        # PEM形式でシリアライズ
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        result = {
            'private_key': private_pem,
            'public_key': public_pem
        }
        
        logger.debug(f"RSAキーペア生成完了: キーサイズ={key_size}ビット")
        return result
        
    except Exception as e:
        logger.error(f"RSAキーペア生成エラー: {str(e)}")
        raise


def create_jwt_token(payload: Dict[str, Any], secret_key: str, 
                    algorithm: str = 'HS256', expires_in: Optional[int] = None) -> str:
    """
    JWTトークンを作成します。
    
    Args:
        payload: トークンに含めるペイロード
        secret_key: 署名用の秘密鍵
        algorithm: 署名アルゴリズム
        expires_in: 有効期限（秒）
    
    Returns:
        str: 生成されたJWTトークン
    """
    try:
        import time
        
        # 有効期限を設定
        if expires_in:
            payload['exp'] = int(time.time()) + expires_in
        
        # 発行時刻を設定
        payload['iat'] = int(time.time())
        
        token = jwt.encode(payload, secret_key, algorithm=algorithm)
        
        logger.debug("JWTトークン作成完了")
        return token
        
    except Exception as e:
        logger.error(f"JWTトークン作成エラー: {str(e)}")
        raise


def verify_jwt_token(token: str, secret_key: str, 
                    algorithm: str = 'HS256') -> Optional[Dict[str, Any]]:
    """
    JWTトークンを検証します。
    
    Args:
        token: 検証するJWTトークン
        secret_key: 検証用の秘密鍵
        algorithm: 署名アルゴリズム
    
    Returns:
        Optional[Dict[str, Any]]: 検証成功時はペイロード、失敗時はNone
    """
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        logger.debug("JWTトークン検証成功")
        return payload
        
    except jwt.ExpiredSignatureError:
        logger.warning("JWTトークンの有効期限が切れています")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"無効なJWTトークン: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"JWTトークン検証エラー: {str(e)}")
        return None


def mask_sensitive_string(text: str, visible_chars: int = 4, mask_char: str = '*') -> str:
    """
    機密文字列をマスクします。
    
    Args:
        text: マスクする文字列
        visible_chars: 表示する文字数（前後）
        mask_char: マスク文字
    
    Returns:
        str: マスクされた文字列
    """
    if len(text) <= visible_chars * 2:
        return mask_char * len(text)
    
    start = text[:visible_chars]
    end = text[-visible_chars:]
    middle = mask_char * (len(text) - visible_chars * 2)
    
    masked = start + middle + end
    logger.debug("機密文字列マスク完了")
    return masked


def generate_api_key(prefix: str = '', length: int = 32) -> str:
    """
    APIキーを生成します。
    
    Args:
        prefix: プレフィックス
        length: キーの長さ
    
    Returns:
        str: 生成されたAPIキー
    """
    key_part = generate_secure_token(length, url_safe=True)
    
    if prefix:
        api_key = f"{prefix}_{key_part}"
    else:
        api_key = key_part
    
    logger.debug(f"APIキー生成完了: プレフィックス={prefix}")
    return api_key


def constant_time_compare(a: str, b: str) -> bool:
    """
    定数時間での文字列比較を行います（タイミング攻撃対策）。
    
    Args:
        a: 比較する文字列1
        b: 比較する文字列2
    
    Returns:
        bool: 文字列が等しい場合True
    """
    try:
        return secrets.compare_digest(a.encode('utf-8'), b.encode('utf-8'))
    except Exception as e:
        logger.error(f"定数時間比較エラー: {str(e)}")
        return False


def derive_key_from_password(password: str, salt: bytes, 
                           key_length: int = 32, iterations: int = DEFAULT_ITERATIONS) -> bytes:
    """
    パスワードから暗号化キーを導出します。
    
    Args:
        password: パスワード
        salt: ソルト
        key_length: キーの長さ（バイト）
        iterations: 反復回数
    
    Returns:
        bytes: 導出されたキー
    """
    try:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=key_length,
            salt=salt,
            iterations=iterations,
        )
        
        password_bytes = password.encode('utf-8')
        key = kdf.derive(password_bytes)
        
        logger.debug("パスワードからキー導出完了")
        return key
        
    except Exception as e:
        logger.error(f"キー導出エラー: {str(e)}")
        raise
