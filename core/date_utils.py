from datetime import datetime, timedelta
from typing import Union

from core.defines import DATE_FORMAT, DATE_TIME_FORMATS


def get_date_key(key: Union[datetime, int, str] = None) -> int:
    if isinstance(key, datetime):
        return int(key.strftime("%Y%m%d"))
    elif isinstance(key, int):
        return key
    elif isinstance(key, str):
        return int(key)

    return int(datetime.now().strftime("%Y%m%d"))


def get_week(date: datetime = None) -> int:
    if date is None:
        date = datetime.now()
    return int(date.strftime("%U"))


def get_month(date: datetime = None) -> int:
    if date is None:
        date = datetime.now()
    return date.month


def get_date():
    return f"{datetime.now():%Y-%m-%d %H:%M:%S}"


def parse_date(date: Union[str, int, float, datetime]):
    if date is None:
        return None
    if isinstance(date, (float, int)):
        return datetime.fromtimestamp(date)
    elif isinstance(date, str):
        return datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    elif isinstance(date, datetime):
        return date
    else:
        raise ValueError(f"This format is not supported: ({date}) type({type(date)})")


def parse_date_time_junction(junction: str) -> (datetime, datetime):
    date_str, time_junc = junction.split(" ")
    date = datetime.strptime(date_str, DATE_FORMAT)
    time_str1, time_str2 = time_junc.split("-")
    print(time_str1, time_str2)
    return parse_date_and_time(time_str1, date), parse_date_and_time(time_str2, date)


def parse_date_and_time(time: str, date: datetime = None) -> datetime:
    if time.startswith("_") or time.startswith("+"):
        return parse_time_delta(time)

    if date is None:
        date_str = datetime.now().strftime(DATE_FORMAT)
    else:
        date_str = date.strftime(DATE_FORMAT)

    if len(time) <= 11:
        date_time_str = f"{date_str} {time.upper()}"
    else:
        date_time_str = time
    for fmt in DATE_TIME_FORMATS:
        try:
            return datetime.strptime(date_time_str, fmt)
        except ValueError:
            pass

    raise ValueError(f"Could not parse time string {time}")


def format_hours(hours: float) -> str:
    h = int(hours)
    decimal = hours - h
    m = int(60 * decimal)
    return f"{h}H {m}M"


def parse_time_delta(date: str) -> datetime:
    """Parse values like -5m or +1h into datetime values"""
    period = date[-1].lower()
    prefix = date[0]
    value = int(date[1:-1])
    if period == "h":
        delta = timedelta(hours=value)
    elif period == "m":
        delta = timedelta(minutes=value)
    else:
        raise ValueError(f"Can only parse hour or minute deltas not {prefix}")
    if prefix == "_":
        return datetime.now() - delta
    else:
        return datetime.now() + delta
