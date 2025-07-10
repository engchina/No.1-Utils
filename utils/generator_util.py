import threading
import time
from typing import Optional


class SnowflakeIdGenerator:
    """
    Snowflakeアルゴリズムを使用してユニークなIDを生成するクラス
    Twitterが開発した分散システム用のID生成アルゴリズムを実装
    """

    # Snowflakeアルゴリズムの定数定義
    EPOCH_TIMESTAMP = 1288834974657  # Twitterエポック時刻 (2010-11-04T01:42:54.657Z)
    DATACENTER_ID_BITS = 5  # データセンターIDのビット数
    WORKER_ID_BITS = 5      # ワーカーIDのビット数
    SEQUENCE_BITS = 12      # シーケンス番号のビット数

    # === 1. 静的メソッド（最も基礎的なユーティリティ） ===

    @staticmethod
    def _calculate_max_value(bits: int) -> int:
        """指定されたビット数での最大値を計算する"""
        return -1 ^ (-1 << bits)

    # === 2. 初期化と検証メソッド ===

    def __init__(self, datacenter_id: int, worker_id: int):
        """
        SnowflakeIdGeneratorを初期化する

        Args:
            datacenter_id: データセンターID (0-31の範囲)
            worker_id: ワーカーID (0-31の範囲)

        Raises:
            ValueError: IDが有効範囲外の場合
        """
        self._validate_ids(datacenter_id, worker_id)

        self._datacenter_id = datacenter_id
        self._worker_id = worker_id
        self._sequence_number = 0
        self._last_timestamp = -1

        # 各フィールドの最大値を計算
        self._max_datacenter_id = self._calculate_max_value(self.DATACENTER_ID_BITS)
        self._max_worker_id = self._calculate_max_value(self.WORKER_ID_BITS)
        self._max_sequence = self._calculate_max_value(self.SEQUENCE_BITS)

        # 各フィールドのビットシフト量を計算
        self._worker_id_shift = self.SEQUENCE_BITS
        self._datacenter_id_shift = self.SEQUENCE_BITS + self.WORKER_ID_BITS
        self._timestamp_shift = self.SEQUENCE_BITS + self.WORKER_ID_BITS + self.DATACENTER_ID_BITS

        # スレッドセーフティを保証するためのロック
        self._lock = threading.Lock()

    def _validate_ids(self, datacenter_id: int, worker_id: int) -> None:
        """データセンターIDとワーカーIDの妥当性を検証する"""
        max_datacenter = self._calculate_max_value(self.DATACENTER_ID_BITS)
        max_worker = self._calculate_max_value(self.WORKER_ID_BITS)

        if not (0 <= datacenter_id <= max_datacenter):
            raise ValueError(f"データセンターIDは0から{max_datacenter}の範囲で指定してください")

        if not (0 <= worker_id <= max_worker):
            raise ValueError(f"ワーカーIDは0から{max_worker}の範囲で指定してください")

    # === 3. 核心業務ロジックメソッド（主要な公開インターフェース） ===

    def generate_id(self) -> int:
        """
        ユニークなSnowflake IDを生成する

        Returns:
            int: 生成されたSnowflake ID

        Raises:
            ValueError: システムクロックが逆行した場合
        """
        with self._lock:
            current_timestamp = self._get_current_timestamp_millis()

            # システムクロックの逆行をチェック
            if current_timestamp < self._last_timestamp:
                raise ValueError("システムクロックが逆行しました。ID生成を拒否します。")

            # 同一ミリ秒内での連続生成処理
            if current_timestamp == self._last_timestamp:
                self._sequence_number = (self._sequence_number + 1) & self._max_sequence
                # シーケンス番号がオーバーフローした場合、次のミリ秒まで待機
                if self._sequence_number == 0:
                    current_timestamp = self._wait_for_next_millisecond(self._last_timestamp)
            else:
                # 新しいミリ秒の場合、シーケンス番号をリセット
                self._sequence_number = 0

            self._last_timestamp = current_timestamp

            # Snowflake IDを構築して返却
            return self._build_snowflake_id(current_timestamp)

    # === 4. 補助メソッド（核心機能をサポートするプライベートメソッド） ===

    def _get_current_timestamp_millis(self) -> int:
        """現在のタイムスタンプをミリ秒単位で取得する"""
        return int(time.time() * 1000)

    def _wait_for_next_millisecond(self, last_timestamp: int) -> int:
        """次のミリ秒まで待機する"""
        current_timestamp = self._get_current_timestamp_millis()
        while current_timestamp <= last_timestamp:
            current_timestamp = self._get_current_timestamp_millis()
        return current_timestamp

    def _build_snowflake_id(self, timestamp: int) -> int:
        """タイムスタンプからSnowflake IDを構築する"""
        return ((timestamp - self.EPOCH_TIMESTAMP) << self._timestamp_shift) | \
               (self._datacenter_id << self._datacenter_id_shift) | \
               (self._worker_id << self._worker_id_shift) | \
               self._sequence_number



# === グローバル変数（シングルトンパターン用） ===
_global_generator: Optional[SnowflakeIdGenerator] = None
_generator_lock = threading.Lock()


# === 5. 公開インターフェース関数（使用頻度と依存関係順に配置） ===

def generate_simple_id() -> int:
    """
    シンプルなSnowflake IDを生成する（グローバルジェネレーターを使用）
    最も頻繁に使用される基本的なID生成関数

    Returns:
        int: 生成されたSnowflake ID
    """
    generator = get_global_id_generator()
    return generator.generate_id()


def get_global_id_generator(datacenter_id: int = 1, worker_id: int = 1) -> SnowflakeIdGenerator:
    """
    グローバルなSnowflakeIdGeneratorインスタンスを取得する
    シングルトンパターンで実装されており、アプリケーション全体で同一インスタンスを使用

    Args:
        datacenter_id: データセンターID (初回呼び出し時のみ有効)
        worker_id: ワーカーID (初回呼び出し時のみ有効)

    Returns:
        SnowflakeIdGenerator: グローバルジェネレーターインスタンス
    """
    global _global_generator

    if _global_generator is None:
        with _generator_lock:
            if _global_generator is None:
                _global_generator = SnowflakeIdGenerator(datacenter_id, worker_id)

    return _global_generator


def create_unique_id_with_prefix(prefix: str, datacenter_id: int = 1, worker_id: int = 1) -> str:
    """
    プレフィックス付きのユニークIDを生成する
    特定の用途向けのカスタマイズされたID生成関数

    Args:
        prefix: IDのプレフィックス文字列
        datacenter_id: データセンターID (デフォルト: 1)
        worker_id: ワーカーID (デフォルト: 1)

    Returns:
        str: プレフィックス付きのユニークID

    Raises:
        ValueError: IDが有効範囲外の場合
    """
    id_generator = SnowflakeIdGenerator(datacenter_id, worker_id)
    snowflake_id = id_generator.generate_id()
    return f"{prefix}{snowflake_id}"


def create_custom_generator(datacenter_id: int, worker_id: int) -> SnowflakeIdGenerator:
    """
    カスタム設定でSnowflakeIdGeneratorインスタンスを作成する
    特定の要件がある場合の専用ジェネレーター作成関数

    Args:
        datacenter_id: データセンターID (0-31の範囲)
        worker_id: ワーカーID (0-31の範囲)

    Returns:
        SnowflakeIdGenerator: 新しいジェネレーターインスタンス

    Raises:
        ValueError: IDが有効範囲外の場合
    """
    return SnowflakeIdGenerator(datacenter_id, worker_id)
