# No.1-Utils

汎用ユーティリティライブラリ - 日常的な開発作業を効率化するための包括的なツールセット

## 概要

No.1-Utilsは、Python開発において頻繁に使用される機能を集約した汎用ユーティリティライブラリです。JSON操作、文字列処理、ファイル操作、日付処理、データ検証、暗号化など、様々な分野の便利な関数を提供します。

## 特徴

- **包括的な機能**: 15つの専門分野にわたる豊富なユーティリティ関数
- **日本語対応**: 日本語特有の処理（電話番号、郵便番号、日付フォーマットなど）をサポート
- **セキュリティ重視**: 暗号化、ハッシュ化、トークン生成などのセキュリティ機能
- **使いやすさ**: 直感的なAPI設計と豊富なエイリアス
- **型安全性**: 全ての関数に型ヒントを提供
- **詳細なログ**: 日本語でのログ出力とエラーハンドリング

## インストール

```bash
conda create -n no.1-utils python=3.12 -y
conda activate no.1-utils
pip install -r requirements.txt
```

## 含まれるモジュール

### 1. JSON操作 (`json_util`)
- JSON文字列の変換・パース
- ファイルの読み書き
- スキーマ検証
- ファイル結合

### 2. 文字列操作 (`string_util`)
- ケース変換（camelCase ↔ snake_case ↔ kebab-case）
- ランダム文字列生成
- データマスキング
- 正規表現による抽出
- Unicode正規化

### 3. ファイル操作 (`file_util`)
- 安全なファイル読み書き
- ファイルコピー・移動
- ハッシュ値計算
- ディレクトリ管理
- ファイル検索

### 4. 日付・時刻操作 (`date_util`)
- 日本時間での日付処理
- 営業日計算
- 年齢計算
- 日付範囲生成
- 相対日付表現

### 5. データ検証 (`validation_util`)
- メールアドレス、URL、電話番号の検証
- パスワード強度チェック
- 日本語テキスト検証
- データ型・範囲検証
- カスタムバリデーター

### 6. 暗号化・セキュリティ (`crypto_util`)
- パスワードハッシュ化（PBKDF2）
- 対称暗号化（Fernet）
- JWT トークン
- RSA鍵ペア生成
- セキュアトークン生成

### 7. 辞書操作 (`dict_util`)
- ネストした辞書の操作
- 辞書のマージ・フィルタリング
- 平坦化・構造化
- 安全な値取得

### 8. ID生成 (`generator_util`)
- Snowflakeアルゴリズム
- ユニークID生成
- プレフィックス付きID
- 分散システム対応

### 9. 画像処理 (`image_util`)
- 画像ファイルのBase64エンコード・デコード
- Data URL形式への変換
- 画像フォーマット検出（JPEG、PNG、GIF、WebP等）
- 画像結合（縦・横方向）
- 画像圧縮・リサイズ
- MIMEタイプ判定

### 10. ネットワーク操作 (`network_util`)
- IPアドレス検証・取得
- ポートスキャン・チェック
- DNS解決・逆引き
- HTTP リクエスト
- ファイルダウンロード
- URL解析・構築

### 11. システム情報・操作 (`system_util`)
- システム情報取得
- CPU・メモリ・ディスク情報
- プロセス管理
- 環境変数操作
- コマンド実行
- 一時ファイルクリーンアップ

### 12. 設定ファイル管理 (`config_util`)
- JSON・YAML・INI・TOML対応
- ドット記法での設定アクセス
- 設定ファイルのマージ
- バックアップ機能
- テンプレート生成

### 13. ログ管理 (`log_util`)
- 複数ハンドラー対応
- カラー・JSON出力
- ローテーション機能
- ログ分析
- 圧縮・アーカイブ

### 14. キャッシュ操作 (`cache_util`)
- メモリキャッシュ（LRU・TTL）
- ファイルキャッシュ
- 関数結果キャッシュ
- デコレーター対応
- 期限切れ自動削除

