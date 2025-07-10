"""
JSON操作のためのユーティリティモジュール
JSONデータの読み書き、変換、検証などの機能を提供します。
"""

import json
import logging
from typing import Any, Dict, List, Union, Optional
from pathlib import Path

# ログ設定
logger = logging.getLogger(__name__)


def dumps_json(data: Any, ensure_ascii: bool = False, indent: int = 2, 
               sort_keys: bool = False, separators: Optional[tuple] = None) -> str:
    """
    PythonオブジェクトをJSON文字列に変換します。
    
    Args:
        data: JSON文字列に変換するPythonオブジェクト
        ensure_ascii: ASCII文字のみを使用するかどうか（デフォルト: False）
        indent: インデントのスペース数（デフォルト: 2）
        sort_keys: キーをソートするかどうか（デフォルト: False）
        separators: セパレータのタプル（デフォルト: None）
    
    Returns:
        str: JSON文字列
    
    Raises:
        TypeError: シリアライズできないオブジェクトの場合
        ValueError: 無効なデータの場合
    """
    try:
        logger.debug(f"JSONエンコード開始: データタイプ={type(data).__name__}")
        
        result = json.dumps(
            data,
            ensure_ascii=ensure_ascii,
            indent=indent,
            sort_keys=sort_keys,
            separators=separators
        )
        
        logger.debug(f"JSONエンコード成功: 文字列長={len(result)}")
        return result
        
    except (TypeError, ValueError) as e:
        logger.error(f"JSONエンコードエラー: {str(e)}")
        raise


def loads_json(json_string: str) -> Any:
    """
    JSON文字列をPythonオブジェクトに変換します。
    
    Args:
        json_string: パースするJSON文字列
    
    Returns:
        Any: パースされたPythonオブジェクト
    
    Raises:
        json.JSONDecodeError: 無効なJSON文字列の場合
        TypeError: 入力が文字列でない場合
    """
    try:
        logger.debug(f"JSONデコード開始: 文字列長={len(json_string)}")
        
        if not isinstance(json_string, str):
            raise TypeError("入力は文字列である必要があります")
        
        result = json.loads(json_string)
        logger.debug(f"JSONデコード成功: 結果タイプ={type(result).__name__}")
        return result
        
    except json.JSONDecodeError as e:
        logger.error(f"JSONデコードエラー: {str(e)}")
        raise
    except TypeError as e:
        logger.error(f"型エラー: {str(e)}")
        raise


def dump_json(data: Any, file_path: Union[str, Path], ensure_ascii: bool = False,
              indent: int = 2, sort_keys: bool = False, encoding: str = 'utf-8') -> None:
    """
    PythonオブジェクトをJSONファイルに書き込みます。
    
    Args:
        data: JSONファイルに書き込むPythonオブジェクト
        file_path: 出力ファイルのパス
        ensure_ascii: ASCII文字のみを使用するかどうか（デフォルト: False）
        indent: インデントのスペース数（デフォルト: 2）
        sort_keys: キーをソートするかどうか（デフォルト: False）
        encoding: ファイルエンコーディング（デフォルト: 'utf-8'）
    
    Raises:
        TypeError: シリアライズできないオブジェクトの場合
        IOError: ファイル書き込みエラーの場合
    """
    try:
        file_path = Path(file_path)
        logger.debug(f"JSONファイル書き込み開始: パス={file_path}")
        
        # ディレクトリが存在しない場合は作成
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding=encoding) as f:
            json.dump(
                data,
                f,
                ensure_ascii=ensure_ascii,
                indent=indent,
                sort_keys=sort_keys
            )
        
        logger.info(f"JSONファイル書き込み成功: {file_path}")
        
    except (TypeError, ValueError) as e:
        logger.error(f"JSONエンコードエラー: {str(e)}")
        raise
    except IOError as e:
        logger.error(f"ファイル書き込みエラー: {str(e)}")
        raise


