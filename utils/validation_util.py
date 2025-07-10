"""
データ検証のためのユーティリティモジュール
各種データの妥当性検証、フォーマットチェック、バリデーション機能を提供します。
"""

import re
import logging
from typing import Any, List, Dict, Optional, Union, Callable
from datetime import datetime, date
from urllib.parse import urlparse

# ログ設定
logger = logging.getLogger(__name__)

# 正規表現パターン（パフォーマンス向上のためプリコンパイル）
EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
PHONE_JP_PATTERN = re.compile(r'^(\+81|0)[0-9]{1,4}-?[0-9]{1,4}-?[0-9]{3,4}$')
PHONE_MOBILE_JP_PATTERN = re.compile(r'^(\+81|0)[789]0-?[0-9]{4}-?[0-9]{4}$')
ZIP_CODE_JP_PATTERN = re.compile(r'^\d{3}-?\d{4}$')
CREDIT_CARD_PATTERN = re.compile(r'^[0-9]{13,19}$')
IPV4_PATTERN = re.compile(r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')
IPV6_PATTERN = re.compile(r'^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$')
HIRAGANA_PATTERN = re.compile(r'^[ひらがな\u3040-\u309F]+$')
KATAKANA_PATTERN = re.compile(r'^[カタカナ\u30A0-\u30FF]+$')
ALPHANUMERIC_PATTERN = re.compile(r'^[a-zA-Z0-9]+$')


class ValidationError(Exception):
    """バリデーションエラー用のカスタム例外クラス"""
    pass


class ValidationResult:
    """バリデーション結果を格納するクラス"""
    
    def __init__(self, is_valid: bool = True, errors: Optional[List[str]] = None):
        self.is_valid = is_valid
        self.errors = errors or []
    
    def add_error(self, error: str) -> None:
        """エラーメッセージを追加"""
        self.errors.append(error)
        self.is_valid = False
    
    def __bool__(self) -> bool:
        return self.is_valid
    
    def __str__(self) -> str:
        if self.is_valid:
            return "検証成功"
        return f"検証失敗: {', '.join(self.errors)}"


def is_valid_email(email: str) -> bool:
    """
    メールアドレスの妥当性を検証します。
    
    Args:
        email: 検証するメールアドレス
    
    Returns:
        bool: 有効なメールアドレスの場合True
    """
    if not email or not isinstance(email, str):
        return False
    
    return bool(EMAIL_PATTERN.match(email.strip()))


def is_valid_phone_jp(phone: str, mobile_only: bool = False) -> bool:
    """
    日本の電話番号の妥当性を検証します。
    
    Args:
        phone: 検証する電話番号
        mobile_only: 携帯電話番号のみを許可するかどうか
    
    Returns:
        bool: 有効な電話番号の場合True
    """
    if not phone or not isinstance(phone, str):
        return False
    
    phone = phone.replace(' ', '').replace('-', '')
    
    if mobile_only:
        return bool(PHONE_MOBILE_JP_PATTERN.match(phone))
    else:
        return bool(PHONE_JP_PATTERN.match(phone))


def is_valid_zip_code_jp(zip_code: str) -> bool:
    """
    日本の郵便番号の妥当性を検証します。
    
    Args:
        zip_code: 検証する郵便番号
    
    Returns:
        bool: 有効な郵便番号の場合True
    """
    if not zip_code or not isinstance(zip_code, str):
        return False
    
    return bool(ZIP_CODE_JP_PATTERN.match(zip_code.strip()))


def is_valid_url(url: str, require_https: bool = False) -> bool:
    """
    URLの妥当性を検証します。
    
    Args:
        url: 検証するURL
        require_https: HTTPSを必須とするかどうか
    
    Returns:
        bool: 有効なURLの場合True
    """
    if not url or not isinstance(url, str):
        return False
    
    try:
        parsed = urlparse(url.strip())
        
        # スキームとネットロケーションが存在することを確認
        if not parsed.scheme or not parsed.netloc:
            return False
        
        # HTTPSが必須の場合
        if require_https and parsed.scheme != 'https':
            return False
        
        # 有効なスキームかどうか確認
        valid_schemes = ['http', 'https', 'ftp', 'ftps']
        if parsed.scheme not in valid_schemes:
            return False
        
        return True
        
    except Exception:
        return False


def is_valid_ip_address(ip: str, version: Optional[int] = None) -> bool:
    """
    IPアドレスの妥当性を検証します。
    
    Args:
        ip: 検証するIPアドレス
        version: IPバージョン（4または6、Noneの場合は両方を許可）
    
    Returns:
        bool: 有効なIPアドレスの場合True
    """
    if not ip or not isinstance(ip, str):
        return False
    
    ip = ip.strip()
    
    if version == 4 or version is None:
        if IPV4_PATTERN.match(ip):
            return True
    
    if version == 6 or version is None:
        if IPV6_PATTERN.match(ip):
            return True
    
    return False


def is_valid_credit_card(card_number: str, validate_luhn: bool = True) -> bool:
    """
    クレジットカード番号の妥当性を検証します。
    
    Args:
        card_number: 検証するクレジットカード番号
        validate_luhn: Luhnアルゴリズムで検証するかどうか
    
    Returns:
        bool: 有効なクレジットカード番号の場合True
    """
    if not card_number or not isinstance(card_number, str):
        return False
    
    # スペースとハイフンを除去
    card_number = card_number.replace(' ', '').replace('-', '')
    
    # 基本的なフォーマットチェック
    if not CREDIT_CARD_PATTERN.match(card_number):
        return False
    
    # Luhnアルゴリズムによる検証
    if validate_luhn:
        return _validate_luhn(card_number)
    
    return True


def _validate_luhn(card_number: str) -> bool:
    """
    Luhnアルゴリズムでクレジットカード番号を検証します。
    
    Args:
        card_number: 検証するクレジットカード番号
    
    Returns:
        bool: Luhnアルゴリズムで有効な場合True
    """
    def luhn_checksum(card_num):
        def digits_of(n):
            return [int(d) for d in str(n)]
        
        digits = digits_of(card_num)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(d * 2))
        return checksum % 10
    
    return luhn_checksum(card_number) == 0


