"""
辞書操作のためのユーティリティ関数集
"""

from typing import Any, Dict, List


def safe_get(dictionary: Dict[str, Any], key: str, default_value: Any = None) -> Any:
    """
    辞書から安全に値を取得する

    Args:
        dictionary: 値を取得する辞書
        key: 検索するキー
        default_value: キーが見つからない場合に返すデフォルト値

    Returns:
        キーに関連付けられた値、存在しない場合はdefault_value

    Note:
        この関数は辞書の組み込みgetメソッドと同等の機能を提供します
    """
    return dictionary.get(key, default_value)


def get_nested_value(dictionary: Dict[str, Any], key_path: str, separator: str = ".",
                    default_value: Any = None) -> Any:
    """
    ネストされた辞書から値を取得する

    Args:
        dictionary: 検索対象の辞書
        key_path: ドット記法でのキーパス（例: "user.profile.name"）
        separator: キーパスの区切り文字
        default_value: 値が見つからない場合のデフォルト値

    Returns:
        指定されたパスの値、見つからない場合はdefault_value
    """
    keys = key_path.split(separator)
    current_value = dictionary

    try:
        for key in keys:
            current_value = current_value[key]
        return current_value
    except (KeyError, TypeError):
        return default_value


def set_nested_value(dictionary: Dict[str, Any], key_path: str, value: Any,
                    separator: str = ".") -> None:
    """
    ネストされた辞書に値を設定する

    Args:
        dictionary: 設定対象の辞書
        key_path: ドット記法でのキーパス
        value: 設定する値
        separator: キーパスの区切り文字
    """
    keys = key_path.split(separator)
    current_dict = dictionary

    # 最後のキー以外のパスを作成
    for key in keys[:-1]:
        if key not in current_dict:
            current_dict[key] = {}
        current_dict = current_dict[key]

    # 最後のキーに値を設定
    current_dict[keys[-1]] = value


def merge_dicts(*dicts: Dict[str, Any], deep: bool = False) -> Dict[str, Any]:
    """
    複数の辞書をマージする

    Args:
        *dicts: マージする辞書のリスト
        deep: 深いマージを行うかどうか

    Returns:
        マージされた新しい辞書
    """
    if not dicts:
        return {}

    result = {}

    for dictionary in dicts:
        if not isinstance(dictionary, dict):
            continue

        if deep:
            result = _deep_merge(result, dictionary)
        else:
            result.update(dictionary)

    return result


def _deep_merge(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    2つの辞書を深くマージする内部関数

    Args:
        dict1: マージ先の辞書
        dict2: マージ元の辞書

    Returns:
        深くマージされた辞書
    """
    result = dict1.copy()

    for key, value in dict2.items():
        if (key in result and
            isinstance(result[key], dict) and
            isinstance(value, dict)):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value

    return result


def filter_dict(dictionary: Dict[str, Any], keys: List[str],
               include: bool = True) -> Dict[str, Any]:
    """
    指定されたキーで辞書をフィルタリングする

    Args:
        dictionary: フィルタリング対象の辞書
        keys: フィルタリングに使用するキーのリスト
        include: Trueの場合は指定キーのみ含める、Falseの場合は除外

    Returns:
        フィルタリングされた新しい辞書
    """
    if include:
        return {k: v for k, v in dictionary.items() if k in keys}
    else:
        return {k: v for k, v in dictionary.items() if k not in keys}


def flatten_dict(dictionary: Dict[str, Any], separator: str = ".",
                parent_key: str = "") -> Dict[str, Any]:
    """
    ネストされた辞書を平坦化する

    Args:
        dictionary: 平坦化する辞書
        separator: キーの区切り文字
        parent_key: 親キー（再帰処理用）

    Returns:
        平坦化された辞書
    """
    items = []

    for key, value in dictionary.items():
        new_key = f"{parent_key}{separator}{key}" if parent_key else key

        if isinstance(value, dict):
            items.extend(flatten_dict(value, separator, new_key).items())
        else:
            items.append((new_key, value))

    return dict(items)


def has_all_keys(dictionary: Dict[str, Any], required_keys: List[str]) -> bool:
    """
    辞書が必要なキーをすべて持っているかチェックする

    Args:
        dictionary: チェック対象の辞書
        required_keys: 必要なキーのリスト

    Returns:
        すべてのキーが存在する場合True
    """
    return all(key in dictionary for key in required_keys)


def remove_none_values(dictionary: Dict[str, Any], recursive: bool = False) -> Dict[str, Any]:
    """
    辞書からNone値を除去する

    Args:
        dictionary: 処理対象の辞書
        recursive: ネストされた辞書も再帰的に処理するかどうか

    Returns:
        None値が除去された新しい辞書
    """
    result = {}

    for key, value in dictionary.items():
        if value is None:
            continue

        if recursive and isinstance(value, dict):
            cleaned_value = remove_none_values(value, recursive=True)
            if cleaned_value:  # 空の辞書は除外
                result[key] = cleaned_value
        else:
            result[key] = value

    return result