"""
設定ファイル管理のためのユーティリティモジュール
JSON、YAML、INI、TOML形式の設定ファイルの読み書き、管理機能を提供します。
"""

import os
import json
import configparser
import logging
from typing import Dict, Any, Optional, Union, List
from pathlib import Path

# ログ設定
logger = logging.getLogger(__name__)

# オプショナルな依存関係のインポート
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    logger.warning("PyYAMLがインストールされていません。YAML機能は無効です。")

try:
    import toml
    TOML_AVAILABLE = True
except ImportError:
    TOML_AVAILABLE = False
    logger.warning("tomlがインストールされていません。TOML機能は無効です。")


class ConfigManager:
    """
    設定ファイル管理クラス
    複数の形式の設定ファイルを統一的に管理します。
    """
    
    def __init__(self, config_path: Union[str, Path], auto_create: bool = True):
        """
        ConfigManagerを初期化します。
        
        Args:
            config_path: 設定ファイルのパス
            auto_create: ファイルが存在しない場合に自動作成するかどうか
        """
        self.config_path = Path(config_path)
        self.auto_create = auto_create
        self._config_data = {}
        self._file_format = self._detect_format()
        
        if self.config_path.exists():
            self.load()
        elif auto_create:
            self._create_default_config()
    
    def _detect_format(self) -> str:
        """ファイル拡張子から設定ファイル形式を検出します。"""
        suffix = self.config_path.suffix.lower()
        
        if suffix == '.json':
            return 'json'
        elif suffix in ['.yml', '.yaml']:
            return 'yaml'
        elif suffix in ['.ini', '.cfg']:
            return 'ini'
        elif suffix == '.toml':
            return 'toml'
        else:
            logger.warning(f"未知のファイル形式: {suffix}、JSONとして扱います")
            return 'json'
    
    def _create_default_config(self) -> None:
        """デフォルト設定ファイルを作成します。"""
        try:
            # ディレクトリが存在しない場合は作成
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # デフォルト設定
            default_config = {
                'app': {
                    'name': 'No.1-Utils Application',
                    'version': '1.0.0',
                    'debug': False
                },
                'logging': {
                    'level': 'INFO',
                    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                }
            }
            
            self._config_data = default_config
            self.save()
            logger.info(f"デフォルト設定ファイル作成: {self.config_path}")
            
        except Exception as e:
            logger.error(f"デフォルト設定ファイル作成エラー: {str(e)}")
    
    def load(self) -> bool:
        """設定ファイルを読み込みます。"""
        try:
            if not self.config_path.exists():
                logger.warning(f"設定ファイルが存在しません: {self.config_path}")
                return False
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                if self._file_format == 'json':
                    self._config_data = json.load(f)
                elif self._file_format == 'yaml':
                    if not YAML_AVAILABLE:
                        raise ImportError("PyYAMLがインストールされていません")
                    self._config_data = yaml.safe_load(f)
                elif self._file_format == 'ini':
                    config = configparser.ConfigParser()
                    config.read(self.config_path, encoding='utf-8')
                    self._config_data = {section: dict(config[section]) for section in config.sections()}
                elif self._file_format == 'toml':
                    if not TOML_AVAILABLE:
                        raise ImportError("tomlがインストールされていません")
                    self._config_data = toml.load(f)
            
            logger.debug(f"設定ファイル読み込み完了: {self.config_path}")
            return True
            
        except Exception as e:
            logger.error(f"設定ファイル読み込みエラー: {str(e)}")
            return False
    
    def save(self) -> bool:
        """設定ファイルを保存します。"""
        try:
            # ディレクトリが存在しない場合は作成
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                if self._file_format == 'json':
                    json.dump(self._config_data, f, indent=2, ensure_ascii=False)
                elif self._file_format == 'yaml':
                    if not YAML_AVAILABLE:
                        raise ImportError("PyYAMLがインストールされていません")
                    yaml.dump(self._config_data, f, default_flow_style=False, allow_unicode=True)
                elif self._file_format == 'ini':
                    config = configparser.ConfigParser()
                    for section, values in self._config_data.items():
                        config[section] = values
                    config.write(f)
                elif self._file_format == 'toml':
                    if not TOML_AVAILABLE:
                        raise ImportError("tomlがインストールされていません")
                    toml.dump(self._config_data, f)
            
            logger.debug(f"設定ファイル保存完了: {self.config_path}")
            return True
            
        except Exception as e:
            logger.error(f"設定ファイル保存エラー: {str(e)}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        設定値を取得します（ドット記法対応）。
        
        Args:
            key: 設定キー（例: "app.name"）
            default: デフォルト値
        
        Returns:
            Any: 設定値
        """
        try:
            keys = key.split('.')
            value = self._config_data
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            
            return value
            
        except Exception as e:
            logger.error(f"設定値取得エラー: {key} - {str(e)}")
            return default
    
    def set(self, key: str, value: Any) -> bool:
        """
        設定値を設定します（ドット記法対応）。
        
        Args:
            key: 設定キー（例: "app.name"）
            value: 設定値
        
        Returns:
            bool: 設定成功の場合True
        """
        try:
            keys = key.split('.')
            current = self._config_data
            
            # 最後のキー以外のパスを作成
            for k in keys[:-1]:
                if k not in current:
                    current[k] = {}
                current = current[k]
            
            # 最後のキーに値を設定
            current[keys[-1]] = value
            
            logger.debug(f"設定値設定完了: {key} = {value}")
            return True
            
        except Exception as e:
            logger.error(f"設定値設定エラー: {key} - {str(e)}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        設定値を削除します。
        
        Args:
            key: 削除する設定キー
        
        Returns:
            bool: 削除成功の場合True
        """
        try:
            keys = key.split('.')
            current = self._config_data
            
            # 最後のキー以外のパスを辿る
            for k in keys[:-1]:
                if isinstance(current, dict) and k in current:
                    current = current[k]
                else:
                    return False
            
            # 最後のキーを削除
            if isinstance(current, dict) and keys[-1] in current:
                del current[keys[-1]]
                logger.debug(f"設定値削除完了: {key}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"設定値削除エラー: {key} - {str(e)}")
            return False
    
    def has(self, key: str) -> bool:
        """
        設定キーが存在するかチェックします。
        
        Args:
            key: チェックする設定キー
        
        Returns:
            bool: キーが存在する場合True
        """
        return self.get(key, object()) is not object()
    
    def get_all(self) -> Dict[str, Any]:
        """
        全ての設定を取得します。
        
        Returns:
            Dict[str, Any]: 全設定の辞書
        """
        return self._config_data.copy()
    
    def update(self, config_dict: Dict[str, Any]) -> bool:
        """
        設定を一括更新します。
        
        Args:
            config_dict: 更新する設定の辞書
        
        Returns:
            bool: 更新成功の場合True
        """
        try:
            self._config_data.update(config_dict)
            logger.debug("設定一括更新完了")
            return True
        except Exception as e:
            logger.error(f"設定一括更新エラー: {str(e)}")
            return False
    
    def backup(self, backup_path: Optional[Union[str, Path]] = None) -> bool:
        """
        設定ファイルをバックアップします。
        
        Args:
            backup_path: バックアップ先パス（Noneの場合は自動生成）
        
        Returns:
            bool: バックアップ成功の場合True
        """
        try:
            if backup_path is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_path = self.config_path.with_suffix(f'.{timestamp}.backup')
            else:
                backup_path = Path(backup_path)
            
            # 現在の設定を一時保存
            original_path = self.config_path
            self.config_path = backup_path
            success = self.save()
            self.config_path = original_path
            
            if success:
                logger.info(f"設定ファイルバックアップ完了: {backup_path}")
            
            return success
            
        except Exception as e:
            logger.error(f"設定ファイルバックアップエラー: {str(e)}")
            return False


def load_config(config_path: Union[str, Path], format_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    設定ファイルを読み込みます（シンプル版）。
    
    Args:
        config_path: 設定ファイルのパス
        format_type: ファイル形式（'json', 'yaml', 'ini', 'toml'）
    
    Returns:
        Optional[Dict[str, Any]]: 設定データ、読み込み失敗時はNone
    """
    try:
        config_path = Path(config_path)
        
        if not config_path.exists():
            logger.warning(f"設定ファイルが存在しません: {config_path}")
            return None
        
        # 形式の自動検出
        if format_type is None:
            suffix = config_path.suffix.lower()
            if suffix == '.json':
                format_type = 'json'
            elif suffix in ['.yml', '.yaml']:
                format_type = 'yaml'
            elif suffix in ['.ini', '.cfg']:
                format_type = 'ini'
            elif suffix == '.toml':
                format_type = 'toml'
            else:
                format_type = 'json'
        
        with open(config_path, 'r', encoding='utf-8') as f:
            if format_type == 'json':
                return json.load(f)
            elif format_type == 'yaml':
                if not YAML_AVAILABLE:
                    raise ImportError("PyYAMLがインストールされていません")
                return yaml.safe_load(f)
            elif format_type == 'ini':
                config = configparser.ConfigParser()
                config.read(config_path, encoding='utf-8')
                return {section: dict(config[section]) for section in config.sections()}
            elif format_type == 'toml':
                if not TOML_AVAILABLE:
                    raise ImportError("tomlがインストールされていません")
                return toml.load(f)
        
        logger.debug(f"設定ファイル読み込み完了: {config_path}")
        
    except Exception as e:
        logger.error(f"設定ファイル読み込みエラー: {config_path} - {str(e)}")
        return None


def save_config(config_data: Dict[str, Any], config_path: Union[str, Path],
               format_type: Optional[str] = None) -> bool:
    """
    設定ファイルを保存します（シンプル版）。
    
    Args:
        config_data: 保存する設定データ
        config_path: 保存先パス
        format_type: ファイル形式
    
    Returns:
        bool: 保存成功の場合True
    """
    try:
        config_path = Path(config_path)
        
        # ディレクトリが存在しない場合は作成
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 形式の自動検出
        if format_type is None:
            suffix = config_path.suffix.lower()
            if suffix == '.json':
                format_type = 'json'
            elif suffix in ['.yml', '.yaml']:
                format_type = 'yaml'
            elif suffix in ['.ini', '.cfg']:
                format_type = 'ini'
            elif suffix == '.toml':
                format_type = 'toml'
            else:
                format_type = 'json'
        
        with open(config_path, 'w', encoding='utf-8') as f:
            if format_type == 'json':
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            elif format_type == 'yaml':
                if not YAML_AVAILABLE:
                    raise ImportError("PyYAMLがインストールされていません")
                yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
            elif format_type == 'ini':
                config = configparser.ConfigParser()
                for section, values in config_data.items():
                    config[section] = values
                config.write(f)
            elif format_type == 'toml':
                if not TOML_AVAILABLE:
                    raise ImportError("tomlがインストールされていません")
                toml.dump(config_data, f)
        
        logger.debug(f"設定ファイル保存完了: {config_path}")
        return True
        
    except Exception as e:
        logger.error(f"設定ファイル保存エラー: {config_path} - {str(e)}")
        return False


def merge_configs(*config_dicts: Dict[str, Any]) -> Dict[str, Any]:
    """
    複数の設定を深くマージします。
    
    Args:
        *config_dicts: マージする設定辞書
    
    Returns:
        Dict[str, Any]: マージされた設定
    """
    def deep_merge(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
        result = dict1.copy()
        
        for key, value in dict2.items():
            if (key in result and
                isinstance(result[key], dict) and
                isinstance(value, dict)):
                result[key] = deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    if not config_dicts:
        return {}
    
    result = config_dicts[0].copy()
    for config_dict in config_dicts[1:]:
        result = deep_merge(result, config_dict)
    
    logger.debug(f"設定マージ完了: {len(config_dicts)}個の設定をマージ")
    return result


def get_config_template(template_type: str = 'basic') -> Dict[str, Any]:
    """
    設定ファイルのテンプレートを取得します。
    
    Args:
        template_type: テンプレートタイプ（'basic', 'web_app', 'database'）
    
    Returns:
        Dict[str, Any]: 設定テンプレート
    """
    templates = {
        'basic': {
            'app': {
                'name': 'My Application',
                'version': '1.0.0',
                'debug': False,
                'environment': 'production'
            },
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'file': 'app.log'
            }
        },
        'web_app': {
            'app': {
                'name': 'Web Application',
                'version': '1.0.0',
                'debug': False,
                'secret_key': 'your-secret-key-here'
            },
            'server': {
                'host': '0.0.0.0',
                'port': 8000,
                'workers': 4
            },
            'database': {
                'url': 'sqlite:///app.db',
                'pool_size': 10,
                'echo': False
            }
        },
        'database': {
            'database': {
                'host': 'localhost',
                'port': 5432,
                'name': 'mydb',
                'user': 'user',
                'password': 'password',
                'pool_size': 10,
                'timeout': 30
            },
            'redis': {
                'host': 'localhost',
                'port': 6379,
                'db': 0,
                'password': None
            }
        }
    }
    
    return templates.get(template_type, templates['basic'])
