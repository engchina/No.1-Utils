"""
ネットワーク操作のためのユーティリティモジュール
HTTP リクエスト、URL 操作、ネットワーク診断などの機能を提供します。
"""

import socket
import urllib.parse
import urllib.request
import urllib.error
import ssl
import json
import logging
from typing import Dict, Any, Optional, Union, List, Tuple
from datetime import datetime, timedelta
import time

# ログ設定
logger = logging.getLogger(__name__)

# 定数定義
DEFAULT_TIMEOUT = 30
DEFAULT_USER_AGENT = 'No.1-Utils/1.0.0'
DEFAULT_RETRIES = 3
COMMON_PORTS = {
    'http': 80,
    'https': 443,
    'ftp': 21,
    'ssh': 22,
    'telnet': 23,
    'smtp': 25,
    'dns': 53,
    'pop3': 110,
    'imap': 143,
    'mysql': 3306,
    'postgresql': 5432,
    'redis': 6379
}


def is_valid_ip(ip_address: str, version: Optional[int] = None) -> bool:
    """
    IPアドレスの妥当性を検証します。
    
    Args:
        ip_address: 検証するIPアドレス
        version: IPバージョン（4または6、Noneの場合は両方を許可）
    
    Returns:
        bool: 有効なIPアドレスの場合True
    """
    try:
        if version == 4:
            socket.inet_aton(ip_address)
            return True
        elif version == 6:
            socket.inet_pton(socket.AF_INET6, ip_address)
            return True
        else:
            # IPv4を試行
            try:
                socket.inet_aton(ip_address)
                return True
            except socket.error:
                # IPv6を試行
                try:
                    socket.inet_pton(socket.AF_INET6, ip_address)
                    return True
                except socket.error:
                    return False
    except socket.error:
        return False


def get_local_ip() -> str:
    """
    ローカルIPアドレスを取得します。
    
    Returns:
        str: ローカルIPアドレス
    """
    try:
        # ダミーの接続を作成してローカルIPを取得
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
        
        logger.debug(f"ローカルIP取得成功: {local_ip}")
        return local_ip
    except Exception as e:
        logger.error(f"ローカルIP取得エラー: {str(e)}")
        return "127.0.0.1"


