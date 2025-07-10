"""
日付・時刻操作のためのユーティリティモジュール
日付の変換、フォーマット、計算、検証などの機能を提供します。
"""

import re
import logging
from datetime import datetime, date, time, timedelta, timezone
from typing import Optional, Union, List, Dict, Any
from dateutil import parser, tz
from dateutil.relativedelta import relativedelta

# ログ設定
logger = logging.getLogger(__name__)

# 定数定義
DEFAULT_DATE_FORMAT = '%Y-%m-%d'
DEFAULT_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DEFAULT_TIME_FORMAT = '%H:%M:%S'
ISO_FORMAT = '%Y-%m-%dT%H:%M:%S'
JAPANESE_DATE_FORMAT = '%Y年%m月%d日'
JAPANESE_DATETIME_FORMAT = '%Y年%m月%d日 %H時%M分%S秒'

# 日本のタイムゾーン
JST = timezone(timedelta(hours=9))


def now_jst() -> datetime:
    """
    現在の日本時間を取得します。
    
    Returns:
        datetime: 現在の日本時間
    """
    return datetime.now(JST)


def today_jst() -> date:
    """
    今日の日付（日本時間）を取得します。
    
    Returns:
        date: 今日の日付
    """
    return now_jst().date()


def parse_date_string(date_string: str, format_hint: Optional[str] = None) -> Optional[datetime]:
    """
    文字列を日付オブジェクトに変換します。
    
    Args:
        date_string: 日付文字列
        format_hint: フォーマットのヒント
    
    Returns:
        Optional[datetime]: パースされた日付オブジェクト
    """
    if not date_string or not date_string.strip():
        return None
    
    try:
        # フォーマットヒントがある場合は最初に試行
        if format_hint:
            try:
                return datetime.strptime(date_string.strip(), format_hint)
            except ValueError:
                logger.debug(f"フォーマットヒントでのパースに失敗: {format_hint}")
        
        # dateutil.parserを使用した柔軟なパース
        parsed_date = parser.parse(date_string.strip())
        logger.debug(f"日付パース成功: {date_string} -> {parsed_date}")
        return parsed_date
        
    except (ValueError, parser.ParserError) as e:
        logger.warning(f"日付パースエラー: {date_string} - {str(e)}")
        return None


def format_date(dt: Union[datetime, date], format_string: str = DEFAULT_DATE_FORMAT) -> str:
    """
    日付オブジェクトを指定されたフォーマットで文字列に変換します。
    
    Args:
        dt: 日付オブジェクト
        format_string: フォーマット文字列
    
    Returns:
        str: フォーマットされた日付文字列
    """
    try:
        if isinstance(dt, date) and not isinstance(dt, datetime):
            # dateオブジェクトの場合はdatetimeに変換
            dt = datetime.combine(dt, time.min)
        
        formatted = dt.strftime(format_string)
        logger.debug(f"日付フォーマット成功: {dt} -> {formatted}")
        return formatted
        
    except Exception as e:
        logger.error(f"日付フォーマットエラー: {str(e)}")
        return str(dt)


def format_japanese_date(dt: Union[datetime, date], include_time: bool = False) -> str:
    """
    日付を日本語形式でフォーマットします。
    
    Args:
        dt: 日付オブジェクト
        include_time: 時刻も含めるかどうか
    
    Returns:
        str: 日本語形式の日付文字列
    """
    format_str = JAPANESE_DATETIME_FORMAT if include_time else JAPANESE_DATE_FORMAT
    return format_date(dt, format_str)


def add_business_days(start_date: Union[datetime, date], days: int) -> date:
    """
    営業日を加算します（土日を除く）。
    
    Args:
        start_date: 開始日
        days: 加算する営業日数
    
    Returns:
        date: 計算結果の日付
    """
    if isinstance(start_date, datetime):
        current_date = start_date.date()
    else:
        current_date = start_date
    
    remaining_days = abs(days)
    direction = 1 if days >= 0 else -1
    
    while remaining_days > 0:
        current_date += timedelta(days=direction)
        # 土曜日(5)と日曜日(6)以外の場合
        if current_date.weekday() < 5:
            remaining_days -= 1
    
    logger.debug(f"営業日計算完了: {start_date} + {days}営業日 = {current_date}")
    return current_date


