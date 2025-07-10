"""
ファイル操作のためのユーティリティモジュール
ファイルの読み書き、コピー、移動、検索などの機能を提供します。
"""

import os
import shutil
import hashlib
import mimetypes
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any, Union, Generator, Callable
from datetime import datetime

# ログ設定
logger = logging.getLogger(__name__)

# 定数定義
DEFAULT_ENCODING = 'utf-8'
CHUNK_SIZE = 8192  # ファイル読み込み時のチャンクサイズ
BACKUP_SUFFIX = '.backup'


def ensure_directory_exists(directory_path: Union[str, Path]) -> Path:
    """
    ディレクトリが存在することを確認し、存在しない場合は作成します。
    
    Args:
        directory_path: ディレクトリパス
    
    Returns:
        Path: ディレクトリのPathオブジェクト
    """
    path = Path(directory_path)
    try:
        path.mkdir(parents=True, exist_ok=True)
        logger.debug(f"ディレクトリ確認完了: {path}")
        return path
    except Exception as e:
        logger.error(f"ディレクトリ作成エラー: {str(e)}")
        raise


def safe_read_file(file_path: Union[str, Path], encoding: str = DEFAULT_ENCODING,
                   fallback_encoding: str = 'latin-1') -> str:
    """
    ファイルを安全に読み込みます。
    
    Args:
        file_path: ファイルパス
        encoding: 文字エンコーディング
        fallback_encoding: フォールバック用エンコーディング
    
    Returns:
        str: ファイルの内容
    
    Raises:
        FileNotFoundError: ファイルが見つからない場合
        IOError: ファイル読み込みエラーの場合
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"ファイルが見つかりません: {path}")
    
    try:
        with open(path, 'r', encoding=encoding) as f:
            content = f.read()
        logger.debug(f"ファイル読み込み成功: {path}")
        return content
    except UnicodeDecodeError:
        logger.warning(f"エンコーディングエラー、フォールバックを使用: {path}")
        try:
            with open(path, 'r', encoding=fallback_encoding) as f:
                return f.read()
        except Exception as e:
            logger.error(f"ファイル読み込みエラー: {str(e)}")
            raise IOError(f"ファイル読み込みに失敗しました: {path}")
    except Exception as e:
        logger.error(f"ファイル読み込みエラー: {str(e)}")
        raise


def safe_write_file(file_path: Union[str, Path], content: str,
                   encoding: str = DEFAULT_ENCODING, create_backup: bool = False) -> None:
    """
    ファイルを安全に書き込みます。
    
    Args:
        file_path: ファイルパス
        content: 書き込む内容
        encoding: 文字エンコーディング
        create_backup: バックアップを作成するかどうか
    
    Raises:
        IOError: ファイル書き込みエラーの場合
    """
    path = Path(file_path)
    
    try:
        # ディレクトリが存在しない場合は作成
        ensure_directory_exists(path.parent)
        
        # バックアップ作成
        if create_backup and path.exists():
            backup_path = path.with_suffix(path.suffix + BACKUP_SUFFIX)
            shutil.copy2(path, backup_path)
            logger.debug(f"バックアップ作成: {backup_path}")
        
        # ファイル書き込み
        with open(path, 'w', encoding=encoding) as f:
            f.write(content)
        
        logger.info(f"ファイル書き込み成功: {path}")
        
    except Exception as e:
        logger.error(f"ファイル書き込みエラー: {str(e)}")
        raise IOError(f"ファイル書き込みに失敗しました: {path}")


def copy_file_with_metadata(source: Union[str, Path], destination: Union[str, Path],
                           preserve_permissions: bool = True) -> None:
    """
    メタデータを保持してファイルをコピーします。
    
    Args:
        source: コピー元ファイルパス
        destination: コピー先ファイルパス
        preserve_permissions: 権限を保持するかどうか
    
    Raises:
        FileNotFoundError: ソースファイルが見つからない場合
        IOError: コピーエラーの場合
    """
    src_path = Path(source)
    dst_path = Path(destination)
    
    if not src_path.exists():
        raise FileNotFoundError(f"ソースファイルが見つかりません: {src_path}")
    
    try:
        # ディレクトリが存在しない場合は作成
        ensure_directory_exists(dst_path.parent)
        
        if preserve_permissions:
            shutil.copy2(src_path, dst_path)
        else:
            shutil.copy(src_path, dst_path)
        
        logger.info(f"ファイルコピー成功: {src_path} -> {dst_path}")
        
    except Exception as e:
        logger.error(f"ファイルコピーエラー: {str(e)}")
        raise IOError(f"ファイルコピーに失敗しました: {src_path} -> {dst_path}")


def move_file_safely(source: Union[str, Path], destination: Union[str, Path]) -> None:
    """
    ファイルを安全に移動します。
    
    Args:
        source: 移動元ファイルパス
        destination: 移動先ファイルパス
    
    Raises:
        FileNotFoundError: ソースファイルが見つからない場合
        IOError: 移動エラーの場合
    """
    src_path = Path(source)
    dst_path = Path(destination)
    
    if not src_path.exists():
        raise FileNotFoundError(f"ソースファイルが見つかりません: {src_path}")
    
    try:
        # ディレクトリが存在しない場合は作成
        ensure_directory_exists(dst_path.parent)
        
        shutil.move(str(src_path), str(dst_path))
        logger.info(f"ファイル移動成功: {src_path} -> {dst_path}")
        
    except Exception as e:
        logger.error(f"ファイル移動エラー: {str(e)}")
        raise IOError(f"ファイル移動に失敗しました: {src_path} -> {dst_path}")


def calculate_file_hash(file_path: Union[str, Path], algorithm: str = 'md5') -> str:
    """
    ファイルのハッシュ値を計算します。
    
    Args:
        file_path: ファイルパス
        algorithm: ハッシュアルゴリズム（md5, sha1, sha256など）
    
    Returns:
        str: ハッシュ値（16進数文字列）
    
    Raises:
        FileNotFoundError: ファイルが見つからない場合
        ValueError: サポートされていないアルゴリズムの場合
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"ファイルが見つかりません: {path}")
    
    try:
        hash_obj = hashlib.new(algorithm)
    except ValueError:
        raise ValueError(f"サポートされていないハッシュアルゴリズム: {algorithm}")
    
    try:
        with open(path, 'rb') as f:
            while chunk := f.read(CHUNK_SIZE):
                hash_obj.update(chunk)
        
        hash_value = hash_obj.hexdigest()
        logger.debug(f"ハッシュ計算完了: {path} ({algorithm}: {hash_value})")
        return hash_value
        
    except Exception as e:
        logger.error(f"ハッシュ計算エラー: {str(e)}")
        raise IOError(f"ハッシュ計算に失敗しました: {path}")


