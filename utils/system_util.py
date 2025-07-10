"""
システム情報・操作のためのユーティリティモジュール
システム情報取得、プロセス管理、環境変数操作などの機能を提供します。
"""

import os
import sys
import platform
import psutil
import subprocess
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from pathlib import Path

# ログ設定
logger = logging.getLogger(__name__)

# 定数定義
BYTES_TO_GB = 1024 ** 3
BYTES_TO_MB = 1024 ** 2


def get_system_info() -> Dict[str, Any]:
    """
    システム情報を取得します。
    
    Returns:
        Dict[str, Any]: システム情報の辞書
    """
    try:
        info = {
            'platform': {
                'system': platform.system(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine(),
                'processor': platform.processor(),
                'architecture': platform.architecture(),
                'node': platform.node()
            },
            'python': {
                'version': sys.version,
                'version_info': sys.version_info,
                'executable': sys.executable,
                'path': sys.path[:3]  # 最初の3つのパスのみ
            },
            'environment': {
                'user': os.getenv('USER') or os.getenv('USERNAME'),
                'home': os.path.expanduser('~'),
                'cwd': os.getcwd(),
                'path_separator': os.pathsep,
                'line_separator': os.linesep
            }
        }
        
        logger.debug("システム情報取得完了")
        return info
        
    except Exception as e:
        logger.error(f"システム情報取得エラー: {str(e)}")
        return {'error': str(e)}


def get_cpu_info() -> Dict[str, Any]:
    """
    CPU情報を取得します。
    
    Returns:
        Dict[str, Any]: CPU情報の辞書
    """
    try:
        cpu_info = {
            'physical_cores': psutil.cpu_count(logical=False),
            'logical_cores': psutil.cpu_count(logical=True),
            'current_frequency': psutil.cpu_freq().current if psutil.cpu_freq() else None,
            'max_frequency': psutil.cpu_freq().max if psutil.cpu_freq() else None,
            'min_frequency': psutil.cpu_freq().min if psutil.cpu_freq() else None,
            'usage_percent': psutil.cpu_percent(interval=1),
            'usage_per_core': psutil.cpu_percent(interval=1, percpu=True),
            'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else None
        }
        
        logger.debug("CPU情報取得完了")
        return cpu_info
        
    except Exception as e:
        logger.error(f"CPU情報取得エラー: {str(e)}")
        return {'error': str(e)}


def get_memory_info() -> Dict[str, Any]:
    """
    メモリ情報を取得します。
    
    Returns:
        Dict[str, Any]: メモリ情報の辞書
    """
    try:
        virtual_memory = psutil.virtual_memory()
        swap_memory = psutil.swap_memory()
        
        memory_info = {
            'virtual': {
                'total_gb': round(virtual_memory.total / BYTES_TO_GB, 2),
                'available_gb': round(virtual_memory.available / BYTES_TO_GB, 2),
                'used_gb': round(virtual_memory.used / BYTES_TO_GB, 2),
                'free_gb': round(virtual_memory.free / BYTES_TO_GB, 2),
                'usage_percent': virtual_memory.percent
            },
            'swap': {
                'total_gb': round(swap_memory.total / BYTES_TO_GB, 2),
                'used_gb': round(swap_memory.used / BYTES_TO_GB, 2),
                'free_gb': round(swap_memory.free / BYTES_TO_GB, 2),
                'usage_percent': swap_memory.percent
            }
        }
        
        logger.debug("メモリ情報取得完了")
        return memory_info
        
    except Exception as e:
        logger.error(f"メモリ情報取得エラー: {str(e)}")
        return {'error': str(e)}


def get_disk_info() -> Dict[str, Any]:
    """
    ディスク情報を取得します。
    
    Returns:
        Dict[str, Any]: ディスク情報の辞書
    """
    try:
        disk_info = {}
        
        # 全てのディスクパーティションを取得
        partitions = psutil.disk_partitions()
        
        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                
                disk_info[partition.device] = {
                    'mountpoint': partition.mountpoint,
                    'filesystem': partition.fstype,
                    'total_gb': round(usage.total / BYTES_TO_GB, 2),
                    'used_gb': round(usage.used / BYTES_TO_GB, 2),
                    'free_gb': round(usage.free / BYTES_TO_GB, 2),
                    'usage_percent': round((usage.used / usage.total) * 100, 2)
                }
            except PermissionError:
                # アクセス権限がない場合はスキップ
                continue
        
        logger.debug("ディスク情報取得完了")
        return disk_info
        
    except Exception as e:
        logger.error(f"ディスク情報取得エラー: {str(e)}")
        return {'error': str(e)}


def get_network_info() -> Dict[str, Any]:
    """
    ネットワーク情報を取得します。
    
    Returns:
        Dict[str, Any]: ネットワーク情報の辞書
    """
    try:
        network_info = {}
        
        # ネットワークインターフェース情報
        interfaces = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
        
        for interface_name, addresses in interfaces.items():
            interface_info = {
                'addresses': [],
                'is_up': stats[interface_name].isup if interface_name in stats else False,
                'speed': stats[interface_name].speed if interface_name in stats else None
            }
            
            for addr in addresses:
                interface_info['addresses'].append({
                    'family': str(addr.family),
                    'address': addr.address,
                    'netmask': addr.netmask,
                    'broadcast': addr.broadcast
                })
            
            network_info[interface_name] = interface_info
        
        # ネットワーク統計情報
        net_io = psutil.net_io_counters()
        network_info['statistics'] = {
            'bytes_sent': net_io.bytes_sent,
            'bytes_received': net_io.bytes_recv,
            'packets_sent': net_io.packets_sent,
            'packets_received': net_io.packets_recv,
            'errors_in': net_io.errin,
            'errors_out': net_io.errout,
            'drops_in': net_io.dropin,
            'drops_out': net_io.dropout
        }
        
        logger.debug("ネットワーク情報取得完了")
        return network_info
        
    except Exception as e:
        logger.error(f"ネットワーク情報取得エラー: {str(e)}")
        return {'error': str(e)}


def get_process_list(sort_by: str = 'memory_percent') -> List[Dict[str, Any]]:
    """
    実行中のプロセス一覧を取得します。
    
    Args:
        sort_by: ソート基準（'memory_percent', 'cpu_percent', 'pid', 'name'）
    
    Returns:
        List[Dict[str, Any]]: プロセス情報のリスト
    """
    try:
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'username', 'memory_percent', 'cpu_percent']):
            try:
                process_info = proc.info
                process_info['memory_mb'] = round(proc.memory_info().rss / BYTES_TO_MB, 2)
                processes.append(process_info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # ソート
        if sort_by in ['memory_percent', 'cpu_percent']:
            processes.sort(key=lambda x: x.get(sort_by, 0), reverse=True)
        else:
            processes.sort(key=lambda x: x.get(sort_by, ''))
        
        logger.debug(f"プロセス一覧取得完了: {len(processes)}件")
        return processes
        
    except Exception as e:
        logger.error(f"プロセス一覧取得エラー: {str(e)}")
        return []


def kill_process_by_name(process_name: str, force: bool = False) -> Dict[str, Any]:
    """
    プロセス名でプロセスを終了します。
    
    Args:
        process_name: 終了するプロセス名
        force: 強制終了するかどうか
    
    Returns:
        Dict[str, Any]: 実行結果の辞書
    """
    try:
        killed_processes = []
        
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'] == process_name:
                    if force:
                        proc.kill()
                    else:
                        proc.terminate()
                    killed_processes.append(proc.info['pid'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        result = {
            'success': True,
            'process_name': process_name,
            'killed_pids': killed_processes,
            'count': len(killed_processes),
            'force': force
        }
        
        logger.info(f"プロセス終了完了: {process_name} - {len(killed_processes)}件")
        return result
        
    except Exception as e:
        result = {
            'success': False,
            'process_name': process_name,
            'error': str(e)
        }
        logger.error(f"プロセス終了エラー: {process_name} - {str(e)}")
        return result


def get_environment_variables(filter_prefix: Optional[str] = None) -> Dict[str, str]:
    """
    環境変数を取得します。
    
    Args:
        filter_prefix: フィルタリング用のプレフィックス
    
    Returns:
        Dict[str, str]: 環境変数の辞書
    """
    try:
        env_vars = dict(os.environ)
        
        if filter_prefix:
            env_vars = {k: v for k, v in env_vars.items() if k.startswith(filter_prefix)}
        
        logger.debug(f"環境変数取得完了: {len(env_vars)}件")
        return env_vars
        
    except Exception as e:
        logger.error(f"環境変数取得エラー: {str(e)}")
        return {}


def set_environment_variable(name: str, value: str, permanent: bool = False) -> bool:
    """
    環境変数を設定します。
    
    Args:
        name: 環境変数名
        value: 設定する値
        permanent: 永続的に設定するかどうか（Windows のみ）
    
    Returns:
        bool: 設定成功の場合True
    """
    try:
        os.environ[name] = value
        
        if permanent and platform.system() == 'Windows':
            # Windows の場合、レジストリに永続的に設定
            subprocess.run(['setx', name, value], check=True, capture_output=True)
        
        logger.debug(f"環境変数設定完了: {name}={value}")
        return True
        
    except Exception as e:
        logger.error(f"環境変数設定エラー: {name} - {str(e)}")
        return False


def execute_command(command: Union[str, List[str]], timeout: int = 30,
                   capture_output: bool = True) -> Dict[str, Any]:
    """
    システムコマンドを実行します。
    
    Args:
        command: 実行するコマンド
        timeout: タイムアウト時間（秒）
        capture_output: 出力をキャプチャするかどうか
    
    Returns:
        Dict[str, Any]: 実行結果の辞書
    """
    try:
        start_time = datetime.now()
        
        if isinstance(command, str):
            # シェルコマンドとして実行
            result = subprocess.run(
                command,
                shell=True,
                timeout=timeout,
                capture_output=capture_output,
                text=True
            )
        else:
            # リストとして実行
            result = subprocess.run(
                command,
                timeout=timeout,
                capture_output=capture_output,
                text=True
            )
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        command_result = {
            'success': result.returncode == 0,
            'return_code': result.returncode,
            'stdout': result.stdout if capture_output else None,
            'stderr': result.stderr if capture_output else None,
            'execution_time_seconds': round(execution_time, 2),
            'command': command
        }
        
        logger.debug(f"コマンド実行完了: {command} - 戻り値: {result.returncode}")
        return command_result
        
    except subprocess.TimeoutExpired:
        result = {
            'success': False,
            'error': 'タイムアウト',
            'command': command,
            'timeout': timeout
        }
        logger.error(f"コマンド実行タイムアウト: {command}")
        return result
        
    except Exception as e:
        result = {
            'success': False,
            'error': str(e),
            'command': command
        }
        logger.error(f"コマンド実行エラー: {command} - {str(e)}")
        return result


def get_system_uptime() -> Dict[str, Any]:
    """
    システムの稼働時間を取得します。
    
    Returns:
        Dict[str, Any]: 稼働時間情報の辞書
    """
    try:
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        current_time = datetime.now()
        uptime = current_time - boot_time
        
        uptime_info = {
            'boot_time': boot_time.isoformat(),
            'current_time': current_time.isoformat(),
            'uptime_seconds': int(uptime.total_seconds()),
            'uptime_days': uptime.days,
            'uptime_hours': uptime.seconds // 3600,
            'uptime_minutes': (uptime.seconds % 3600) // 60,
            'uptime_formatted': str(uptime).split('.')[0]  # マイクロ秒を除去
        }
        
        logger.debug("システム稼働時間取得完了")
        return uptime_info
        
    except Exception as e:
        logger.error(f"システム稼働時間取得エラー: {str(e)}")
        return {'error': str(e)}


def check_admin_privileges() -> bool:
    """
    管理者権限で実行されているかチェックします。
    
    Returns:
        bool: 管理者権限の場合True
    """
    try:
        if platform.system() == 'Windows':
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            return os.geteuid() == 0
    except Exception as e:
        logger.error(f"管理者権限チェックエラー: {str(e)}")
        return False


def get_installed_packages() -> List[Dict[str, str]]:
    """
    インストールされているPythonパッケージ一覧を取得します。
    
    Returns:
        List[Dict[str, str]]: パッケージ情報のリスト
    """
    try:
        result = execute_command([sys.executable, '-m', 'pip', 'list', '--format=json'])
        
        if result['success']:
            import json
            packages = json.loads(result['stdout'])
            logger.debug(f"インストール済みパッケージ取得完了: {len(packages)}件")
            return packages
        else:
            logger.error("パッケージ一覧取得失敗")
            return []
            
    except Exception as e:
        logger.error(f"パッケージ一覧取得エラー: {str(e)}")
        return []


def cleanup_temp_files(temp_dir: Optional[str] = None, older_than_days: int = 7) -> Dict[str, Any]:
    """
    一時ファイルをクリーンアップします。
    
    Args:
        temp_dir: 一時ディレクトリパス（Noneの場合はシステムデフォルト）
        older_than_days: この日数より古いファイルを削除
    
    Returns:
        Dict[str, Any]: クリーンアップ結果の辞書
    """
    try:
        if temp_dir is None:
            temp_dir = Path.home() / 'tmp' if platform.system() != 'Windows' else Path.home() / 'AppData' / 'Local' / 'Temp'
        else:
            temp_dir = Path(temp_dir)
        
        if not temp_dir.exists():
            return {'success': False, 'error': 'ディレクトリが存在しません'}
        
        cutoff_time = datetime.now() - timedelta(days=older_than_days)
        deleted_files = []
        total_size = 0
        
        for file_path in temp_dir.rglob('*'):
            if file_path.is_file():
                try:
                    file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_time < cutoff_time:
                        file_size = file_path.stat().st_size
                        file_path.unlink()
                        deleted_files.append(str(file_path))
                        total_size += file_size
                except (PermissionError, FileNotFoundError):
                    continue
        
        result = {
            'success': True,
            'temp_dir': str(temp_dir),
            'deleted_files_count': len(deleted_files),
            'total_size_mb': round(total_size / BYTES_TO_MB, 2),
            'older_than_days': older_than_days
        }
        
        logger.info(f"一時ファイルクリーンアップ完了: {len(deleted_files)}件削除")
        return result
        
    except Exception as e:
        result = {
            'success': False,
            'error': str(e)
        }
        logger.error(f"一時ファイルクリーンアップエラー: {str(e)}")
        return result