def get_age(birth_date: Union[datetime, date], reference_date: Optional[Union[datetime, date]] = None) -> int:
    """
    年齢を計算します。
    
    Args:
        birth_date: 生年月日
        reference_date: 基準日（デフォルト: 今日）
    
    Returns:
        int: 年齢
    """
    if reference_date is None:
        reference_date = today_jst()
    
    if isinstance(birth_date, datetime):
        birth_date = birth_date.date()
    if isinstance(reference_date, datetime):
        reference_date = reference_date.date()
    
    age = reference_date.year - birth_date.year
    
    # 誕生日がまだ来ていない場合は1歳引く
    if (reference_date.month, reference_date.day) < (birth_date.month, birth_date.day):
        age -= 1
    
    logger.debug(f"年齢計算完了: {birth_date} -> {age}歳 (基準日: {reference_date})")
    return age


def get_date_range(start_date: Union[datetime, date], end_date: Union[datetime, date]) -> List[date]:
    """
    指定された期間の日付リストを生成します。
    
    Args:
        start_date: 開始日
        end_date: 終了日
    
    Returns:
        List[date]: 日付のリスト
    """
    if isinstance(start_date, datetime):
        start_date = start_date.date()
    if isinstance(end_date, datetime):
        end_date = end_date.date()
    
    if start_date > end_date:
        start_date, end_date = end_date, start_date
    
    date_list = []
    current_date = start_date
    
    while current_date <= end_date:
        date_list.append(current_date)
        current_date += timedelta(days=1)
    
    logger.debug(f"日付範囲生成完了: {start_date} - {end_date} ({len(date_list)}日間)")
    return date_list


