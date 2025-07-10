import base64
import re
from io import BytesIO
from pathlib import Path
from typing import Optional, Dict, Pattern, Tuple

from PIL import Image

# 定数定義
DEFAULT_FORMAT = 'jpeg'
DEFAULT_QUALITY = 85
DEFAULT_MAX_WIDTH = 800
DEFAULT_MAX_HEIGHT = 1200
MERGE_DIRECTIONS = ['vertical', 'horizontal']

# Base64マジックナンバーパターン（パフォーマンス向上のためプリコンパイル）
# 参考: https://en.wikipedia.org/wiki/List_of_file_signatures
MAGIC_PATTERNS: Dict[Pattern[str], str] = {
    re.compile(r'^/9j/'): 'jpeg',  # JPEG
    re.compile(r'^iVBORw0KGgo'): 'png',  # PNG
    re.compile(r'^R0lGOD'): 'gif',  # GIF
    re.compile(r'^UklGR'): 'webp',  # WebP
    re.compile(r'^Qk0='): 'bmp',  # BMP ('BM')
    re.compile(r'^SUkq|^TU0A'): 'tiff',  # TIFF (リトルエンディアン II* とビッグエンディアン MM*)
    re.compile(r'^JVBER'): 'pdf',  # PDF ('%PDF')
}

# 拡張子とMIMEタイプのマッピング
MIME_TYPES: Dict[str, str] = {
    'jpeg': 'image/jpeg',
    'jpg': 'image/jpeg',
    'png': 'image/png',
    'gif': 'image/gif',
    'webp': 'image/webp',
    'bmp': 'image/bmp',
    'tiff': 'image/tiff',
    'tif': 'image/tiff',
}


# =============================================================================
# 基本ユーティリティ関数（プライベートヘルパー関数）
# =============================================================================


def _detect_format_from_base64(data: str) -> Optional[str]:
    """Base64データのマジックナンバーから画像フォーマットを検出"""
    for pattern, format_name in MAGIC_PATTERNS.items():
        if pattern.search(data):
            return format_name
    return None


def _validate_base64_data(data: str, strict: bool = False) -> bool:
    """Base64データの妥当性を検証"""
    if not isinstance(data, str) or not data:
        if strict:
            raise ValueError("入力が無効です: Base64データは空または非文字列であってはなりません。")
        return False

    if strict:
        try:
            base64.b64decode(data, validate=True)
        except (ValueError, base64.binascii.Error) as e:
            raise ValueError(f"無効なBase64データです: {e}") from e

    return True


def _calculate_resize_dimensions(
    original_size: Tuple[int, int],
    max_width: int,
    max_height: int
) -> Tuple[Tuple[int, int], bool]:
    """リサイズ後の寸法を計算"""
    width, height = original_size

    if width <= max_width and height <= max_height:
        return original_size, False

    # アスペクト比を保持してリサイズ
    ratio = min(max_width / width, max_height / height)
    new_width = int(width * ratio)
    new_height = int(height * ratio)

    return (new_width, new_height), True


def _calculate_merge_layout(
    img1_size: Tuple[int, int],
    img2_size: Tuple[int, int],
    direction: str
) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    """結合画像のレイアウトを計算"""
    w1, h1 = img1_size
    w2, h2 = img2_size

    if direction == 'horizontal':
        canvas_size = (w1 + w2, max(h1, h2))
        img2_position = (w1, 0)
    else:  # vertical
        canvas_size = (max(w1, w2), h1 + h2)
        img2_position = (0, h1)

    return canvas_size, img2_position


def _create_compression_info(
    original_size: Tuple[int, int],
    new_size: Tuple[int, int],
    original_format: str,
    quality: int,
    original_data_size: int,
    compressed_data_size: int,
    was_resized: bool
) -> str:
    """圧縮情報テキストを生成"""
    orig_w, orig_h = original_size
    new_w, new_h = new_size

    compression_ratio = (1 - compressed_data_size / original_data_size) * 100

    info = f"元画像: {orig_w}×{orig_h}px ({original_format}), "
    if was_resized:
        info += f"リサイズ後: {new_w}×{new_h}px, "
    info += f"品質: {quality}%, データサイズ: {original_data_size:,} → {compressed_data_size:,} bytes ({compression_ratio:.1f}% 削減)"

    return info


# =============================================================================
# フォーマット検出と変換
# =============================================================================


def create_data_url_from_base64(
    data: str,
    default_format: str = DEFAULT_FORMAT,
    strict: bool = False
) -> Optional[str]:
    """
    Base64データをData URL形式に変換

    Args:
        data: Base64エンコード文字列
        default_format: 形式を認識できない場合のデフォルト形式
        strict: 厳格な検証を行うかどうか

    Returns:
        Data URL文字列、無効な場合はNone

    Raises:
        ValueError: strict=Trueで無効なデータの場合
    """
    # 入力値の検証
    if not _validate_base64_data(data, strict):
        return None

    # 既にURLの場合はそのまま返す
    if data.startswith(('data:', 'http://', 'https://')):
        return data

    # フォーマット検出
    detected_format = _detect_format_from_base64(data)
    format_name = detected_format or default_format
    mime_type = MIME_TYPES.get(format_name, f'image/{default_format}')

    return f"data:{mime_type};base64,{data}"


