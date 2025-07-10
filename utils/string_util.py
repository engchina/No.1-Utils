"""
文字列操作のためのユーティリティモジュール
文字列の変換、検証、フォーマット、解析などの機能を提供します。
"""

import re
import string
import secrets
import unicodedata
import logging
from typing import List, Optional, Dict, Any, Union

# ログ設定
logger = logging.getLogger(__name__)

# 定数定義
DEFAULT_ENCODING = 'utf-8'
ALPHANUMERIC_CHARS = string.ascii_letters + string.digits
SPECIAL_CHARS = "!@#$%^&*()_+-=[]{}|;:,.<>?"


def is_empty_or_whitespace(text: Optional[str]) -> bool:
    """
    文字列が空またはホワイトスペースのみかどうかを判定します。
    
    Args:
        text: 判定する文字列
    
    Returns:
        bool: 空またはホワイトスペースのみの場合True
    """
    return not text or text.isspace()


def safe_strip(text: Optional[str], chars: Optional[str] = None) -> str:
    """
    安全に文字列の前後の空白を除去します。
    
    Args:
        text: 処理する文字列
        chars: 除去する文字（デフォルト: None）
    
    Returns:
        str: 前後の空白が除去された文字列
    """
    if text is None:
        return ""
    return text.strip(chars)


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """
    文字列を指定された長さで切り詰めます。
    
    Args:
        text: 切り詰める文字列
        max_length: 最大長
        suffix: 切り詰められた場合に追加する接尾辞
    
    Returns:
        str: 切り詰められた文字列
    """
    if len(text) <= max_length:
        return text
    
    if max_length <= len(suffix):
        return suffix[:max_length]
    
    return text[:max_length - len(suffix)] + suffix


def camel_to_snake(text: str) -> str:
    """
    キャメルケースをスネークケースに変換します。
    
    Args:
        text: 変換する文字列
    
    Returns:
        str: スネークケースに変換された文字列
    """
    # 大文字の前にアンダースコアを挿入
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def snake_to_camel(text: str, capitalize_first: bool = False) -> str:
    """
    スネークケースをキャメルケースに変換します。
    
    Args:
        text: 変換する文字列
        capitalize_first: 最初の文字を大文字にするかどうか
    
    Returns:
        str: キャメルケースに変換された文字列
    """
    components = text.split('_')
    if capitalize_first:
        return ''.join(word.capitalize() for word in components)
    else:
        return components[0] + ''.join(word.capitalize() for word in components[1:])


def kebab_to_camel(text: str, capitalize_first: bool = False) -> str:
    """
    ケバブケースをキャメルケースに変換します。
    
    Args:
        text: 変換する文字列
        capitalize_first: 最初の文字を大文字にするかどうか
    
    Returns:
        str: キャメルケースに変換された文字列
    """
    components = text.split('-')
    if capitalize_first:
        return ''.join(word.capitalize() for word in components)
    else:
        return components[0] + ''.join(word.capitalize() for word in components[1:])


def generate_random_string(length: int, include_special: bool = False) -> str:
    """
    ランダムな文字列を生成します。
    
    Args:
        length: 生成する文字列の長さ
        include_special: 特殊文字を含めるかどうか
    
    Returns:
        str: 生成されたランダム文字列
    """
    chars = ALPHANUMERIC_CHARS
    if include_special:
        chars += SPECIAL_CHARS
    
    return ''.join(secrets.choice(chars) for _ in range(length))


def mask_sensitive_data(text: str, mask_char: str = "*", 
                       visible_start: int = 2, visible_end: int = 2) -> str:
    """
    機密データをマスクします。
    
    Args:
        text: マスクする文字列
        mask_char: マスク文字
        visible_start: 開始部分の表示文字数
        visible_end: 終了部分の表示文字数
    
    Returns:
        str: マスクされた文字列
    """
    if len(text) <= visible_start + visible_end:
        return mask_char * len(text)
    
    start = text[:visible_start]
    end = text[-visible_end:] if visible_end > 0 else ""
    middle = mask_char * (len(text) - visible_start - visible_end)
    
    return start + middle + end


def extract_numbers(text: str) -> List[str]:
    """
    文字列から数字を抽出します。
    
    Args:
        text: 処理する文字列
    
    Returns:
        List[str]: 抽出された数字のリスト
    """
    return re.findall(r'\d+', text)