### 15. 数学計算 (`math_util`)
- 統計計算
- 幾何学計算
- 単位変換
- 金融計算
- 素数・フィボナッチ
- 二次方程式解法

## 基本的な使用方法

```python
import utils

# JSON操作
data = {"name": "田中太郎", "age": 30}
json_str = utils.to_json(data)
parsed = utils.from_json(json_str)

# 文字列操作
clean_text = utils.strip("  Hello World  ")
snake_case = utils.camel_to_snake("userName")
random_str = utils.random_string(10)

# 日付操作
now = utils.now()  # 現在の日本時間
today = utils.today()  # 今日の日付
jp_date = utils.jp_date(now)  # 日本語形式

# 検証
is_valid_email = utils.valid_email("test@example.com")
is_valid_url = utils.valid_url("https://example.com")

# 暗号化
hashed = utils.hash_password("password")
token = utils.secure_token(32)
encrypted = utils.encrypt("secret", key)

# 辞書操作
value = utils.get_nested(data, "user.profile.name")
utils.set_nested(data, "user.profile.phone", "090-1234-5678")

# ID生成
unique_id = utils.generate_simple_id()

# ネットワーク操作
ping_result = utils.ping("google.com")
local_ip = utils.local_ip()
response = utils.http_get("https://api.example.com/data")

# システム情報
cpu_info = utils.cpu_info()
memory_info = utils.memory_info()
processes = utils.get_process_list()

# 設定管理
config = utils.ConfigManager("config.json")
config.set("app.debug", True)
debug_mode = config.get("app.debug", False)

# ログ管理
log_manager = utils.setup_logging("myapp")
logger = utils.logger()
logger.info("アプリケーション開始")

# キャッシュ操作
cache = utils.memory_cache()
cache.set("key", "value", ttl=300)
cached_value = cache.get("key")

# 数学計算
stats = utils.stats([1, 2, 3, 4, 5])
percentage = utils.percentage(25, 100)  # 25%
distance = utils.distance_2d(0, 0, 3, 4)  # 5.0
```

## 詳細な使用例

詳細な使用例については、`example_usage.py` ファイルを参照してください。

```bash
python example_usage.py
```

## エイリアス

よく使用される関数には短縮エイリアスが用意されています：

```python
# 元の関数名 → エイリアス
utils.safe_get() → utils.get()
utils.dumps_json() → utils.to_json()
utils.loads_json() → utils.from_json()
utils.safe_strip() → utils.strip()
utils.generate_random_string() → utils.random_string()
utils.mask_sensitive_data() → utils.mask()
utils.now_jst() → utils.now()
utils.today_jst() → utils.today()
utils.encrypt_data() → utils.encrypt()
utils.decrypt_data() → utils.decrypt()
```

## 各モジュールの詳細

### JSON操作 (`json_util`)

```python
# 基本的なJSON操作
data = {"name": "田中", "age": 30}
json_str = utils.dumps_json(data, indent=2)
parsed = utils.loads_json(json_str)

# ファイル操作
utils.dump_json(data, "data.json")
loaded = utils.load_json("data.json")

# 検証とフォーマット
is_valid = utils.is_valid_json('{"key": "value"}')
pretty = utils.pretty_print_json(data)

# 複数ファイルの結合
utils.merge_json_files(["file1.json", "file2.json"], "merged.json")
```

### 文字列操作 (`string_util`)

```python
# ケース変換
utils.camel_to_snake("userName")  # → "user_name"
utils.snake_to_camel("user_name")  # → "userName"
utils.kebab_to_camel("user-name")  # → "userName"

# 文字列生成とマスキング
random_str = utils.generate_random_string(10, include_special=True)
masked = utils.mask_sensitive_data("1234567890", visible_start=2, visible_end=2)

# 抽出機能
numbers = utils.extract_numbers("価格は1000円です")
emails = utils.extract_emails("連絡先: test@example.com")
urls = utils.extract_urls("サイト: https://example.com")

# 日本語処理
normalized = utils.normalize_unicode("ガ")  # 濁点の正規化
no_accents = utils.remove_accents("café")  # アクセント除去
word_count = utils.count_words("これは日本語のテストです", language='ja')
```