def is_valid_japanese_text(text: str, text_type: str = 'any') -> bool:
    """
    日本語テキストの妥当性を検証します。
    
    Args:
        text: 検証するテキスト
        text_type: テキストタイプ（'hiragana', 'katakana', 'any'）
    
    Returns:
        bool: 有効な日本語テキストの場合True
    """
    if not text or not isinstance(text, str):
        return False
    
    text = text.strip()
    
    if text_type == 'hiragana':
        return bool(HIRAGANA_PATTERN.match(text))
    elif text_type == 'katakana':
        return bool(KATAKANA_PATTERN.match(text))
    else:
        # 日本語文字（ひらがな、カタカナ、漢字）が含まれているかチェック
        japanese_chars = re.findall(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', text)
        return len(japanese_chars) > 0


def validate_password_strength(password: str, min_length: int = 8,
                             require_uppercase: bool = True,
                             require_lowercase: bool = True,
                             require_digits: bool = True,
                             require_special: bool = True) -> ValidationResult:
    """
    パスワードの強度を検証します。
    
    Args:
        password: 検証するパスワード
        min_length: 最小長
        require_uppercase: 大文字を必須とするかどうか
        require_lowercase: 小文字を必須とするかどうか
        require_digits: 数字を必須とするかどうか
        require_special: 特殊文字を必須とするかどうか
    
    Returns:
        ValidationResult: 検証結果
    """
    result = ValidationResult()
    
    if not password or not isinstance(password, str):
        result.add_error("パスワードが指定されていません")
        return result
    
    # 長さチェック
    if len(password) < min_length:
        result.add_error(f"パスワードは{min_length}文字以上である必要があります")
    
    # 大文字チェック
    if require_uppercase and not re.search(r'[A-Z]', password):
        result.add_error("パスワードには大文字を含める必要があります")
    
    # 小文字チェック
    if require_lowercase and not re.search(r'[a-z]', password):
        result.add_error("パスワードには小文字を含める必要があります")
    
    # 数字チェック
    if require_digits and not re.search(r'\d', password):
        result.add_error("パスワードには数字を含める必要があります")
    
    # 特殊文字チェック
    if require_special and not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password):
        result.add_error("パスワードには特殊文字を含める必要があります")
    
    logger.debug(f"パスワード強度検証完了: {result}")
    return result