def get_month_boundaries(dt: Union[datetime, date]) -> tuple[date, date]:
    """
    指定された日付の月の開始日と終了日を取得します。
    
    Args:
        dt: 基準となる日付
    
    Returns:
        tuple[date, date]: (月初日, 月末日)
    """
    if isinstance(dt, datetime):
        dt = dt.date()
    
    # 月初日
    first_day = dt.replace(day=1)
    
    # 月末日
    if dt.month == 12:
        last_day = dt.replace(year=dt.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        last_day = dt.replace(month=dt.month + 1, day=1) - timedelta(days=1)
    
    logger.debug(f"月境界取得完了: {dt} -> {first_day} - {last_day}")
    return first_day, last_day


def get_quarter_boundaries(dt: Union[datetime, date]) -> tuple[date, date]:
    """
    指定された日付の四半期の開始日と終了日を取得します。
    
    Args:
        dt: 基準となる日付
    
    Returns:
        tuple[date, date]: (四半期開始日, 四半期終了日)
    """
    if isinstance(dt, datetime):
        dt = dt.date()
    
    # 四半期の開始月を計算
    quarter_start_month = ((dt.month - 1) // 3) * 3 + 1
    
    # 四半期開始日
    quarter_start = dt.replace(month=quarter_start_month, day=1)
    
    # 四半期終了日
    if quarter_start_month == 10:  # Q4
        quarter_end = dt.replace(year=dt.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        quarter_end = dt.replace(month=quarter_start_month + 3, day=1) - timedelta(days=1)
    
    logger.debug(f"四半期境界取得完了: {dt} -> {quarter_start} - {quarter_end}")
    return quarter_start, quarter_end


def is_weekend(dt: Union[datetime, date]) -> bool:
    """
    指定された日付が週末（土日）かどうかを判定します。
    
    Args:
        dt: 判定する日付
    
    Returns:
        bool: 週末の場合True
    """
    if isinstance(dt, datetime):
        dt = dt.date()
    
    return dt.weekday() >= 5  # 土曜日(5)または日曜日(6)


def is_business_day(dt: Union[datetime, date]) -> bool:
    """
    指定された日付が営業日（平日）かどうかを判定します。
    
    Args:
        dt: 判定する日付
    
    Returns:
        bool: 営業日の場合True
    """
    return not is_weekend(dt)


def time_until(target_datetime: datetime, from_datetime: Optional[datetime] = None) -> Dict[str, int]:
    """
    指定された日時までの残り時間を計算します。
    
    Args:
        target_datetime: 目標日時
        from_datetime: 基準日時（デフォルト: 現在時刻）
    
    Returns:
        Dict[str, int]: 残り時間の辞書（days, hours, minutes, seconds）
    """
    if from_datetime is None:
        from_datetime = now_jst()
    
    if target_datetime.tzinfo is None:
        target_datetime = target_datetime.replace(tzinfo=JST)
    if from_datetime.tzinfo is None:
        from_datetime = from_datetime.replace(tzinfo=JST)
    
    delta = target_datetime - from_datetime
    
    if delta.total_seconds() < 0:
        # 過去の日時の場合
        return {'days': 0, 'hours': 0, 'minutes': 0, 'seconds': 0}
    
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    result = {
        'days': days,
        'hours': hours,
        'minutes': minutes,
        'seconds': seconds
    }
    
    logger.debug(f"残り時間計算完了: {from_datetime} -> {target_datetime} = {result}")
    return result


def format_duration(seconds: int) -> str:
    """
    秒数を人間が読みやすい形式にフォーマットします。
    
    Args:
        seconds: 秒数
    
    Returns:
        str: フォーマットされた期間文字列
    """
    if seconds < 0:
        return "0秒"
    
    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    parts = []
    if days > 0:
        parts.append(f"{days}日")
    if hours > 0:
        parts.append(f"{hours}時間")
    if minutes > 0:
        parts.append(f"{minutes}分")
    if seconds > 0 or not parts:
        parts.append(f"{seconds}秒")
    
    return "".join(parts)


def convert_timezone(dt: datetime, target_tz: Union[str, timezone]) -> datetime:
    """
    日時を指定されたタイムゾーンに変換します。
    
    Args:
        dt: 変換する日時
        target_tz: 目標タイムゾーン
    
    Returns:
        datetime: 変換された日時
    """
    try:
        if isinstance(target_tz, str):
            target_tz = tz.gettz(target_tz)
        
        if dt.tzinfo is None:
            # タイムゾーン情報がない場合はJSTとして扱う
            dt = dt.replace(tzinfo=JST)
        
        converted = dt.astimezone(target_tz)
        logger.debug(f"タイムゾーン変換完了: {dt} -> {converted}")
        return converted
        
    except Exception as e:
        logger.error(f"タイムゾーン変換エラー: {str(e)}")
        return dt


def validate_date_range(start_date: Union[datetime, date], 
                       end_date: Union[datetime, date]) -> bool:
    """
    日付範囲の妥当性を検証します。
    
    Args:
        start_date: 開始日
        end_date: 終了日
    
    Returns:
        bool: 妥当な範囲の場合True
    """
    if isinstance(start_date, datetime):
        start_date = start_date.date()
    if isinstance(end_date, datetime):
        end_date = end_date.date()
    
    return start_date <= end_date


def get_relative_date_description(dt: Union[datetime, date], 
                                reference_date: Optional[Union[datetime, date]] = None) -> str:
    """
    相対的な日付の説明を取得します（例：「昨日」「来週」など）。
    
    Args:
        dt: 対象日付
        reference_date: 基準日（デフォルト: 今日）
    
    Returns:
        str: 相対的な日付の説明
    """
    if reference_date is None:
        reference_date = today_jst()
    
    if isinstance(dt, datetime):
        dt = dt.date()
    if isinstance(reference_date, datetime):
        reference_date = reference_date.date()
    
    delta = (dt - reference_date).days
    
    if delta == 0:
        return "今日"
    elif delta == 1:
        return "明日"
    elif delta == -1:
        return "昨日"
    elif delta == 2:
        return "明後日"
    elif delta == -2:
        return "一昨日"
    elif 3 <= delta <= 6:
        return f"{delta}日後"
    elif -6 <= delta <= -3:
        return f"{abs(delta)}日前"
    elif 7 <= delta <= 13:
        return "来週"
    elif -13 <= delta <= -7:
        return "先週"
    elif delta > 13:
        return f"{delta}日後"
    else:
        return f"{abs(delta)}日前"
