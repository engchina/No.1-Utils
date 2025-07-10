"""
キャッシュ操作のためのユーティリティモジュール
メモリキャッシュ、ファイルキャッシュ、TTL管理などの機能を提供します。
"""

import os
import pickle
import json
import hashlib
import threading
import logging
from typing import Any, Optional, Dict, Callable, Union, List
from datetime import datetime, timedelta
from pathlib import Path
from functools import wraps
import time

# ログ設定
logger = logging.getLogger(__name__)


class MemoryCache:
    """
    メモリベースのキャッシュクラス
    TTL（Time To Live）とLRU（Least Recently Used）をサポートします。
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: Optional[int] = None):
        """
        MemoryCacheを初期化します。
        
        Args:
            max_size: 最大キャッシュサイズ
            default_ttl: デフォルトTTL（秒）
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._access_times: Dict[str, float] = {}
        self._lock = threading.RLock()
        
        logger.debug(f"メモリキャッシュ初期化: max_size={max_size}, default_ttl={default_ttl}")
    
    def _is_expired(self, key: str) -> bool:
        """キーが期限切れかどうかをチェックします。"""
        if key not in self._cache:
            return True
        
        entry = self._cache[key]
        if entry.get('expires_at') is None:
            return False
        
        return datetime.now() > entry['expires_at']
    
    def _cleanup_expired(self) -> None:
        """期限切れのエントリを削除します。"""
        expired_keys = [key for key in self._cache.keys() if self._is_expired(key)]
        for key in expired_keys:
            self._remove_key(key)
    
    def _remove_key(self, key: str) -> None:
        """キーを削除します。"""
        if key in self._cache:
            del self._cache[key]
        if key in self._access_times:
            del self._access_times[key]
    
    def _evict_lru(self) -> None:
        """LRUアルゴリズムで最も古いエントリを削除します。"""
        if not self._access_times:
            return
        
        lru_key = min(self._access_times.keys(), key=lambda k: self._access_times[k])
        self._remove_key(lru_key)
        logger.debug(f"LRU削除: {lru_key}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        キャッシュから値を取得します。
        
        Args:
            key: キー
            default: デフォルト値
        
        Returns:
            Any: キャッシュされた値またはデフォルト値
        """
        with self._lock:
            if self._is_expired(key):
                self._remove_key(key)
                return default
            
            if key in self._cache:
                self._access_times[key] = time.time()
                value = self._cache[key]['value']
                logger.debug(f"キャッシュヒット: {key}")
                return value
            
            logger.debug(f"キャッシュミス: {key}")
            return default
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        キャッシュに値を設定します。
        
        Args:
            key: キー
            value: 値
            ttl: TTL（秒）
        """
        with self._lock:
            # 期限切れエントリのクリーンアップ
            self._cleanup_expired()
            
            # サイズ制限チェック
            if len(self._cache) >= self.max_size and key not in self._cache:
                self._evict_lru()
            
            # TTLの設定
            expires_at = None
            if ttl is not None:
                expires_at = datetime.now() + timedelta(seconds=ttl)
            elif self.default_ttl is not None:
                expires_at = datetime.now() + timedelta(seconds=self.default_ttl)
            
            # エントリの設定
            self._cache[key] = {
                'value': value,
                'expires_at': expires_at,
                'created_at': datetime.now()
            }
            self._access_times[key] = time.time()
            
            logger.debug(f"キャッシュ設定: {key}, TTL={ttl}")
    
    def delete(self, key: str) -> bool:
        """
        キャッシュからキーを削除します。
        
        Args:
            key: 削除するキー
        
        Returns:
            bool: 削除成功の場合True
        """
        with self._lock:
            if key in self._cache:
                self._remove_key(key)
                logger.debug(f"キャッシュ削除: {key}")
                return True
            return False
    
    def clear(self) -> None:
        """キャッシュをクリアします。"""
        with self._lock:
            self._cache.clear()
            self._access_times.clear()
            logger.debug("キャッシュクリア完了")
    
    def exists(self, key: str) -> bool:
        """
        キーが存在するかチェックします。
        
        Args:
            key: チェックするキー
        
        Returns:
            bool: キーが存在し、期限切れでない場合True
        """
        with self._lock:
            return not self._is_expired(key) and key in self._cache
    
    def keys(self) -> List[str]:
        """
        有効なキーのリストを取得します。
        
        Returns:
            List[str]: キーのリスト
        """
        with self._lock:
            self._cleanup_expired()
            return list(self._cache.keys())
    
    def size(self) -> int:
        """
        キャッシュサイズを取得します。
        
        Returns:
            int: キャッシュサイズ
        """
        with self._lock:
            self._cleanup_expired()
            return len(self._cache)
    
    def stats(self) -> Dict[str, Any]:
        """
        キャッシュ統計を取得します。
        
        Returns:
            Dict[str, Any]: 統計情報
        """
        with self._lock:
            self._cleanup_expired()
            
            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'default_ttl': self.default_ttl,
                'keys': list(self._cache.keys())
            }