def get_file_info(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    ファイルの詳細情報を取得します。
    
    Args:
        file_path: ファイルパス
    
    Returns:
        Dict[str, Any]: ファイル情報の辞書
    
    Raises:
        FileNotFoundError: ファイルが見つからない場合
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"ファイルが見つかりません: {path}")
    
    try:
        stat = path.stat()
        mime_type, _ = mimetypes.guess_type(str(path))
        
        info = {
            'name': path.name,
            'path': str(path.absolute()),
            'size': stat.st_size,
            'size_human': format_file_size(stat.st_size),
            'created': datetime.fromtimestamp(stat.st_ctime),
            'modified': datetime.fromtimestamp(stat.st_mtime),
            'accessed': datetime.fromtimestamp(stat.st_atime),
            'is_file': path.is_file(),
            'is_directory': path.is_dir(),
            'extension': path.suffix,
            'mime_type': mime_type,
            'permissions': oct(stat.st_mode)[-3:]
        }
        
        logger.debug(f"ファイル情報取得完了: {path}")
        return info
        
    except Exception as e:
        logger.error(f"ファイル情報取得エラー: {str(e)}")
        raise


def format_file_size(size_bytes: int) -> str:
    """
    ファイルサイズを人間が読みやすい形式にフォーマットします。
    
    Args:
        size_bytes: バイト単位のファイルサイズ
    
    Returns:
        str: フォーマットされたファイルサイズ
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB", "PB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {size_names[i]}"


def find_files(directory: Union[str, Path], pattern: str = "*",
               recursive: bool = True, include_dirs: bool = False) -> List[Path]:
    """
    指定されたパターンでファイルを検索します。
    
    Args:
        directory: 検索するディレクトリ
        pattern: 検索パターン（glob形式）
        recursive: 再帰的に検索するかどうか
        include_dirs: ディレクトリも含めるかどうか
    
    Returns:
        List[Path]: 見つかったファイルのリスト
    """
    path = Path(directory)
    
    if not path.exists():
        logger.warning(f"ディレクトリが見つかりません: {path}")
        return []
    
    try:
        if recursive:
            matches = path.rglob(pattern)
        else:
            matches = path.glob(pattern)
        
        results = []
        for match in matches:
            if include_dirs or match.is_file():
                results.append(match)
        
        logger.debug(f"ファイル検索完了: {len(results)}件見つかりました")
        return results
        
    except Exception as e:
        logger.error(f"ファイル検索エラー: {str(e)}")
        return []


def clean_directory(directory: Union[str, Path], older_than_days: int = 30,
                   pattern: str = "*", dry_run: bool = True) -> List[Path]:
    """
    指定された日数より古いファイルを削除します。
    
    Args:
        directory: クリーンアップするディレクトリ
        older_than_days: この日数より古いファイルを対象とする
        pattern: 削除対象のファイルパターン
        dry_run: 実際には削除せず、対象ファイルのリストのみ返す
    
    Returns:
        List[Path]: 削除対象（または削除済み）ファイルのリスト
    """
    path = Path(directory)
    
    if not path.exists():
        logger.warning(f"ディレクトリが見つかりません: {path}")
        return []
    
    try:
        cutoff_time = datetime.now().timestamp() - (older_than_days * 24 * 60 * 60)
        files_to_delete = []
        
        for file_path in path.glob(pattern):
            if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                files_to_delete.append(file_path)
                
                if not dry_run:
                    file_path.unlink()
                    logger.info(f"ファイル削除: {file_path}")
        
        if dry_run:
            logger.info(f"ドライラン完了: {len(files_to_delete)}件のファイルが削除対象です")
        else:
            logger.info(f"クリーンアップ完了: {len(files_to_delete)}件のファイルを削除しました")
        
        return files_to_delete
        
    except Exception as e:
        logger.error(f"ディレクトリクリーンアップエラー: {str(e)}")
        return []


def read_file_in_chunks(file_path: Union[str, Path], chunk_size: int = CHUNK_SIZE) -> Generator[bytes, None, None]:
    """
    ファイルをチャンク単位で読み込みます（大きなファイル用）。
    
    Args:
        file_path: ファイルパス
        chunk_size: チャンクサイズ
    
    Yields:
        bytes: ファイルのチャンク
    
    Raises:
        FileNotFoundError: ファイルが見つからない場合
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"ファイルが見つかりません: {path}")
    
    try:
        with open(path, 'rb') as f:
            while chunk := f.read(chunk_size):
                yield chunk
        logger.debug(f"チャンク読み込み完了: {path}")
    except Exception as e:
        logger.error(f"チャンク読み込みエラー: {str(e)}")
        raise
