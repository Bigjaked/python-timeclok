""" This file contains our SqlAlchemy connection generator function which generates
session factories for our databases. It also has a few utility functions that get used
throughout the application. """
from datetime import datetime
from multiprocessing import Lock
from typing import Union

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

from core.defines import DATE_FORMAT, DATE_TIME_FORMATS


class SqlAlchemyConnGenerator:
    """
    Stores configuration information for sql database connection and implements helper
    methods for the generation of a session maker, sessions and engines.
    Defaults to using the SingletonThreadPool for use in multi-threaded applications.
    """

    _lock: Lock

    def __init__(
        self,
        user="",
        passwd="",
        db_name="",
        host=None,
        port=None,
        db_type=None,
        **kwargs,
    ):
        self._username = user
        self._password = passwd
        self._db_name = db_name
        self._hostname = host or "127.0.0.1"
        self._host_port = port or 3306
        self._database_type = db_type or "mysql+mysqlconnector"
        self._uri_string = "{0}://{1}:{2}@{3}:{4}/{5}"
        self._lock = Lock()

        if "pool_size" in kwargs:
            self._pool_size = kwargs.get("pool_size")
        else:
            self._pool_size = None
        self._sqlite_db = kwargs.get("sqlite_db", False)
        self._pool_type = kwargs.get("pool_type", QueuePool)
        self._echo = kwargs.get("echo", False)

        self._engine = None
        self._maker = None
        self._current_session = None

    @property
    def sqlite_db(self):
        return self._sqlite_db

    @sqlite_db.setter
    def sqlite_db(self, test):
        self._sqlite_db = test

    @property
    def engine(self) -> Engine:
        if self._engine is None:
            if self._sqlite_db:
                self._engine = create_engine(self.db_uri, echo=self._echo)
            else:
                self._engine = create_engine(
                    self.db_uri,
                    poolclass=self._pool_type,
                    echo=self._echo,
                    pool_size=self._pool_size or 0,
                )
        return self._engine

    @property
    def port(self):
        return self._host_port

    @property
    def db_uri(self):
        if self._sqlite_db:
            if isinstance(self._sqlite_db, str):
                return f"sqlite:///{self._sqlite_db}"
            else:
                return "sqlite://"
        else:
            return self._uri_string.format(
                self._database_type,
                self._username,
                self._password,
                self._hostname,
                self._host_port,
                self._db_name,
            )

    def maker(self):
        if self._maker is None:
            self._maker = sessionmaker(
                bind=self.engine, autocommit=False, autoflush=False
            )
        return self._maker()

    def make_new_session(self):
        self._current_session = self.maker()

    @property
    def session(self):
        if self._current_session is None:
            self.make_new_session()
        return self._current_session

    def create_tables(self, base):
        base.metadata.create_all(self.engine)

    @property
    def locked_session(self):
        # with self._lock:
        return self.session

    @property
    def spawn_unique_session(self):
        """
        This property is used whenever we want to spawn a totally unique session
        instance. This is typically used in cases where we are doing things with threads
        or processes. We also return the lock instance for this connection generator.
        This way the threads or processes can each have their own unique session but can
        still use a shared lock to prevent integrity errors.

        :return:
        """
        class_self = self

        class SessionWrapper:
            """
            This SessionWrapper class mimics the interface of SqlAlchemyConnGenerator so
            that we can use the two interchangeably.
            """

            def __init__(self):
                self._session = None
                self._lock = class_self._lock

            @property
            def session(self):
                if self._session is None:
                    self._session = class_self.maker()
                return self._session

            @property
            def locked_session(self):
                with self._lock:
                    return self.session

        session_wrapper = SessionWrapper()

        return session_wrapper


def to_json(data):
    if isinstance(data, (str, int, float, list, tuple, bool)):
        return data
    elif isinstance(data, datetime):
        # return data.strftime("%Y/%m/%d %H:%M")
        return data.timestamp()

    return data


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


def parse_date_and_time(time: str, date: datetime = None):
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