def check_port_open(host: str, port: int, timeout: int = DEFAULT_TIMEOUT) -> bool:
    """
    指定されたホストとポートが開いているかチェックします。
    
    Args:
        host: ホスト名またはIPアドレス
        port: ポート番号
        timeout: タイムアウト時間（秒）
    
    Returns:
        bool: ポートが開いている場合True
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            is_open = result == 0
        
        logger.debug(f"ポートチェック: {host}:{port} = {'開放' if is_open else '閉鎖'}")
        return is_open
    except Exception as e:
        logger.error(f"ポートチェックエラー: {str(e)}")
        return False


def scan_ports(host: str, ports: List[int], timeout: int = 5) -> Dict[int, bool]:
    """
    複数のポートをスキャンします。
    
    Args:
        host: ホスト名またはIPアドレス
        ports: スキャンするポートのリスト
        timeout: 各ポートのタイムアウト時間（秒）
    
    Returns:
        Dict[int, bool]: ポート番号と開放状態の辞書
    """
    results = {}
    
    for port in ports:
        results[port] = check_port_open(host, port, timeout)
        time.sleep(0.1)  # 負荷軽減のための短い待機
    
    open_ports = [port for port, is_open in results.items() if is_open]
    logger.info(f"ポートスキャン完了: {host} - 開放ポート: {open_ports}")
    
    return results


def resolve_hostname(hostname: str) -> Optional[str]:
    """
    ホスト名をIPアドレスに解決します。
    
    Args:
        hostname: 解決するホスト名
    
    Returns:
        Optional[str]: IPアドレス、解決できない場合はNone
    """
    try:
        ip_address = socket.gethostbyname(hostname)
        logger.debug(f"ホスト名解決成功: {hostname} → {ip_address}")
        return ip_address
    except socket.gaierror as e:
        logger.warning(f"ホスト名解決失敗: {hostname} - {str(e)}")
        return None


def reverse_dns_lookup(ip_address: str) -> Optional[str]:
    """
    IPアドレスからホスト名を逆引きします。
    
    Args:
        ip_address: 逆引きするIPアドレス
    
    Returns:
        Optional[str]: ホスト名、逆引きできない場合はNone
    """
    try:
        hostname = socket.gethostbyaddr(ip_address)[0]
        logger.debug(f"逆引きDNS成功: {ip_address} → {hostname}")
        return hostname
    except socket.herror as e:
        logger.warning(f"逆引きDNS失敗: {ip_address} - {str(e)}")
        return None


def ping_host(host: str, timeout: int = DEFAULT_TIMEOUT) -> Dict[str, Any]:
    """
    ホストにpingを送信します（TCP接続による疑似ping）。
    
    Args:
        host: pingを送信するホスト
        timeout: タイムアウト時間（秒）
    
    Returns:
        Dict[str, Any]: ping結果の辞書
    """
    start_time = time.time()
    
    try:
        # HTTP(80)またはHTTPS(443)ポートへの接続を試行
        port = 80
        if host.startswith('https://') or host.endswith(':443'):
            port = 443
        
        # URLからホスト名を抽出
        if '://' in host:
            host = urllib.parse.urlparse(host).netloc.split(':')[0]
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            
        end_time = time.time()
        response_time = (end_time - start_time) * 1000  # ミリ秒
        
        success = result == 0
        
        result_dict = {
            'host': host,
            'success': success,
            'response_time_ms': round(response_time, 2),
            'timestamp': datetime.now().isoformat()
        }
        
        logger.debug(f"Ping結果: {host} - {'成功' if success else '失敗'} ({response_time:.2f}ms)")
        return result_dict
        
    except Exception as e:
        end_time = time.time()
        response_time = (end_time - start_time) * 1000
        
        result_dict = {
            'host': host,
            'success': False,
            'response_time_ms': round(response_time, 2),
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }
        
        logger.error(f"Pingエラー: {host} - {str(e)}")
        return result_dict


def simple_http_request(url: str, method: str = 'GET', headers: Optional[Dict[str, str]] = None,
                       data: Optional[Union[str, bytes, Dict[str, Any]]] = None,
                       timeout: int = DEFAULT_TIMEOUT) -> Dict[str, Any]:
    """
    シンプルなHTTPリクエストを送信します。
    
    Args:
        url: リクエストURL
        method: HTTPメソッド
        headers: リクエストヘッダー
        data: リクエストデータ
        timeout: タイムアウト時間（秒）
    
    Returns:
        Dict[str, Any]: レスポンス情報の辞書
    """
    try:
        # デフォルトヘッダーを設定
        if headers is None:
            headers = {}
        
        if 'User-Agent' not in headers:
            headers['User-Agent'] = DEFAULT_USER_AGENT
        
        # データの処理
        if data is not None:
            if isinstance(data, dict):
                data = json.dumps(data).encode('utf-8')
                headers['Content-Type'] = 'application/json'
            elif isinstance(data, str):
                data = data.encode('utf-8')
        
        # リクエストの作成
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        
        start_time = time.time()
        
        # リクエストの送信
        with urllib.request.urlopen(req, timeout=timeout) as response:
            response_data = response.read()
            end_time = time.time()
            
            # レスポンスの解析
            content_type = response.headers.get('Content-Type', '')
            
            if 'application/json' in content_type:
                try:
                    response_data = json.loads(response_data.decode('utf-8'))
                except json.JSONDecodeError:
                    response_data = response_data.decode('utf-8')
            else:
                response_data = response_data.decode('utf-8')
            
            result = {
                'success': True,
                'status_code': response.status,
                'headers': dict(response.headers),
                'data': response_data,
                'response_time_ms': round((end_time - start_time) * 1000, 2),
                'url': url
            }
            
            logger.debug(f"HTTPリクエスト成功: {method} {url} - {response.status}")
            return result
            
    except urllib.error.HTTPError as e:
        result = {
            'success': False,
            'status_code': e.code,
            'error': str(e),
            'url': url
        }
        logger.error(f"HTTPエラー: {method} {url} - {e.code}")
        return result
        
    except Exception as e:
        result = {
            'success': False,
            'error': str(e),
            'url': url
        }
        logger.error(f"リクエストエラー: {method} {url} - {str(e)}")
        return result


def download_file(url: str, file_path: str, chunk_size: int = 8192,
                 timeout: int = DEFAULT_TIMEOUT) -> Dict[str, Any]:
    """
    ファイルをダウンロードします。
    
    Args:
        url: ダウンロードURL
        file_path: 保存先ファイルパス
        chunk_size: チャンクサイズ（バイト）
        timeout: タイムアウト時間（秒）
    
    Returns:
        Dict[str, Any]: ダウンロード結果の辞書
    """
    try:
        start_time = time.time()
        
        req = urllib.request.Request(url, headers={'User-Agent': DEFAULT_USER_AGENT})
        
        with urllib.request.urlopen(req, timeout=timeout) as response:
            total_size = int(response.headers.get('Content-Length', 0))
            downloaded_size = 0
            
            with open(file_path, 'wb') as f:
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded_size += len(chunk)
        
        end_time = time.time()
        download_time = end_time - start_time
        
        result = {
            'success': True,
            'file_path': file_path,
            'total_size': total_size,
            'downloaded_size': downloaded_size,
            'download_time_seconds': round(download_time, 2),
            'average_speed_kbps': round((downloaded_size / 1024) / download_time, 2) if download_time > 0 else 0
        }
        
        logger.info(f"ファイルダウンロード成功: {url} → {file_path}")
        return result
        
    except Exception as e:
        result = {
            'success': False,
            'error': str(e),
            'url': url,
            'file_path': file_path
        }
        logger.error(f"ファイルダウンロードエラー: {url} - {str(e)}")
        return result


def get_public_ip() -> Optional[str]:
    """
    パブリックIPアドレスを取得します。
    
    Returns:
        Optional[str]: パブリックIPアドレス、取得できない場合はNone
    """
    services = [
        'https://api.ipify.org',
        'https://icanhazip.com',
        'https://ident.me'
    ]
    
    for service in services:
        try:
            response = simple_http_request(service, timeout=10)
            if response.get('success'):
                ip = response['data'].strip()
                if is_valid_ip(ip, version=4):
                    logger.debug(f"パブリックIP取得成功: {ip}")
                    return ip
        except Exception:
            continue
    
    logger.warning("パブリックIP取得失敗")
    return None


def parse_url(url: str) -> Dict[str, Any]:
    """
    URLを解析して各部分を取得します。
    
    Args:
        url: 解析するURL
    
    Returns:
        Dict[str, Any]: URL構成要素の辞書
    """
    try:
        parsed = urllib.parse.urlparse(url)
        
        result = {
            'scheme': parsed.scheme,
            'netloc': parsed.netloc,
            'hostname': parsed.hostname,
            'port': parsed.port,
            'path': parsed.path,
            'params': parsed.params,
            'query': parsed.query,
            'fragment': parsed.fragment,
            'username': parsed.username,
            'password': parsed.password,
            'query_params': dict(urllib.parse.parse_qsl(parsed.query))
        }
        
        logger.debug(f"URL解析完了: {url}")
        return result
        
    except Exception as e:
        logger.error(f"URL解析エラー: {url} - {str(e)}")
        return {'error': str(e)}


def build_url(base_url: str, path: str = '', params: Optional[Dict[str, Any]] = None) -> str:
    """
    URLを構築します。
    
    Args:
        base_url: ベースURL
        path: パス
        params: クエリパラメータ
    
    Returns:
        str: 構築されたURL
    """
    try:
        # ベースURLとパスを結合
        url = urllib.parse.urljoin(base_url, path)
        
        # クエリパラメータを追加
        if params:
            query_string = urllib.parse.urlencode(params)
            url = f"{url}?{query_string}"
        
        logger.debug(f"URL構築完了: {url}")
        return url
        
    except Exception as e:
        logger.error(f"URL構築エラー: {str(e)}")
        return base_url
