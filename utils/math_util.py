"""
数学計算のためのユーティリティモジュール
統計計算、数値処理、幾何学計算、単位変換などの機能を提供します。
"""

import math
import statistics
import random
import logging
from typing import List, Union, Tuple, Dict, Any, Optional
from decimal import Decimal, ROUND_HALF_UP
from fractions import Fraction

# ログ設定
logger = logging.getLogger(__name__)

# 定数定義
PI = math.pi
E = math.e
GOLDEN_RATIO = (1 + math.sqrt(5)) / 2


def safe_divide(dividend: Union[int, float], divisor: Union[int, float], 
               default: Union[int, float] = 0) -> Union[int, float]:
    """
    安全な除算を行います（ゼロ除算エラーを回避）。
    
    Args:
        dividend: 被除数
        divisor: 除数
        default: ゼロ除算時のデフォルト値
    
    Returns:
        Union[int, float]: 除算結果またはデフォルト値
    """
    try:
        if divisor == 0:
            logger.warning(f"ゼロ除算が発生しました: {dividend} / {divisor}")
            return default
        return dividend / divisor
    except Exception as e:
        logger.error(f"除算エラー: {str(e)}")
        return default


def round_decimal(value: Union[int, float, str], decimal_places: int = 2,
                 rounding_method: str = 'ROUND_HALF_UP') -> float:
    """
    指定された小数点以下の桁数で四捨五入します。
    
    Args:
        value: 四捨五入する値
        decimal_places: 小数点以下の桁数
        rounding_method: 四捨五入方法
    
    Returns:
        float: 四捨五入された値
    """
    try:
        decimal_value = Decimal(str(value))
        rounding = getattr(Decimal, rounding_method, ROUND_HALF_UP)
        
        if decimal_places == 0:
            quantize_value = Decimal('1')
        else:
            quantize_value = Decimal('0.' + '0' * (decimal_places - 1) + '1')
        
        rounded = decimal_value.quantize(quantize_value, rounding=rounding)
        result = float(rounded)
        
        logger.debug(f"四捨五入完了: {value} → {result} ({decimal_places}桁)")
        return result
        
    except Exception as e:
        logger.error(f"四捨五入エラー: {str(e)}")
        return float(value)


def percentage(part: Union[int, float], total: Union[int, float], 
              decimal_places: int = 2) -> float:
    """
    パーセンテージを計算します。
    
    Args:
        part: 部分
        total: 全体
        decimal_places: 小数点以下の桁数
    
    Returns:
        float: パーセンテージ
    """
    if total == 0:
        logger.warning("全体が0のためパーセンテージを計算できません")
        return 0.0
    
    result = (part / total) * 100
    return round_decimal(result, decimal_places)


def percentage_change(old_value: Union[int, float], new_value: Union[int, float],
                     decimal_places: int = 2) -> float:
    """
    変化率（パーセンテージ）を計算します。
    
    Args:
        old_value: 古い値
        new_value: 新しい値
        decimal_places: 小数点以下の桁数
    
    Returns:
        float: 変化率（パーセンテージ）
    """
    if old_value == 0:
        logger.warning("古い値が0のため変化率を計算できません")
        return 0.0
    
    change = ((new_value - old_value) / old_value) * 100
    return round_decimal(change, decimal_places)


def clamp(value: Union[int, float], min_value: Union[int, float], 
         max_value: Union[int, float]) -> Union[int, float]:
    """
    値を指定された範囲内に制限します。
    
    Args:
        value: 制限する値
        min_value: 最小値
        max_value: 最大値
    
    Returns:
        Union[int, float]: 制限された値
    """
    return max(min_value, min(value, max_value))


def normalize(value: Union[int, float], min_value: Union[int, float], 
             max_value: Union[int, float]) -> float:
    """
    値を0-1の範囲に正規化します。
    
    Args:
        value: 正規化する値
        min_value: 最小値
        max_value: 最大値
    
    Returns:
        float: 正規化された値（0-1）
    """
    if max_value == min_value:
        logger.warning("最大値と最小値が同じため正規化できません")
        return 0.0
    
    return (value - min_value) / (max_value - min_value)


def lerp(start: Union[int, float], end: Union[int, float], t: float) -> float:
    """
    線形補間を行います。
    
    Args:
        start: 開始値
        end: 終了値
        t: 補間係数（0-1）
    
    Returns:
        float: 補間された値
    """
    return start + (end - start) * clamp(t, 0.0, 1.0)


