from .fixtures import db
import clok
from core.models import Clok
from datetime import datetime


message = "hi im a message"


def test_clok_in_parse_dates(db):
    cloks = (
        ("2020-09-01 01:00:00", datetime(2020, 9, 1, 1)),
        ("2020-09-01 1:00:00", datetime(2020, 9, 1, 1)),
        ("2020-09-01 01:00", datetime(2020, 9, 1, 1)),
        ("2020-09-01 1:00", datetime(2020, 9, 1, 1)),
        ("2020-09-01 01:00:00am", datetime(2020, 9, 1, 1)),
        ("2020-09-01 1:00:00am", datetime(2020, 9, 1, 1)),
        ("2020-09-01 01:00am", datetime(2020, 9, 1, 1)),
        ("2020-09-01 1:00am", datetime(2020, 9, 1, 1)),
    )
    for date_str, date in cloks:
        clok.in_(date_str, out=None, m=message)
        c = Clok.get_last_record()
        assert c.time_in == date
        assert message in c.get_journals


def test_clok_in_parse_junctions(db):
    cloks = (
        (
            "2020-09-01 01:00:00-02:00:00",
            (datetime(2020, 9, 1, 1), datetime(2020, 9, 1, 2)),
        ),
        (
            "2020-09-02 1:00:00-2:00:00",
            (datetime(2020, 9, 2, 1), datetime(2020, 9, 2, 2)),
        ),
        ("2020-09-03 01:00-02:00", (datetime(2020, 9, 3, 1), datetime(2020, 9, 3, 2))),
        ("2020-09-04 1:00-2:00", (datetime(2020, 9, 4, 1), datetime(2020, 9, 4, 2))),
        (
            "2020-09-05 01:00:00am-02:00:00am",
            (datetime(2020, 9, 5, 1), datetime(2020, 9, 5, 2)),
        ),
        (
            "2020-09-06 1:00:00am-2:00:00am",
            (datetime(2020, 9, 6, 1), datetime(2020, 9, 6, 2)),
        ),
        (
            "2020-09-07 01:00am-02:00am",
            (datetime(2020, 9, 7, 1), datetime(2020, 9, 7, 2)),
        ),
        (
            "2020-09-08 1:00am-2:00am",
            (datetime(2020, 9, 8, 1), datetime(2020, 9, 8, 2)),
        ),
    )
    message = "hi im a message"
    for date_str, (date1, date2) in cloks:
        clok.in_(date_str, out=None, m=message)
        c = Clok.get_most_recent_record()
        print(c.to_dict)
        assert c.time_in == date1
        assert c.time_out == date2
        assert message in c.get_journals