class FileCache:
    """
    ファイルベースのキャッシュクラス
    """
    
    def __init__(self, cache_dir: Union[str, Path] = '.cache', 
                 default_ttl: Optional[int] = None,
                 serializer: str = 'pickle'):
        """
        FileCacheを初期化します。
        
        Args:
            cache_dir: キャッシュディレクトリ
            default_ttl: デフォルトTTL（秒）
            serializer: シリアライザー（'pickle', 'json'）
        """
        self.cache_dir = Path(cache_dir)
        self.default_ttl = default_ttl
        self.serializer = serializer
        self._lock = threading.RLock()
        
        # キャッシュディレクトリを作成
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        logger.debug(f"ファイルキャッシュ初期化: dir={cache_dir}, ttl={default_ttl}")
    
    def _get_cache_path(self, key: str) -> Path:
        """キーからキャッシュファイルパスを生成します。"""
        # キーをハッシュ化してファイル名として使用
        key_hash = hashlib.md5(key.encode('utf-8')).hexdigest()
        return self.cache_dir / f"{key_hash}.cache"
    
    def _get_meta_path(self, key: str) -> Path:
        """キーからメタデータファイルパスを生成します。"""
        key_hash = hashlib.md5(key.encode('utf-8')).hexdigest()
        return self.cache_dir / f"{key_hash}.meta"
    
    def _is_expired(self, key: str) -> bool:
        """キーが期限切れかどうかをチェックします。"""
        meta_path = self._get_meta_path(key)
        
        if not meta_path.exists():
            return True
        
        try:
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            
            expires_at = meta.get('expires_at')
            if expires_at is None:
                return False
            
            expires_datetime = datetime.fromisoformat(expires_at)
            return datetime.now() > expires_datetime
            
        except Exception:
            return True
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        キャッシュから値を取得します。
        
        Args:
            key: キー
            default: デフォルト値
        
        Returns:
            Any: キャッシュされた値またはデフォルト値
        """
        with self._lock:
            if self._is_expired(key):
                self.delete(key)
                return default
            
            cache_path = self._get_cache_path(key)
            
            if not cache_path.exists():
                logger.debug(f"ファイルキャッシュミス: {key}")
                return default
            
            try:
                with open(cache_path, 'rb') as f:
                    if self.serializer == 'pickle':
                        value = pickle.load(f)
                    elif self.serializer == 'json':
                        value = json.load(f)
                    else:
                        raise ValueError(f"サポートされていないシリアライザー: {self.serializer}")
                
                logger.debug(f"ファイルキャッシュヒット: {key}")
                return value
                
            except Exception as e:
                logger.error(f"ファイルキャッシュ読み込みエラー: {key} - {str(e)}")
                self.delete(key)
                return default
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        キャッシュに値を設定します。
        
        Args:
            key: キー
            value: 値
            ttl: TTL（秒）
        
        Returns:
            bool: 設定成功の場合True
        """
        with self._lock:
            try:
                cache_path = self._get_cache_path(key)
                meta_path = self._get_meta_path(key)
                
                # 値をシリアライズして保存
                with open(cache_path, 'wb') as f:
                    if self.serializer == 'pickle':
                        pickle.dump(value, f)
                    elif self.serializer == 'json':
                        json.dump(value, f, ensure_ascii=False, indent=2)
                    else:
                        raise ValueError(f"サポートされていないシリアライザー: {self.serializer}")
                
                # メタデータを保存
                expires_at = None
                if ttl is not None:
                    expires_at = (datetime.now() + timedelta(seconds=ttl)).isoformat()
                elif self.default_ttl is not None:
                    expires_at = (datetime.now() + timedelta(seconds=self.default_ttl)).isoformat()
                
                meta = {
                    'key': key,
                    'created_at': datetime.now().isoformat(),
                    'expires_at': expires_at,
                    'serializer': self.serializer
                }
                
                with open(meta_path, 'w', encoding='utf-8') as f:
                    json.dump(meta, f, ensure_ascii=False, indent=2)
                
                logger.debug(f"ファイルキャッシュ設定: {key}, TTL={ttl}")
                return True
                
            except Exception as e:
                logger.error(f"ファイルキャッシュ設定エラー: {key} - {str(e)}")
                return False
    
    def delete(self, key: str) -> bool:
        """
        キャッシュからキーを削除します。
        
        Args:
            key: 削除するキー
        
        Returns:
            bool: 削除成功の場合True
        """
        with self._lock:
            cache_path = self._get_cache_path(key)
            meta_path = self._get_meta_path(key)
            
            deleted = False
            
            if cache_path.exists():
                cache_path.unlink()
                deleted = True
            
            if meta_path.exists():
                meta_path.unlink()
                deleted = True
            
            if deleted:
                logger.debug(f"ファイルキャッシュ削除: {key}")
            
            return deleted
    
    def clear(self) -> int:
        """
        キャッシュをクリアします。
        
        Returns:
            int: 削除されたファイル数
        """
        with self._lock:
            deleted_count = 0
            
            for file_path in self.cache_dir.glob('*.cache'):
                file_path.unlink()
                deleted_count += 1
            
            for file_path in self.cache_dir.glob('*.meta'):
                file_path.unlink()
                deleted_count += 1
            
            logger.debug(f"ファイルキャッシュクリア完了: {deleted_count}ファイル削除")
            return deleted_count
    
    def cleanup_expired(self) -> int:
        """
        期限切れのキャッシュを削除します。
        
        Returns:
            int: 削除されたキー数
        """
        with self._lock:
            deleted_count = 0
            
            for meta_path in self.cache_dir.glob('*.meta'):
                try:
                    with open(meta_path, 'r', encoding='utf-8') as f:
                        meta = json.load(f)
                    
                    key = meta.get('key', '')
                    if self._is_expired(key):
                        self.delete(key)
                        deleted_count += 1
                        
                except Exception:
                    # 破損したメタファイルも削除
                    meta_path.unlink()
                    cache_path = meta_path.with_suffix('.cache')
                    if cache_path.exists():
                        cache_path.unlink()
                    deleted_count += 1
            
            logger.debug(f"期限切れキャッシュクリーンアップ完了: {deleted_count}キー削除")
            return deleted_count