def extract_emails(text: str) -> List[str]:
    """
    文字列からメールアドレスを抽出します。
    
    Args:
        text: 処理する文字列
    
    Returns:
        List[str]: 抽出されたメールアドレスのリスト
    """
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.findall(email_pattern, text)


def extract_urls(text: str) -> List[str]:
    """
    文字列からURLを抽出します。
    
    Args:
        text: 処理する文字列
    
    Returns:
        List[str]: 抽出されたURLのリスト
    """
    url_pattern = r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?'
    return re.findall(url_pattern, text)


def normalize_unicode(text: str, form: str = 'NFC') -> str:
    """
    Unicode文字列を正規化します。
    
    Args:
        text: 正規化する文字列
        form: 正規化形式（NFC, NFD, NFKC, NFKD）
    
    Returns:
        str: 正規化された文字列
    """
    return unicodedata.normalize(form, text)


def remove_accents(text: str) -> str:
    """
    文字列からアクセント記号を除去します。
    
    Args:
        text: 処理する文字列
    
    Returns:
        str: アクセント記号が除去された文字列
    """
    # NFD正規化でアクセント記号を分離
    nfd = unicodedata.normalize('NFD', text)
    # 結合文字（アクセント記号）を除去
    return ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')


def count_words(text: str, language: str = 'en') -> int:
    """
    文字列の単語数をカウントします。
    
    Args:
        text: カウントする文字列
        language: 言語（'en': 英語, 'ja': 日本語）
    
    Returns:
        int: 単語数
    """
    if language == 'ja':
        # 日本語の場合は文字数をカウント（空白を除く）
        return len(re.sub(r'\s+', '', text))
    else:
        # 英語の場合は単語数をカウント
        words = re.findall(r'\b\w+\b', text)
        return len(words)


def format_template(template: str, variables: Dict[str, Any], 
                   safe_mode: bool = True) -> str:
    """
    テンプレート文字列に変数を埋め込みます。
    
    Args:
        template: テンプレート文字列（{variable_name}形式）
        variables: 埋め込む変数の辞書
        safe_mode: 安全モード（存在しない変数をそのまま残す）
    
    Returns:
        str: 変数が埋め込まれた文字列
    """
    try:
        if safe_mode:
            # 存在しない変数はそのまま残す
            class SafeDict(dict):
                def __missing__(self, key):
                    return '{' + key + '}'
            
            return template.format_map(SafeDict(variables))
        else:
            return template.format(**variables)
    except KeyError as e:
        logger.error(f"テンプレート変数が見つかりません: {str(e)}")
        raise


def similarity_ratio(text1: str, text2: str) -> float:
    """
    2つの文字列の類似度を計算します（簡易版）。
    
    Args:
        text1: 比較する文字列1
        text2: 比較する文字列2
    
    Returns:
        float: 類似度（0.0-1.0）
    """
    if not text1 and not text2:
        return 1.0
    if not text1 or not text2:
        return 0.0
    
    # 簡易的なJaccard係数を使用
    set1 = set(text1.lower())
    set2 = set(text2.lower())
    
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    
    return intersection / union if union > 0 else 0.0


def clean_html_tags(text: str) -> str:
    """
    文字列からHTMLタグを除去します。
    
    Args:
        text: 処理する文字列
    
    Returns:
        str: HTMLタグが除去された文字列
    """
    # HTMLタグを除去
    clean_text = re.sub(r'<[^>]+>', '', text)
    # HTMLエンティティをデコード（基本的なもののみ）
    html_entities = {
        '&amp;': '&',
        '&lt;': '<',
        '&gt;': '>',
        '&quot;': '"',
        '&#39;': "'",
        '&nbsp;': ' '
    }
    
    for entity, char in html_entities.items():
        clean_text = clean_text.replace(entity, char)
    
    return clean_text


def validate_string_length(text: str, min_length: int = 0, 
                          max_length: Optional[int] = None) -> bool:
    """
    文字列の長さを検証します。
    
    Args:
        text: 検証する文字列
        min_length: 最小長
        max_length: 最大長
    
    Returns:
        bool: 検証結果
    """
    length = len(text)
    
    if length < min_length:
        return False
    
    if max_length is not None and length > max_length:
        return False
    
    return True