def distance_2d(x1: Union[int, float], y1: Union[int, float],
               x2: Union[int, float], y2: Union[int, float]) -> float:
    """
    2D空間での2点間の距離を計算します。
    
    Args:
        x1, y1: 点1の座標
        x2, y2: 点2の座標
    
    Returns:
        float: 距離
    """
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def distance_3d(x1: Union[int, float], y1: Union[int, float], z1: Union[int, float],
               x2: Union[int, float], y2: Union[int, float], z2: Union[int, float]) -> float:
    """
    3D空間での2点間の距離を計算します。
    
    Args:
        x1, y1, z1: 点1の座標
        x2, y2, z2: 点2の座標
    
    Returns:
        float: 距離
    """
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)


def angle_between_points(x1: Union[int, float], y1: Union[int, float],
                        x2: Union[int, float], y2: Union[int, float]) -> float:
    """
    2点間の角度を計算します（ラジアン）。
    
    Args:
        x1, y1: 点1の座標
        x2, y2: 点2の座標
    
    Returns:
        float: 角度（ラジアン）
    """
    return math.atan2(y2 - y1, x2 - x1)


def degrees_to_radians(degrees: Union[int, float]) -> float:
    """度をラジアンに変換します。"""
    return math.radians(degrees)


def radians_to_degrees(radians: Union[int, float]) -> float:
    """ラジアンを度に変換します。"""
    return math.degrees(radians)


def factorial(n: int) -> int:
    """
    階乗を計算します。
    
    Args:
        n: 階乗を計算する数
    
    Returns:
        int: 階乗の結果
    """
    if n < 0:
        raise ValueError("負の数の階乗は計算できません")
    return math.factorial(n)


def fibonacci(n: int) -> int:
    """
    フィボナッチ数列のn番目の値を計算します。
    
    Args:
        n: 位置（0から開始）
    
    Returns:
        int: フィボナッチ数
    """
    if n < 0:
        raise ValueError("負の位置は指定できません")
    
    if n <= 1:
        return n
    
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    
    return b


def gcd(a: int, b: int) -> int:
    """最大公約数を計算します。"""
    return math.gcd(a, b)


def lcm(a: int, b: int) -> int:
    """最小公倍数を計算します。"""
    return abs(a * b) // gcd(a, b)


def is_prime(n: int) -> bool:
    """
    素数かどうかを判定します。
    
    Args:
        n: 判定する数
    
    Returns:
        bool: 素数の場合True
    """
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    
    return True


def prime_factors(n: int) -> List[int]:
    """
    素因数分解を行います。
    
    Args:
        n: 素因数分解する数
    
    Returns:
        List[int]: 素因数のリスト
    """
    factors = []
    d = 2
    
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
    
    if n > 1:
        factors.append(n)
    
    return factors


def calculate_statistics(numbers: List[Union[int, float]]) -> Dict[str, float]:
    """
    数値リストの統計情報を計算します。
    
    Args:
        numbers: 数値のリスト
    
    Returns:
        Dict[str, float]: 統計情報の辞書
    """
    if not numbers:
        logger.warning("空のリストが渡されました")
        return {}
    
    try:
        stats = {
            'count': len(numbers),
            'sum': sum(numbers),
            'mean': statistics.mean(numbers),
            'median': statistics.median(numbers),
            'min': min(numbers),
            'max': max(numbers),
            'range': max(numbers) - min(numbers)
        }
        
        if len(numbers) > 1:
            stats['stdev'] = statistics.stdev(numbers)
            stats['variance'] = statistics.variance(numbers)
        
        # モードの計算（例外処理付き）
        try:
            stats['mode'] = statistics.mode(numbers)
        except statistics.StatisticsError:
            stats['mode'] = None
        
        logger.debug(f"統計計算完了: {len(numbers)}個の数値")
        return stats
        
    except Exception as e:
        logger.error(f"統計計算エラー: {str(e)}")
        return {}


def moving_average(numbers: List[Union[int, float]], window_size: int) -> List[float]:
    """
    移動平均を計算します。
    
    Args:
        numbers: 数値のリスト
        window_size: ウィンドウサイズ
    
    Returns:
        List[float]: 移動平均のリスト
    """
    if window_size <= 0 or window_size > len(numbers):
        logger.warning("無効なウィンドウサイズです")
        return []
    
    moving_averages = []
    
    for i in range(len(numbers) - window_size + 1):
        window = numbers[i:i + window_size]
        avg = sum(window) / window_size
        moving_averages.append(avg)
    
    logger.debug(f"移動平均計算完了: ウィンドウサイズ={window_size}")
    return moving_averages


def compound_interest(principal: Union[int, float], rate: Union[int, float],
                     time: Union[int, float], compound_frequency: int = 1) -> float:
    """
    複利計算を行います。
    
    Args:
        principal: 元本
        rate: 年利率（小数）
        time: 期間（年）
        compound_frequency: 年間複利回数
    
    Returns:
        float: 複利計算結果
    """
    return principal * (1 + rate / compound_frequency) ** (compound_frequency * time)