# グローバルキャッシュインスタンス
_memory_cache: Optional[MemoryCache] = None
_file_cache: Optional[FileCache] = None


def get_memory_cache() -> MemoryCache:
    """グローバルメモリキャッシュを取得します。"""
    global _memory_cache
    if _memory_cache is None:
        _memory_cache = MemoryCache()
    return _memory_cache


def get_file_cache() -> FileCache:
    """グローバルファイルキャッシュを取得します。"""
    global _file_cache
    if _file_cache is None:
        _file_cache = FileCache()
    return _file_cache


def cache_result(ttl: Optional[int] = None, cache_type: str = 'memory'):
    """
    関数の結果をキャッシュするデコレーター。
    
    Args:
        ttl: TTL（秒）
        cache_type: キャッシュタイプ（'memory', 'file'）
    
    Returns:
        デコレートされた関数
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # キャッシュキーを生成
            key_data = f"{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
            cache_key = hashlib.md5(key_data.encode('utf-8')).hexdigest()
            
            # キャッシュから取得を試行
            if cache_type == 'memory':
                cache = get_memory_cache()
            elif cache_type == 'file':
                cache = get_file_cache()
            else:
                raise ValueError(f"サポートされていないキャッシュタイプ: {cache_type}")
            
            result = cache.get(cache_key)
            if result is not None:
                logger.debug(f"関数結果キャッシュヒット: {func.__name__}")
                return result
            
            # 関数を実行してキャッシュに保存
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            logger.debug(f"関数結果キャッシュ保存: {func.__name__}")
            
            return result
        
        return wrapper
    return decorator


def memoize(ttl: Optional[int] = None):
    """
    関数の結果をメモ化するデコレーター（メモリキャッシュ使用）。
    
    Args:
        ttl: TTL（秒）
    
    Returns:
        デコレートされた関数
    """
    return cache_result(ttl=ttl, cache_type='memory')


def clear_all_caches() -> Dict[str, int]:
    """
    全てのキャッシュをクリアします。
    
    Returns:
        Dict[str, int]: クリア結果
    """
    result = {}
    
    # メモリキャッシュをクリア
    memory_cache = get_memory_cache()
    memory_size = memory_cache.size()
    memory_cache.clear()
    result['memory_cleared'] = memory_size
    
    # ファイルキャッシュをクリア
    file_cache = get_file_cache()
    file_cleared = file_cache.clear()
    result['file_cleared'] = file_cleared // 2  # .cache と .meta ファイルがあるため
    
    logger.info(f"全キャッシュクリア完了: {result}")
    return result
