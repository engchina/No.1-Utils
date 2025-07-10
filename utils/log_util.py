"""
ログ管理のためのユーティリティモジュール
ログ設定、フォーマット、ローテーション、分析などの機能を提供します。
"""

import os
import logging
import logging.handlers
import json
import gzip
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum

# ログレベルの定義
class LogLevel(Enum):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class ColoredFormatter(logging.Formatter):
    """
    カラー出力対応のログフォーマッター
    """
    
    # カラーコード
    COLORS = {
        'DEBUG': '\033[36m',      # シアン
        'INFO': '\033[32m',       # 緑
        'WARNING': '\033[33m',    # 黄
        'ERROR': '\033[31m',      # 赤
        'CRITICAL': '\033[35m',   # マゼンタ
        'RESET': '\033[0m'        # リセット
    }
    
    def format(self, record):
        # 元のフォーマットを適用
        formatted = super().format(record)
        
        # カラーコードを追加
        level_name = record.levelname
        if level_name in self.COLORS:
            color = self.COLORS[level_name]
            reset = self.COLORS['RESET']
            formatted = f"{color}{formatted}{reset}"
        
        return formatted


class JSONFormatter(logging.Formatter):
    """
    JSON形式のログフォーマッター
    """
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # 例外情報がある場合は追加
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # 追加属性があれば追加
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                          'filename', 'module', 'lineno', 'funcName', 'created',
                          'msecs', 'relativeCreated', 'thread', 'threadName',
                          'processName', 'process', 'getMessage', 'exc_info',
                          'exc_text', 'stack_info']:
                log_entry[key] = value
        
        return json.dumps(log_entry, ensure_ascii=False)


