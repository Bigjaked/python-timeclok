from datetime import datetime
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
    if date is not None:
        date_str = date.strftime(DATE_FORMAT)
    else:
        date_str = datetime.now().strftime(DATE_FORMAT)

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