def get_mime_type_by_extension(file_path: str) -> str:
    """
    ファイル拡張子からMIMEタイプを取得

    Args:
        file_path: ファイルパス

    Returns:
        MIMEタイプ

    Raises:
        ValueError: サポートされていない拡張子の場合
    """
    extension = Path(file_path).suffix.lower().lstrip('.')

    if extension in MIME_TYPES:
        return MIME_TYPES[extension]

    supported = ', '.join(sorted(MIME_TYPES.keys()))
    raise ValueError(f"サポートされていない画像フォーマットです。サポート対象: {supported}")


# =============================================================================
# ファイルエンコーディング
# =============================================================================


def encode_image_file(file_path: str, as_data_url: bool = False) -> str:
    """
    画像ファイルをBase64エンコード

    Args:
        file_path: 画像ファイルのパス
        as_data_url: データURL形式で返すかどうか

    Returns:
        Base64エンコードされた画像データまたはデータURL

    Raises:
        FileNotFoundError: ファイルが存在しない場合
        ValueError: サポートされていない画像フォーマットの場合
    """
    try:
        with open(file_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode('utf-8')
    except FileNotFoundError:
        raise FileNotFoundError(f"画像ファイルが見つかりません: {file_path}")

    if as_data_url:
        mime_type = get_mime_type_by_extension(file_path)
        return f"data:{mime_type};base64,{encoded}"

    return encoded


# =============================================================================
# 画像処理（結合・圧縮）
# =============================================================================


def merge_images(
    first_path: str,
    second_path: str,
    output_path: str,
    direction: str = 'vertical'
) -> None:
    """
    2つの画像を結合

    Args:
        first_path: 最初の画像のパス
        second_path: 2番目の画像のパス
        output_path: 出力画像のパス
        direction: 結合方向（'vertical' または 'horizontal'）

    Raises:
        ValueError: サポートされていない方向の場合
        FileNotFoundError: 画像ファイルが見つからない場合
    """
    if direction not in MERGE_DIRECTIONS:
        supported = ', '.join(MERGE_DIRECTIONS)
        raise ValueError(f"方向は {supported} のいずれかである必要があります")

    try:
        with Image.open(first_path) as img1, Image.open(second_path) as img2:
            img1_rgb = img1.convert("RGB")
            img2_rgb = img2.convert("RGB")

            # レイアウト計算
            canvas_size, img2_pos = _calculate_merge_layout(
                img1_rgb.size, img2_rgb.size, direction
            )

            # 結合画像を作成
            canvas = Image.new('RGB', canvas_size)
            canvas.paste(img1_rgb, (0, 0))
            canvas.paste(img2_rgb, img2_pos)

            # 保存
            canvas.save(output_path)
            print(f"結合画像を保存しました: {output_path}")

    except FileNotFoundError as e:
        raise FileNotFoundError(f"画像ファイルが見つかりません: {e}")


def compress_image_data_url(
    data_url: str,
    quality: int = DEFAULT_QUALITY,
    max_width: int = DEFAULT_MAX_WIDTH,
    max_height: int = DEFAULT_MAX_HEIGHT
) -> Tuple[str, str]:
    """
    データURL画像を圧縮

    Args:
        data_url: 元の画像URL（data:image/...;base64,... 形式）
        quality: JPEG圧縮品質 (1-100)
        max_width: 最大幅
        max_height: 最大高さ

    Returns:
        (圧縮された画像のデータURL, 圧縮情報テキスト)
    """
    try:
        # データURLチェック
        if not data_url.startswith('data:image/'):
            return data_url, ""

        # Base64データ部分を取得
        _, base64_data = data_url.split(',', 1)
        image_data = base64.b64decode(base64_data)

        # 画像を開いて処理
        with Image.open(BytesIO(image_data)) as img:
            # RGBモードに変換
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')

            # 元の画像情報
            original_size = img.size
            original_format = img.format if img.format else "Unknown"

            # リサイズ処理
            new_size, was_resized = _calculate_resize_dimensions(
                original_size, max_width, max_height
            )

            if was_resized:
                img = img.resize(new_size, Image.Resampling.LANCZOS)
                print(f"画像サイズを圧縮: {original_size[0]}x{original_size[1]} -> {new_size[0]}x{new_size[1]}")

            # 圧縮保存
            with BytesIO() as buffer:
                img.save(buffer, format='JPEG', quality=quality, optimize=True)
                compressed_data = buffer.getvalue()

            # Base64エンコード
            compressed_base64 = base64.b64encode(compressed_data).decode('utf-8')
            compressed_url = f"data:image/jpeg;base64,{compressed_base64}"

            # 圧縮情報生成
            info = _create_compression_info(
                original_size, new_size, original_format, quality,
                len(base64_data), len(compressed_base64), was_resized
            )

            print(f"画像圧縮完了: {info}")
            return compressed_url, info

    except Exception as e:
        error_msg = f"画像圧縮中にエラーが発生しました: {e}"
        print(error_msg)
        return data_url, error_msg