def load_json(file_path: Union[str, Path], encoding: str = 'utf-8') -> Any:
    """
    JSONファイルを読み込んでPythonオブジェクトに変換します。
    
    Args:
        file_path: 読み込むJSONファイルのパス
        encoding: ファイルエンコーディング（デフォルト: 'utf-8'）
    
    Returns:
        Any: パースされたPythonオブジェクト
    
    Raises:
        FileNotFoundError: ファイルが見つからない場合
        json.JSONDecodeError: 無効なJSONファイルの場合
        IOError: ファイル読み込みエラーの場合
    """
    try:
        file_path = Path(file_path)
        logger.debug(f"JSONファイル読み込み開始: パス={file_path}")
        
        if not file_path.exists():
            raise FileNotFoundError(f"ファイルが見つかりません: {file_path}")
        
        with open(file_path, 'r', encoding=encoding) as f:
            result = json.load(f)
        
        logger.info(f"JSONファイル読み込み成功: {file_path}")
        return result
        
    except FileNotFoundError as e:
        logger.error(f"ファイル未発見エラー: {str(e)}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"JSONデコードエラー: {str(e)}")
        raise
    except IOError as e:
        logger.error(f"ファイル読み込みエラー: {str(e)}")
        raise


def is_valid_json(json_string: str) -> bool:
    """
    文字列が有効なJSONかどうかを検証します。
    
    Args:
        json_string: 検証するJSON文字列
    
    Returns:
        bool: 有効なJSONの場合True、そうでなければFalse
    """
    try:
        json.loads(json_string)
        logger.debug("JSON検証成功")
        return True
    except (json.JSONDecodeError, TypeError):
        logger.debug("JSON検証失敗")
        return False


def pretty_print_json(data: Any, indent: int = 2) -> str:
    """
    PythonオブジェクトをきれいにフォーマットされたJSON文字列に変換します。
    
    Args:
        data: フォーマットするPythonオブジェクト
        indent: インデントのスペース数（デフォルト: 2）
    
    Returns:
        str: フォーマットされたJSON文字列
    """
    try:
        result = json.dumps(data, ensure_ascii=False, indent=indent, sort_keys=True)
        logger.debug("JSON整形成功")
        return result
    except (TypeError, ValueError) as e:
        logger.error(f"JSON整形エラー: {str(e)}")
        raise


def merge_json_files(file_paths: List[Union[str, Path]], output_path: Union[str, Path]) -> None:
    """
    複数のJSONファイルを結合して新しいファイルに出力します。
    
    Args:
        file_paths: 結合するJSONファイルのパスリスト
        output_path: 出力ファイルのパス
    
    Raises:
        FileNotFoundError: ファイルが見つからない場合
        json.JSONDecodeError: 無効なJSONファイルの場合
    """
    try:
        merged_data = {}
        
        for file_path in file_paths:
            logger.debug(f"ファイル結合処理中: {file_path}")
            data = load_json(file_path)
            
            if isinstance(data, dict):
                merged_data.update(data)
            else:
                logger.warning(f"辞書型でないデータをスキップ: {file_path}")
        
        dump_json(merged_data, output_path)
        logger.info(f"JSONファイル結合完了: 出力先={output_path}")
        
    except Exception as e:
        logger.error(f"JSONファイル結合エラー: {str(e)}")
        raise


def validate_json_schema(data: Any, required_keys: List[str]) -> bool:
    """
    JSONデータが必要なキーを持っているかを検証します。
    
    Args:
        data: 検証するデータ
        required_keys: 必須キーのリスト
    
    Returns:
        bool: すべての必須キーが存在する場合True
    """
    try:
        if not isinstance(data, dict):
            logger.debug("データが辞書型ではありません")
            return False
        
        missing_keys = [key for key in required_keys if key not in data]
        
        if missing_keys:
            logger.debug(f"不足キー: {missing_keys}")
            return False
        
        logger.debug("スキーマ検証成功")
        return True
        
    except Exception as e:
        logger.error(f"スキーマ検証エラー: {str(e)}")
        return False