class LogManager:
    """
    ログ管理クラス
    複数のハンドラーとフォーマッターを統一的に管理します。
    """
    
    def __init__(self, name: str = 'app'):
        """
        LogManagerを初期化します。
        
        Args:
            name: ロガー名
        """
        self.name = name
        self.logger = logging.getLogger(name)
        self.handlers = {}
        self._configured = False
    
    def setup_basic_logging(self, level: Union[str, int, LogLevel] = LogLevel.INFO,
                           format_string: Optional[str] = None,
                           enable_colors: bool = True) -> None:
        """
        基本的なログ設定を行います。
        
        Args:
            level: ログレベル
            format_string: フォーマット文字列
            enable_colors: カラー出力を有効にするかどうか
        """
        # レベルの変換
        if isinstance(level, LogLevel):
            level = level.value
        elif isinstance(level, str):
            level = getattr(logging, level.upper())
        
        self.logger.setLevel(level)
        
        # 既存のハンドラーをクリア
        self.logger.handlers.clear()
        
        # デフォルトフォーマット
        if format_string is None:
            format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        # コンソールハンドラーを追加
        console_handler = logging.StreamHandler()
        
        if enable_colors:
            formatter = ColoredFormatter(format_string)
        else:
            formatter = logging.Formatter(format_string)
        
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        self.handlers['console'] = console_handler
        
        self._configured = True
        self.logger.info("基本ログ設定完了")
    
    def add_file_handler(self, file_path: Union[str, Path],
                        level: Union[str, int, LogLevel] = LogLevel.INFO,
                        format_string: Optional[str] = None,
                        encoding: str = 'utf-8') -> bool:
        """
        ファイルハンドラーを追加します。
        
        Args:
            file_path: ログファイルパス
            level: ログレベル
            format_string: フォーマット文字列
            encoding: ファイルエンコーディング
        
        Returns:
            bool: 追加成功の場合True
        """
        try:
            file_path = Path(file_path)
            
            # ディレクトリが存在しない場合は作成
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # レベルの変換
            if isinstance(level, LogLevel):
                level = level.value
            elif isinstance(level, str):
                level = getattr(logging, level.upper())
            
            # ファイルハンドラーを作成
            file_handler = logging.FileHandler(file_path, encoding=encoding)
            file_handler.setLevel(level)
            
            # フォーマッターを設定
            if format_string is None:
                format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            
            formatter = logging.Formatter(format_string)
            file_handler.setFormatter(formatter)
            
            self.logger.addHandler(file_handler)
            self.handlers[f'file_{file_path.name}'] = file_handler
            
            self.logger.info(f"ファイルハンドラー追加完了: {file_path}")
            return True
            
        except Exception as e:
            print(f"ファイルハンドラー追加エラー: {str(e)}")
            return False
    
    def add_rotating_file_handler(self, file_path: Union[str, Path],
                                 max_bytes: int = 10 * 1024 * 1024,  # 10MB
                                 backup_count: int = 5,
                                 level: Union[str, int, LogLevel] = LogLevel.INFO,
                                 format_string: Optional[str] = None) -> bool:
        """
        ローテーションファイルハンドラーを追加します。
        
        Args:
            file_path: ログファイルパス
            max_bytes: 最大ファイルサイズ（バイト）
            backup_count: バックアップファイル数
            level: ログレベル
            format_string: フォーマット文字列
        
        Returns:
            bool: 追加成功の場合True
        """
        try:
            file_path = Path(file_path)
            
            # ディレクトリが存在しない場合は作成
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # レベルの変換
            if isinstance(level, LogLevel):
                level = level.value
            elif isinstance(level, str):
                level = getattr(logging, level.upper())
            
            # ローテーションハンドラーを作成
            rotating_handler = logging.handlers.RotatingFileHandler(
                file_path, maxBytes=max_bytes, backupCount=backup_count, encoding='utf-8'
            )
            rotating_handler.setLevel(level)
            
            # フォーマッターを設定
            if format_string is None:
                format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            
            formatter = logging.Formatter(format_string)
            rotating_handler.setFormatter(formatter)
            
            self.logger.addHandler(rotating_handler)
            self.handlers[f'rotating_{file_path.name}'] = rotating_handler
            
            self.logger.info(f"ローテーションハンドラー追加完了: {file_path}")
            return True
            
        except Exception as e:
            print(f"ローテーションハンドラー追加エラー: {str(e)}")
            return False
    
    def add_json_handler(self, file_path: Union[str, Path],
                        level: Union[str, int, LogLevel] = LogLevel.INFO) -> bool:
        """
        JSON形式のファイルハンドラーを追加します。
        
        Args:
            file_path: ログファイルパス
            level: ログレベル
        
        Returns:
            bool: 追加成功の場合True
        """
        try:
            file_path = Path(file_path)
            
            # ディレクトリが存在しない場合は作成
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # レベルの変換
            if isinstance(level, LogLevel):
                level = level.value
            elif isinstance(level, str):
                level = getattr(logging, level.upper())
            
            # JSONハンドラーを作成
            json_handler = logging.FileHandler(file_path, encoding='utf-8')
            json_handler.setLevel(level)
            
            # JSONフォーマッターを設定
            json_formatter = JSONFormatter()
            json_handler.setFormatter(json_formatter)
            
            self.logger.addHandler(json_handler)
            self.handlers[f'json_{file_path.name}'] = json_handler
            
            self.logger.info(f"JSONハンドラー追加完了: {file_path}")
            return True
            
        except Exception as e:
            print(f"JSONハンドラー追加エラー: {str(e)}")
            return False
    
    def remove_handler(self, handler_name: str) -> bool:
        """
        ハンドラーを削除します。
        
        Args:
            handler_name: 削除するハンドラー名
        
        Returns:
            bool: 削除成功の場合True
        """
        try:
            if handler_name in self.handlers:
                handler = self.handlers[handler_name]
                self.logger.removeHandler(handler)
                handler.close()
                del self.handlers[handler_name]
                self.logger.info(f"ハンドラー削除完了: {handler_name}")
                return True
            else:
                self.logger.warning(f"ハンドラーが見つかりません: {handler_name}")
                return False
                
        except Exception as e:
            print(f"ハンドラー削除エラー: {str(e)}")
            return False
    
    def set_level(self, level: Union[str, int, LogLevel]) -> None:
        """
        ログレベルを設定します。
        
        Args:
            level: ログレベル
        """
        if isinstance(level, LogLevel):
            level = level.value
        elif isinstance(level, str):
            level = getattr(logging, level.upper())
        
        self.logger.setLevel(level)
        self.logger.info(f"ログレベル変更: {logging.getLevelName(level)}")
    
    def get_logger(self) -> logging.Logger:
        """
        ロガーインスタンスを取得します。
        
        Returns:
            logging.Logger: ロガーインスタンス
        """
        return self.logger


def setup_application_logging(app_name: str, log_dir: Union[str, Path] = 'logs',
                             log_level: Union[str, LogLevel] = LogLevel.INFO,
                             enable_console: bool = True,
                             enable_file: bool = True,
                             enable_json: bool = False,
                             enable_rotation: bool = True) -> LogManager:
    """
    アプリケーション用のログ設定を行います。
    
    Args:
        app_name: アプリケーション名
        log_dir: ログディレクトリ
        log_level: ログレベル
        enable_console: コンソール出力を有効にするかどうか
        enable_file: ファイル出力を有効にするかどうか
        enable_json: JSON出力を有効にするかどうか
        enable_rotation: ローテーションを有効にするかどうか
    
    Returns:
        LogManager: 設定されたログマネージャー
    """
    log_manager = LogManager(app_name)
    
    # 基本設定
    if enable_console:
        log_manager.setup_basic_logging(level=log_level, enable_colors=True)
    else:
        log_manager.logger.setLevel(log_level.value if isinstance(log_level, LogLevel) else log_level)
    
    log_dir = Path(log_dir)
    
    # ファイル出力
    if enable_file:
        if enable_rotation:
            log_manager.add_rotating_file_handler(
                log_dir / f'{app_name}.log',
                max_bytes=10 * 1024 * 1024,  # 10MB
                backup_count=5,
                level=log_level
            )
        else:
            log_manager.add_file_handler(
                log_dir / f'{app_name}.log',
                level=log_level
            )
    
    # JSON出力
    if enable_json:
        log_manager.add_json_handler(
            log_dir / f'{app_name}.json',
            level=log_level
        )
    
    return log_manager


