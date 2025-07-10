"""
No.1-Utils - 汎用ユーティリティライブラリ

このパッケージには以下のユーティリティモジュールが含まれています：

- dict_util: 辞書操作のためのユーティリティ
- generator_util: SnowflakeアルゴリズムによるID生成
- image_util: 画像処理のためのユーティリティ
- json_util: JSON操作のためのユーティリティ
- string_util: 文字列操作のためのユーティリティ
- file_util: ファイル操作のためのユーティリティ
- date_util: 日付・時刻操作のためのユーティリティ
- validation_util: データ検証のためのユーティリティ
- crypto_util: 暗号化・復号化のためのユーティリティ
- network_util: ネットワーク操作のためのユーティリティ
- system_util: システム情報・操作のためのユーティリティ
- config_util: 設定ファイル管理のためのユーティリティ
- log_util: ログ管理のためのユーティリティ
- cache_util: キャッシュ操作のためのユーティリティ
- math_util: 数学計算のためのユーティリティ
"""

# バージョン情報
__version__ = "1.0.0"
__author__ = "No.1-Utils Team"

# 主要なクラスと関数をインポート
from .dict_util import (
    safe_get,
    get_nested_value,
    set_nested_value,
    merge_dicts,
    filter_dict,
    flatten_dict,
    has_all_keys,
    remove_none_values
)

from .generator_util import (
    SnowflakeIdGenerator,
    generate_simple_id,
    get_global_id_generator,
    create_unique_id_with_prefix,
    create_custom_generator
)

from .json_util import (
    dumps_json,
    loads_json,
    dump_json,
    load_json,
    is_valid_json,
    pretty_print_json,
    merge_json_files,
    validate_json_schema
)

from .string_util import (
    is_empty_or_whitespace,
    safe_strip,
    truncate_string,
    camel_to_snake,
    snake_to_camel,
    kebab_to_camel,
    generate_random_string,
    mask_sensitive_data,
    extract_numbers,
    extract_emails,
    extract_urls,
    normalize_unicode,
    remove_accents,
    count_words,
    format_template,
    similarity_ratio,
    clean_html_tags,
    validate_string_length
)

from .file_util import (
    ensure_directory_exists,
    safe_read_file,
    safe_write_file,
    copy_file_with_metadata,
    move_file_safely,
    calculate_file_hash,
    get_file_info,
    format_file_size,
    find_files,
    clean_directory,
    read_file_in_chunks
)

from .date_util import (
    now_jst,
    today_jst,
    parse_date_string,
    format_date,
    format_japanese_date,
    add_business_days,
    get_age,
    get_date_range,
    get_month_boundaries,
    get_quarter_boundaries,
    is_weekend,
    is_business_day,
    time_until,
    format_duration,
    convert_timezone,
    validate_date_range,
    get_relative_date_description
)

from .validation_util import (
    ValidationError,
    ValidationResult,
    is_valid_email,
    is_valid_phone_jp,
    is_valid_zip_code_jp,
    is_valid_url,
    is_valid_ip_address,
    is_valid_credit_card,
    is_valid_japanese_text,
    validate_password_strength,
    validate_age,
    validate_required_fields,
    validate_data_types,
    validate_string_length as validate_string_length_detailed,
    validate_numeric_range,
    create_custom_validator
)

from .crypto_util import (
    generate_salt,
    generate_secure_token,
    hash_password,
    verify_password,
    simple_hash,
    generate_fernet_key,
    encrypt_data,
    decrypt_data,
    generate_rsa_keypair,
    create_jwt_token,
    verify_jwt_token,
    mask_sensitive_string,
    generate_api_key,
    constant_time_compare,
    derive_key_from_password
)

from .network_util import (
    is_valid_ip,
    get_local_ip,
    check_port_open,
    scan_ports,
    resolve_hostname,
    reverse_dns_lookup,
    ping_host,
    simple_http_request,
    download_file,
    get_public_ip,
    parse_url,
    build_url
)