### ファイル操作 (`file_util`)

```python
# 安全なファイル操作
content = utils.safe_read_file("file.txt", encoding="utf-8")
utils.safe_write_file("output.txt", content, create_backup=True)

# ファイル情報とハッシュ
info = utils.get_file_info("file.txt")
hash_value = utils.calculate_file_hash("file.txt", algorithm="sha256")

# ファイル検索とクリーンアップ
files = utils.find_files("/path/to/dir", "*.py", recursive=True)
old_files = utils.clean_directory("/temp", older_than_days=30, dry_run=True)

# ファイルサイズフォーマット
size_str = utils.format_file_size(1024 * 1024)  # → "1.0 MB"
```

### 日付・時刻操作 (`date_util`)

```python
# 基本的な日付操作
now = utils.now_jst()  # 現在の日本時間
today = utils.today_jst()  # 今日の日付

# 日付パースとフォーマット
date_obj = utils.parse_date_string("2024-01-15")
jp_format = utils.format_japanese_date(date_obj, include_time=True)

# 営業日と年齢計算
business_day = utils.add_business_days(today, 5)  # 5営業日後
age = utils.get_age("1990-05-15")

# 日付範囲と境界
date_range = utils.get_date_range("2024-01-01", "2024-01-31")
month_start, month_end = utils.get_month_boundaries(today)

# 相対的な日付表現
relative = utils.get_relative_date_description("2024-01-16")  # "明日"
```

### データ検証 (`validation_util`)

```python
# 基本的な検証
utils.is_valid_email("test@example.com")
utils.is_valid_phone_jp("090-1234-5678", mobile_only=True)
utils.is_valid_zip_code_jp("123-4567")
utils.is_valid_url("https://example.com", require_https=True)

# パスワード強度検証
result = utils.validate_password_strength(
    "StrongPass123!",
    min_length=8,
    require_uppercase=True,
    require_special=True
)

# データ構造の検証
data = {"name": "田中", "email": "tanaka@example.com", "age": 30}
required_result = utils.validate_required_fields(data, ["name", "email"])
type_result = utils.validate_data_types(data, {"name": str, "age": int})

# カスタムバリデーター
custom_validator = utils.create_custom_validator(
    lambda x: len(x) > 5,
    "値は5文字以上である必要があります"
)
```

### 暗号化・セキュリティ (`crypto_util`)

```python
# パスワードハッシュ化
hashed = utils.hash_password("my_password")
is_valid = utils.verify_password("my_password", hashed['hash'], hashed['salt'])

# 対称暗号化
key = utils.generate_fernet_key()
encrypted = utils.encrypt_data("機密データ", key)
decrypted = utils.decrypt_data(encrypted, key)

# トークンとAPIキー生成
token = utils.generate_secure_token(32, url_safe=True)
api_key = utils.generate_api_key("API", 24)

# JWT操作
payload = {"user_id": 123, "role": "admin"}
jwt_token = utils.create_jwt_token(payload, "secret_key", expires_in=3600)
decoded = utils.verify_jwt_token(jwt_token, "secret_key")

# ハッシュ計算
hash_value = utils.simple_hash("データ", algorithm="sha256")
```

## 必要な依存関係

主要な依存関係：

- `cryptography`: 暗号化機能
- `python-dateutil`: 日付解析
- `PyJWT`: JWT トークン
- `Pillow`: 画像処理機能

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 貢献

バグ報告、機能要求、プルリクエストを歓迎します。

## 更新履歴

### v1.0.0
- 初回リリース
- 15つのユーティリティモジュールを提供
- 日本語対応とセキュリティ機能を重視
- ネットワーク、システム、設定、ログ、キャッシュ、数学計算機能を追加
- 包括的なエイリアスとショートカット関数を提供