def analyze_log_file(log_file: Union[str, Path], 
                    start_time: Optional[datetime] = None,
                    end_time: Optional[datetime] = None) -> Dict[str, Any]:
    """
    ログファイルを分析します。
    
    Args:
        log_file: 分析するログファイル
        start_time: 分析開始時刻
        end_time: 分析終了時刻
    
    Returns:
        Dict[str, Any]: 分析結果
    """
    try:
        log_file = Path(log_file)
        
        if not log_file.exists():
            return {'error': 'ログファイルが存在しません'}
        
        stats = {
            'total_lines': 0,
            'levels': {'DEBUG': 0, 'INFO': 0, 'WARNING': 0, 'ERROR': 0, 'CRITICAL': 0},
            'errors': [],
            'warnings': [],
            'time_range': {'start': None, 'end': None},
            'file_size': log_file.stat().st_size
        }
        
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                stats['total_lines'] += 1
                
                # ログレベルをカウント
                for level in stats['levels']:
                    if level in line:
                        stats['levels'][level] += 1
                        break
                
                # エラーと警告を収集
                if 'ERROR' in line:
                    stats['errors'].append(line.strip())
                elif 'WARNING' in line:
                    stats['warnings'].append(line.strip())
                
                # 時刻範囲の更新（簡易的な実装）
                if stats['time_range']['start'] is None:
                    stats['time_range']['start'] = line[:19]  # YYYY-MM-DD HH:MM:SS
                stats['time_range']['end'] = line[:19]
        
        # エラーと警告は最新の10件のみ保持
        stats['errors'] = stats['errors'][-10:]
        stats['warnings'] = stats['warnings'][-10:]
        
        return stats
        
    except Exception as e:
        return {'error': str(e)}


def compress_old_logs(log_dir: Union[str, Path], days_old: int = 7) -> Dict[str, Any]:
    """
    古いログファイルを圧縮します。
    
    Args:
        log_dir: ログディレクトリ
        days_old: この日数より古いファイルを圧縮
    
    Returns:
        Dict[str, Any]: 圧縮結果
    """
    try:
        log_dir = Path(log_dir)
        
        if not log_dir.exists():
            return {'error': 'ログディレクトリが存在しません'}
        
        cutoff_time = datetime.now() - timedelta(days=days_old)
        compressed_files = []
        total_saved_bytes = 0
        
        for log_file in log_dir.glob('*.log'):
            file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
            
            if file_time < cutoff_time:
                # 圧縮ファイル名
                compressed_file = log_file.with_suffix('.log.gz')
                
                # ファイルを圧縮
                with open(log_file, 'rb') as f_in:
                    with gzip.open(compressed_file, 'wb') as f_out:
                        f_out.writelines(f_in)
                
                # 元のファイルサイズと圧縮後のサイズを記録
                original_size = log_file.stat().st_size
                compressed_size = compressed_file.stat().st_size
                saved_bytes = original_size - compressed_size
                
                compressed_files.append({
                    'original': str(log_file),
                    'compressed': str(compressed_file),
                    'original_size': original_size,
                    'compressed_size': compressed_size,
                    'saved_bytes': saved_bytes
                })
                
                total_saved_bytes += saved_bytes
                
                # 元のファイルを削除
                log_file.unlink()
        
        result = {
            'success': True,
            'compressed_files': compressed_files,
            'total_files': len(compressed_files),
            'total_saved_bytes': total_saved_bytes,
            'total_saved_mb': round(total_saved_bytes / (1024 * 1024), 2)
        }
        
        return result
        
    except Exception as e:
        return {'error': str(e)}


# グローバルログマネージャー
_global_log_manager: Optional[LogManager] = None


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    ロガーを取得します。
    
    Args:
        name: ロガー名（Noneの場合はグローバルロガー）
    
    Returns:
        logging.Logger: ロガーインスタンス
    """
    global _global_log_manager
    
    if name is None:
        if _global_log_manager is None:
            _global_log_manager = setup_application_logging('no1-utils')
        return _global_log_manager.get_logger()
    else:
        return logging.getLogger(name)


def log_function_call(func):
    """
    関数呼び出しをログに記録するデコレーター。
    
    Args:
        func: デコレートする関数
    
    Returns:
        デコレートされた関数
    """
    def wrapper(*args, **kwargs):
        logger = get_logger()
        logger.debug(f"関数呼び出し開始: {func.__name__}")
        
        try:
            result = func(*args, **kwargs)
            logger.debug(f"関数呼び出し完了: {func.__name__}")
            return result
        except Exception as e:
            logger.error(f"関数呼び出しエラー: {func.__name__} - {str(e)}")
            raise
    
    return wrapper