from .system_util import (
    get_system_info,
    get_cpu_info,
    get_memory_info,
    get_disk_info,
    get_network_info,
    get_process_list,
    kill_process_by_name,
    get_environment_variables,
    set_environment_variable,
    execute_command,
    get_system_uptime,
    check_admin_privileges,
    get_installed_packages,
    cleanup_temp_files
)

from .config_util import (
    ConfigManager,
    load_config,
    save_config,
    merge_configs,
    get_config_template
)

from .log_util import (
    LogLevel,
    LogManager,
    setup_application_logging,
    analyze_log_file,
    compress_old_logs,
    get_logger,
    log_function_call
)

from .cache_util import (
    MemoryCache,
    FileCache,
    get_memory_cache,
    get_file_cache,
    cache_result,
    memoize,
    clear_all_caches
)

from .math_util import (
    safe_divide,
    round_decimal,
    percentage,
    percentage_change,
    clamp,
    normalize,
    lerp,
    distance_2d,
    distance_3d,
    angle_between_points,
    degrees_to_radians,
    radians_to_degrees,
    factorial,
    fibonacci,
    gcd,
    lcm,
    is_prime,
    prime_factors,
    calculate_statistics,
    moving_average,
    compound_interest,
    simple_interest,
    convert_units,
    generate_random_numbers,
    solve_quadratic
)

# 便利なエイリアス
# よく使用される関数のショートカット
get = safe_get
set_nested = set_nested_value
get_nested = get_nested_value
merge = merge_dicts
filter_keys = filter_dict
flatten = flatten_dict

# JSON操作のショートカット
to_json = dumps_json
from_json = loads_json
save_json = dump_json
load_json_file = load_json

# 文字列操作のショートカット
strip = safe_strip
truncate = truncate_string
random_string = generate_random_string
mask = mask_sensitive_data

# ファイル操作のショートカット
read_file = safe_read_file
write_file = safe_write_file
copy_file = copy_file_with_metadata
move_file = move_file_safely
file_hash = calculate_file_hash
file_info = get_file_info

# 日付操作のショートカット
now = now_jst
today = today_jst
parse_date = parse_date_string
jp_date = format_japanese_date

# 暗号化のショートカット
encrypt = encrypt_data
decrypt = decrypt_data
hash_data = simple_hash
secure_token = generate_secure_token

# 検証のショートカット
valid_email = is_valid_email
valid_url = is_valid_url
valid_phone = is_valid_phone_jp

# ネットワークのショートカット
ping = ping_host
http_get = lambda url: simple_http_request(url, 'GET')
http_post = lambda url, data=None: simple_http_request(url, 'POST', data=data)
local_ip = get_local_ip
public_ip = get_public_ip

# システムのショートカット
cpu_info = get_cpu_info
memory_info = get_memory_info
disk_info = get_disk_info
system_info = get_system_info
run_command = execute_command

# 設定のショートカット
load_cfg = load_config
save_cfg = save_config

# ログのショートカット
setup_logging = setup_application_logging
logger = get_logger

# キャッシュのショートカット
memory_cache = get_memory_cache
file_cache = get_file_cache

# 数学のショートカット
stats = calculate_statistics
random_numbers = generate_random_numbers

