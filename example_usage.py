#!/usr/bin/env python3
"""
No.1-Utils 使用例
各種ユーティリティ関数の使用方法を示すサンプルコード
"""

import utils
from datetime import datetime

def main():
    print("=== No.1-Utils 使用例 ===\n")
    
    # 1. JSON操作の例
    print("1. JSON操作の例:")
    data = {"name": "田中太郎", "age": 30, "city": "東京"}
    json_str = utils.to_json(data)
    print(f"JSON文字列: {json_str}")
    
    parsed_data = utils.from_json(json_str)
    print(f"パース結果: {parsed_data}")
    print()
    
    # 2. 文字列操作の例
    print("2. 文字列操作の例:")
    text = "  Hello World  "
    print(f"元の文字列: '{text}'")
    print(f"トリム後: '{utils.strip(text)}'")
    
    camel_case = "userName"
    snake_case = utils.camel_to_snake(camel_case)
    print(f"キャメルケース→スネークケース: {camel_case} → {snake_case}")
    
    random_str = utils.random_string(10)
    print(f"ランダム文字列: {random_str}")
    
    masked = utils.mask("1234567890123456")
    print(f"マスク処理: 1234567890123456 → {masked}")
    print()
    
    # 3. 日付操作の例
    print("3. 日付操作の例:")
    now = utils.now()
    today = utils.today()
    print(f"現在時刻（JST）: {now}")
    print(f"今日の日付: {today}")
    
    jp_date = utils.jp_date(now)
    print(f"日本語形式: {jp_date}")
    
    birth_date = utils.parse_date("1990-05-15")
    if birth_date:
        age = utils.get_age(birth_date)
        print(f"年齢計算: 1990-05-15生まれ → {age}歳")
    print()
    
    # 4. 辞書操作の例
    print("4. 辞書操作の例:")
    nested_dict = {
        "user": {
            "profile": {
                "name": "山田花子",
                "email": "hanako@example.com"
            }
        }
    }
    
    name = utils.get_nested(nested_dict, "user.profile.name")
    print(f"ネストした値の取得: {name}")
    
    utils.set_nested(nested_dict, "user.profile.phone", "090-1234-5678")
    phone = utils.get_nested(nested_dict, "user.profile.phone")
    print(f"ネストした値の設定: {phone}")
    print()
    
    # 5. 検証の例
    print("5. 検証の例:")
    email = "test@example.com"
    print(f"メールアドレス検証: {email} → {utils.valid_email(email)}")
    
    url = "https://www.example.com"
    print(f"URL検証: {url} → {utils.valid_url(url)}")
    
    phone = "090-1234-5678"
    print(f"電話番号検証: {phone} → {utils.valid_phone(phone)}")
    print()
    
    # 6. 暗号化の例
    print("6. 暗号化の例:")
    password = "my_secret_password"
    hashed = utils.hash_password(password)
    print(f"パスワードハッシュ化完了")
    
    is_valid = utils.verify_password(password, hashed['hash'], hashed['salt'])
    print(f"パスワード検証: {is_valid}")
    
    token = utils.secure_token(16)
    print(f"セキュアトークン: {token}")
    
    # 対称暗号化の例
    key = utils.generate_fernet_key()
    plaintext = "機密データ"
    encrypted = utils.encrypt(plaintext, key)
    decrypted = utils.decrypt(encrypted, key)
    print(f"暗号化・復号化: {plaintext} → 暗号化 → {decrypted}")
    print()
    
    # 7. ID生成の例
    print("7. ID生成の例:")
    unique_id = utils.generate_simple_id()
    print(f"ユニークID: {unique_id}")
    
    prefixed_id = utils.create_unique_id_with_prefix("USER_")
    print(f"プレフィックス付きID: {prefixed_id}")
    print()
    
    # 8. ファイル操作の例（仮想的な例）
    print("8. ファイル操作の例:")
    file_size = 1024 * 1024 * 2.5  # 2.5MB
    formatted_size = utils.format_file_size(int(file_size))
    print(f"ファイルサイズフォーマット: {int(file_size)}バイト → {formatted_size}")
    print()
    
    # 9. バリデーションの詳細例
    print("9. バリデーションの詳細例:")
    user_data = {
        "name": "佐藤次郎",
        "email": "jiro@example.com",
        "age": 25
    }
    
    required_fields = ["name", "email", "age"]
    validation_result = utils.validate_required_fields(user_data, required_fields)
    print(f"必須フィールド検証: {validation_result}")
    
    type_specs = {"name": str, "email": str, "age": int}
    type_validation = utils.validate_data_types(user_data, type_specs)
    print(f"データ型検証: {type_validation}")
    
    password_strength = utils.validate_password_strength("StrongPass123!")
    print(f"パスワード強度検証: {password_strength}")
    print()

    # 10. ネットワーク操作の例
    print("10. ネットワーク操作の例:")
    local_ip = utils.local_ip()
    print(f"ローカルIP: {local_ip}")

    # ping_result = utils.ping("google.com")
    # print(f"Ping結果: {ping_result['success']} ({ping_result.get('response_time_ms', 0)}ms)")

    url_parts = utils.parse_url("https://example.com/path?param=value")
    print(f"URL解析: ホスト={url_parts.get('hostname')}, パス={url_parts.get('path')}")
    print()

    # 11. システム情報の例
    print("11. システム情報の例:")
    cpu_info = utils.cpu_info()
    print(f"CPU使用率: {cpu_info.get('usage_percent', 0)}%")

    memory_info = utils.memory_info()
    print(f"メモリ使用率: {memory_info['virtual']['usage_percent']}%")

    system_info = utils.system_info()
    print(f"OS: {system_info['platform']['system']} {system_info['platform']['release']}")
    print()

    # 12. 設定管理の例
    print("12. 設定管理の例:")
    # 一時的な設定ファイルを作成
    config_data = {
        "app": {"name": "テストアプリ", "version": "1.0.0"},
        "database": {"host": "localhost", "port": 5432}
    }
    utils.save_cfg(config_data, "temp_config.json")

    # 設定を読み込み
    loaded_config = utils.load_cfg("temp_config.json")
    print(f"設定読み込み: アプリ名={loaded_config['app']['name']}")

    # ConfigManagerを使用
    config_manager = utils.ConfigManager("temp_config.json")
    app_name = config_manager.get("app.name")
    print(f"ConfigManager: {app_name}")
    print()

    # 13. キャッシュ操作の例
    print("13. キャッシュ操作の例:")
    cache = utils.memory_cache()
    cache.set("test_key", "test_value", ttl=60)
    cached_value = cache.get("test_key")
    print(f"メモリキャッシュ: {cached_value}")

    # 関数結果のキャッシュ
    @utils.memoize(ttl=30)
    def expensive_calculation(x):
        import time
        time.sleep(0.1)  # 重い処理をシミュレート
        return x * x

    result1 = expensive_calculation(5)  # 初回は計算
    result2 = expensive_calculation(5)  # キャッシュから取得
    print(f"関数キャッシュ: {result1} = {result2}")
    print()

    # 14. 数学計算の例
    print("14. 数学計算の例:")
    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    stats = utils.stats(numbers)
    print(f"統計情報: 平均={stats['mean']}, 中央値={stats['median']}")

    percentage = utils.percentage(25, 100)
    print(f"パーセンテージ: 25/100 = {percentage}%")

    distance = utils.distance_2d(0, 0, 3, 4)
    print(f"2D距離: (0,0)から(3,4)まで = {distance}")

    # 単位変換
    meters = utils.convert_units(100, 'cm', 'm')
    print(f"単位変換: 100cm = {meters}m")

    # 素数判定
    is_prime = utils.is_prime(17)
    print(f"素数判定: 17は素数? {is_prime}")
    print()

    # 15. ログ管理の例
    print("15. ログ管理の例:")
    # ログマネージャーの設定
    log_manager = utils.setup_logging("example_app", enable_console=True, enable_file=False)
    logger = log_manager.get_logger()

    logger.info("これはINFOレベルのログです")
    logger.warning("これはWARNINGレベルのログです")
    logger.debug("これはDEBUGレベルのログです（表示されない場合があります）")
    print()

    print("=== 使用例完了 ===")

if __name__ == "__main__":
    main()