def validate_age(birth_date: Union[datetime, date], min_age: int = 0, max_age: int = 150) -> ValidationResult:
    """
    年齢の妥当性を検証します。
    
    Args:
        birth_date: 生年月日
        min_age: 最小年齢
        max_age: 最大年齢
    
    Returns:
        ValidationResult: 検証結果
    """
    result = ValidationResult()
    
    if not birth_date:
        result.add_error("生年月日が指定されていません")
        return result
    
    try:
        from .date_util import get_age
        age = get_age(birth_date)
        
        if age < min_age:
            result.add_error(f"年齢は{min_age}歳以上である必要があります")
        
        if age > max_age:
            result.add_error(f"年齢は{max_age}歳以下である必要があります")
        
    except Exception as e:
        result.add_error(f"年齢計算エラー: {str(e)}")
    
    logger.debug(f"年齢検証完了: {result}")
    return result


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> ValidationResult:
    """
    必須フィールドの存在を検証します。
    
    Args:
        data: 検証するデータ辞書
        required_fields: 必須フィールドのリスト
    
    Returns:
        ValidationResult: 検証結果
    """
    result = ValidationResult()
    
    if not isinstance(data, dict):
        result.add_error("データが辞書形式ではありません")
        return result
    
    for field in required_fields:
        if field not in data:
            result.add_error(f"必須フィールド '{field}' が存在しません")
        elif data[field] is None or (isinstance(data[field], str) and not data[field].strip()):
            result.add_error(f"必須フィールド '{field}' が空です")
    
    logger.debug(f"必須フィールド検証完了: {result}")
    return result


def validate_data_types(data: Dict[str, Any], type_specs: Dict[str, type]) -> ValidationResult:
    """
    データ型の妥当性を検証します。
    
    Args:
        data: 検証するデータ辞書
        type_specs: フィールド名と期待する型の辞書
    
    Returns:
        ValidationResult: 検証結果
    """
    result = ValidationResult()
    
    if not isinstance(data, dict):
        result.add_error("データが辞書形式ではありません")
        return result
    
    for field, expected_type in type_specs.items():
        if field in data and data[field] is not None:
            if not isinstance(data[field], expected_type):
                result.add_error(f"フィールド '{field}' の型が正しくありません。期待: {expected_type.__name__}, 実際: {type(data[field]).__name__}")
    
    logger.debug(f"データ型検証完了: {result}")
    return result


def validate_string_length(text: str, field_name: str, min_length: int = 0, 
                          max_length: Optional[int] = None) -> ValidationResult:
    """
    文字列の長さを検証します。
    
    Args:
        text: 検証する文字列
        field_name: フィールド名
        min_length: 最小長
        max_length: 最大長
    
    Returns:
        ValidationResult: 検証結果
    """
    result = ValidationResult()
    
    if not isinstance(text, str):
        result.add_error(f"フィールド '{field_name}' は文字列である必要があります")
        return result
    
    length = len(text)
    
    if length < min_length:
        result.add_error(f"フィールド '{field_name}' は{min_length}文字以上である必要があります")
    
    if max_length is not None and length > max_length:
        result.add_error(f"フィールド '{field_name}' は{max_length}文字以下である必要があります")
    
    logger.debug(f"文字列長検証完了: {field_name} = {result}")
    return result


def validate_numeric_range(value: Union[int, float], field_name: str,
                          min_value: Optional[Union[int, float]] = None,
                          max_value: Optional[Union[int, float]] = None) -> ValidationResult:
    """
    数値の範囲を検証します。
    
    Args:
        value: 検証する数値
        field_name: フィールド名
        min_value: 最小値
        max_value: 最大値
    
    Returns:
        ValidationResult: 検証結果
    """
    result = ValidationResult()
    
    if not isinstance(value, (int, float)):
        result.add_error(f"フィールド '{field_name}' は数値である必要があります")
        return result
    
    if min_value is not None and value < min_value:
        result.add_error(f"フィールド '{field_name}' は{min_value}以上である必要があります")
    
    if max_value is not None and value > max_value:
        result.add_error(f"フィールド '{field_name}' は{max_value}以下である必要があります")
    
    logger.debug(f"数値範囲検証完了: {field_name} = {result}")
    return result


def create_custom_validator(validation_func: Callable[[Any], bool], 
                           error_message: str) -> Callable[[Any], ValidationResult]:
    """
    カスタムバリデーターを作成します。
    
    Args:
        validation_func: 検証関数
        error_message: エラーメッセージ
    
    Returns:
        Callable: バリデーター関数
    """
    def validator(value: Any) -> ValidationResult:
        result = ValidationResult()
        try:
            if not validation_func(value):
                result.add_error(error_message)
        except Exception as e:
            result.add_error(f"検証エラー: {str(e)}")
        return result
    
    return validator
