"""This file contains our ORM (Object Relational Mapper) classes for our cloud database
schema. These basically allow us to more easily query and insert into our database
without having to play with sql directly unless we want to. """

from datetime import datetime, timedelta
from typing import Union

from sqlalchemy import Column, DateTime, Integer, TEXT, UniqueConstraint, desc
from sqlalchemy.orm import relationship

from core.database import Model, SurrogatePK, Tracked, reference_col
from core.defines import SECONDS_PER_HOUR
from core.utils import get_date_key, get_month, get_week


class SpanQuery:
    @classmethod
    def get_by_date_key(cls, key: Union[datetime, int, str] = None):
        if key is None:
            dk = get_date_key()
        else:
            dk = get_date_key(key)
        return [i for i in (cls.query().filter(cls.date_key == dk).all())]

    @classmethod
    def get_by_month_key(cls, key: Union[int, str] = None):
        if key is None:
            key = get_month()
        return [i for i in (cls.query().filter(cls.month_key == int(key)).all())]

    @classmethod
    def get_by_week_key(cls, key: Union[int, str] = None):
        if key is None:
            key = get_week()
        return [i for i in (cls.query().filter(cls.week_key == int(key)).all())]

    @classmethod
    def dump(cls):
        return [i.to_dict for i in cls.query().all()]


class Clok(Model, SurrogatePK, SpanQuery):
    __tablename__ = "time_clok"
    __table_args__ = (UniqueConstraint("time_in", "time_out", name="natural"),)
    id = Column(Integer, primary_key=True, autoincrement=True)
    date_key = Column(Integer, default=get_date_key)
    week_key = Column(Integer, default=get_week)
    month_key = Column(Integer, default=get_month)
    time_in = Column(DateTime, default=datetime.now)
    time_out = Column(DateTime, default=None)
    time_span = Column(Integer, default=0)
    journal_entries = relationship("time_clok_journal.clok_id")

    def __init__(
        self,
        date_key: int = None,
        week_key: int = None,
        month_key: int = None,
        time_in: datetime = None,
        time_out: datetime = None,
        journal_msg: str = None,
    ):
        self.date_key = date_key
        self.week_key = week_key
        self.month_key = month_key
        self.time_in = time_in
        self.time_out = time_out
        if journal_msg is not None:
            self.add_journal(journal_msg)

    @property
    def to_dict(self):
        return dict(
            date_key=self.date_key,
            week_key=self.week_key,
            month_key=self.month_key,
            time_in=self.time_in,
            time_out=self.time_out,
            time_span=self.time_span,
            journals=self.get_journals,
        )

    def update_span(self):
        if self.time_in and self.time_out:
            self.time_span = (self.time_out - self.time_in).total_seconds()
            self.save()

    @property
    def span(self):
        return round(self.time_span / SECONDS_PER_HOUR, 3)

    @classmethod
    def get_last_record(cls):
        return cls.query().order_by(desc(cls.time_in)).first()

    @classmethod
    def first_clock_in(cls, minus: int, verbose=False):
        now = datetime.now() - timedelta(minutes=minus)
        if verbose:
            print(f"Clocking you in at {now:%Y-%m-%d %H:%M:%S}")
        a = cls(time_in=now)
        a.save()

    @classmethod
    def clock_in(cls, verbose=False):
        cls.clock_in_when(datetime.now(), verbose)

    @classmethod
    def clock_in_when(cls, when: datetime, verbose=False):
        if verbose:
            print(f"Clocking you in at {when:%Y-%m-%d %H:%M:%S}")
        c = cls(
            time_in=when,
            date_key=get_date_key(when),
            month_key=get_month(when),
            week_key=get_week(when),
        )
        c.save()
        return c

    @classmethod
    def clock_out(cls, verbose=False):
        cls.clock_out_when(datetime.now(), verbose)

    @classmethod
    def clock_out_when(cls, when: datetime, verbose=False):
        if verbose:
            print(f"Clocking you out at {when:%Y-%m-%d %H:%M:%S}")
        r = cls.get_last_record()
        r.time_out = when
        r.update_span()
        r.save()

    @classmethod
    def get_day_hours(cls, key: int = None):
        records = cls.get_by_date_key(key)
        return sum([i.time_span for i in records])

    @classmethod
    def get_week_hours(cls, key: int = None):
        records = cls.get_by_week_key(key)
        return sum([i.time_span for i in records])

    @classmethod
    def get_month_hours(cls, key: int = None):
        records = cls.get_by_month_key(key)
        return sum([i.time_span for i in records])

    def __repr__(self):
        if self.time_out is None:
            time_out = "None"
        else:
            time_out = self.time_out.strftime("%Y-%m-%d %H:%M:%S")

        clok_info = _clock_format_row(
            self.id,
            self.date_key,
            self.month_key,
            self.week_key,
            self.time_in.strftime("%Y-%m-%d %H:%M:%S"),
            time_out,
            self.span,
        )
        journals = [i for i in self.journal_entries]
        if journals:
            j_info = "\n".join([str(i) for i in journals])
            clok_info += f"\n{j_info}"
        return clok_info

    def __str__(self):
        return self.__repr__()

    def add_journal(self, msg: str):
        j = Journal(clock=self, entry=msg)
        j.save()

    @property
    def get_journals(self):
        journals = self.journal_entries
        if journals is not None:
            return [j.entry for j in journals]
        else:
            return None


class Journal(Model, SurrogatePK, Tracked, SpanQuery):
    __tablename__ = "time_clok_journal"

    __table_args__ = (UniqueConstraint("id", "time", name="natural"),)
    clok_id = reference_col("time_clok")
    time = Column(DateTime, default=datetime.now)
    entry = Column(TEXT)

    def __init__(self, clock: Clok, time: datetime = None, entry: str = None):
        self.clok_id = clock.id
        self.time = time
        self.entry = entry

    @property
    def to_dict(self):
        return dict(time=self.time, entry=self.entry)

    def __repr__(self):
        return _journal_format_row(self.id, self.entry)

    def __str__(self):
        return self.__repr__()


def _journal_format_row(journal_id, journal_entry) -> str:
    return f"    - ID: {journal_id:<6} {journal_entry:<64}"  # 80 - ( 6 + 10)


def clock_row_header():
    return _clock_format_row(
        "ID", "Date Key", "Month", "Week", "Clock In", "Clock Out", "Hours "
    )


def _clock_format_row(clok_id, date, month, week, time_in, time_out, time_span) -> str:
    return (
        f"{clok_id:<6} "
        f"{date:<10} "
        f"{month:<6} "
        f"{week:<6} "
        f"{time_in:<20} "
        f"{time_out:<20} "
        f"{time_span:<6}"
    )