__all__ = [
    # バージョン情報
    '__version__',
    '__author__',

    # 辞書操作
    'safe_get', 'get_nested_value', 'set_nested_value', 'merge_dicts',
    'filter_dict', 'flatten_dict', 'has_all_keys', 'remove_none_values',

    # ID生成
    'SnowflakeIdGenerator', 'generate_simple_id', 'get_global_id_generator',
    'create_unique_id_with_prefix', 'create_custom_generator',

    # JSON操作
    'dumps_json', 'loads_json', 'dump_json', 'load_json', 'is_valid_json',
    'pretty_print_json', 'merge_json_files', 'validate_json_schema',

    # 文字列操作
    'is_empty_or_whitespace', 'safe_strip', 'truncate_string', 'camel_to_snake',
    'snake_to_camel', 'kebab_to_camel', 'generate_random_string', 'mask_sensitive_data',
    'extract_numbers', 'extract_emails', 'extract_urls', 'normalize_unicode',
    'remove_accents', 'count_words', 'format_template', 'similarity_ratio',
    'clean_html_tags', 'validate_string_length',

    # ファイル操作
    'ensure_directory_exists', 'safe_read_file', 'safe_write_file',
    'copy_file_with_metadata', 'move_file_safely', 'calculate_file_hash',
    'get_file_info', 'format_file_size', 'find_files', 'clean_directory',
    'read_file_in_chunks',

    # 日付操作
    'now_jst', 'today_jst', 'parse_date_string', 'format_date', 'format_japanese_date',
    'add_business_days', 'get_age', 'get_date_range', 'get_month_boundaries',
    'get_quarter_boundaries', 'is_weekend', 'is_business_day', 'time_until',
    'format_duration', 'convert_timezone', 'validate_date_range',
    'get_relative_date_description',

    # 検証
    'ValidationError', 'ValidationResult', 'is_valid_email', 'is_valid_phone_jp',
    'is_valid_zip_code_jp', 'is_valid_url', 'is_valid_ip_address', 'is_valid_credit_card',
    'is_valid_japanese_text', 'validate_password_strength', 'validate_age',
    'validate_required_fields', 'validate_data_types', 'validate_string_length_detailed',
    'validate_numeric_range', 'create_custom_validator',

    # 暗号化
    'generate_salt', 'generate_secure_token', 'hash_password', 'verify_password',
    'simple_hash', 'generate_fernet_key', 'encrypt_data', 'decrypt_data',
    'generate_rsa_keypair', 'create_jwt_token', 'verify_jwt_token',
    'mask_sensitive_string', 'generate_api_key', 'constant_time_compare',
    'derive_key_from_password',

    # ネットワーク
    'is_valid_ip', 'get_local_ip', 'check_port_open', 'scan_ports',
    'resolve_hostname', 'reverse_dns_lookup', 'ping_host', 'simple_http_request',
    'download_file', 'get_public_ip', 'parse_url', 'build_url',

    # システム
    'get_system_info', 'get_cpu_info', 'get_memory_info', 'get_disk_info',
    'get_network_info', 'get_process_list', 'kill_process_by_name',
    'get_environment_variables', 'set_environment_variable', 'execute_command',
    'get_system_uptime', 'check_admin_privileges', 'get_installed_packages',
    'cleanup_temp_files',

    # 設定
    'ConfigManager', 'load_config', 'save_config', 'merge_configs',
    'get_config_template',

    # ログ
    'LogLevel', 'LogManager', 'setup_application_logging', 'analyze_log_file',
    'compress_old_logs', 'get_logger', 'log_function_call',

    # キャッシュ
    'MemoryCache', 'FileCache', 'get_memory_cache', 'get_file_cache',
    'cache_result', 'memoize', 'clear_all_caches',

    # 数学
    'safe_divide', 'round_decimal', 'percentage', 'percentage_change',
    'clamp', 'normalize', 'lerp', 'distance_2d', 'distance_3d',
    'angle_between_points', 'degrees_to_radians', 'radians_to_degrees',
    'factorial', 'fibonacci', 'gcd', 'lcm', 'is_prime', 'prime_factors',
    'calculate_statistics', 'moving_average', 'compound_interest',
    'simple_interest', 'convert_units', 'generate_random_numbers',
    'solve_quadratic',

    # エイリアス
    'get', 'set_nested', 'get_nested', 'merge', 'filter_keys', 'flatten',
    'to_json', 'from_json', 'save_json', 'load_json_file',
    'strip', 'truncate', 'random_string', 'mask',
    'read_file', 'write_file', 'copy_file', 'move_file', 'file_hash', 'file_info',
    'now', 'today', 'parse_date', 'jp_date',
    'encrypt', 'decrypt', 'hash_data', 'secure_token',
    'valid_email', 'valid_url', 'valid_phone',
    'ping', 'http_get', 'http_post', 'local_ip', 'public_ip',
    'cpu_info', 'memory_info', 'disk_info', 'system_info', 'run_command',
    'load_cfg', 'save_cfg', 'setup_logging', 'logger',
    'memory_cache', 'file_cache', 'stats', 'random_numbers'
]