def simple_interest(principal: Union[int, float], rate: Union[int, float],
                   time: Union[int, float]) -> float:
    """
    単利計算を行います。
    
    Args:
        principal: 元本
        rate: 年利率（小数）
        time: 期間（年）
    
    Returns:
        float: 単利計算結果
    """
    return principal * (1 + rate * time)


def convert_units(value: Union[int, float], from_unit: str, to_unit: str) -> Optional[float]:
    """
    単位変換を行います。
    
    Args:
        value: 変換する値
        from_unit: 変換元の単位
        to_unit: 変換先の単位
    
    Returns:
        Optional[float]: 変換結果、変換できない場合はNone
    """
    # 長さの変換表（メートル基準）
    length_units = {
        'mm': 0.001,
        'cm': 0.01,
        'm': 1.0,
        'km': 1000.0,
        'inch': 0.0254,
        'ft': 0.3048,
        'yard': 0.9144,
        'mile': 1609.34
    }
    
    # 重量の変換表（グラム基準）
    weight_units = {
        'mg': 0.001,
        'g': 1.0,
        'kg': 1000.0,
        'oz': 28.3495,
        'lb': 453.592,
        'ton': 1000000.0
    }
    
    # 温度変換（特別処理）
    if from_unit == 'celsius' and to_unit == 'fahrenheit':
        return (value * 9/5) + 32
    elif from_unit == 'fahrenheit' and to_unit == 'celsius':
        return (value - 32) * 5/9
    elif from_unit == 'celsius' and to_unit == 'kelvin':
        return value + 273.15
    elif from_unit == 'kelvin' and to_unit == 'celsius':
        return value - 273.15
    
    # 長さ変換
    if from_unit in length_units and to_unit in length_units:
        meters = value * length_units[from_unit]
        result = meters / length_units[to_unit]
        logger.debug(f"長さ変換: {value} {from_unit} → {result} {to_unit}")
        return result
    
    # 重量変換
    if from_unit in weight_units and to_unit in weight_units:
        grams = value * weight_units[from_unit]
        result = grams / weight_units[to_unit]
        logger.debug(f"重量変換: {value} {from_unit} → {result} {to_unit}")
        return result
    
    logger.warning(f"サポートされていない単位変換: {from_unit} → {to_unit}")
    return None


def generate_random_numbers(count: int, min_value: Union[int, float] = 0,
                          max_value: Union[int, float] = 100,
                          number_type: str = 'int') -> List[Union[int, float]]:
    """
    ランダムな数値のリストを生成します。
    
    Args:
        count: 生成する数値の個数
        min_value: 最小値
        max_value: 最大値
        number_type: 数値タイプ（'int', 'float'）
    
    Returns:
        List[Union[int, float]]: ランダム数値のリスト
    """
    numbers = []
    
    for _ in range(count):
        if number_type == 'int':
            numbers.append(random.randint(int(min_value), int(max_value)))
        elif number_type == 'float':
            numbers.append(random.uniform(min_value, max_value))
        else:
            raise ValueError(f"サポートされていない数値タイプ: {number_type}")
    
    logger.debug(f"ランダム数値生成完了: {count}個の{number_type}型数値")
    return numbers


def solve_quadratic(a: Union[int, float], b: Union[int, float], 
                   c: Union[int, float]) -> Tuple[Optional[complex], Optional[complex]]:
    """
    二次方程式 ax² + bx + c = 0 を解きます。
    
    Args:
        a, b, c: 二次方程式の係数
    
    Returns:
        Tuple[Optional[complex], Optional[complex]]: 解のタプル
    """
    if a == 0:
        logger.warning("aが0のため二次方程式ではありません")
        if b == 0:
            return (None, None)
        else:
            # 一次方程式として解く
            x = -c / b
            return (complex(x, 0), None)
    
    discriminant = b ** 2 - 4 * a * c
    
    if discriminant >= 0:
        sqrt_discriminant = math.sqrt(discriminant)
        x1 = (-b + sqrt_discriminant) / (2 * a)
        x2 = (-b - sqrt_discriminant) / (2 * a)
        return (complex(x1, 0), complex(x2, 0))
    else:
        sqrt_discriminant = math.sqrt(-discriminant)
        real_part = -b / (2 * a)
        imaginary_part = sqrt_discriminant / (2 * a)
        x1 = complex(real_part, imaginary_part)
        x2 = complex(real_part, -imaginary_part)
        return (x1, x2)
