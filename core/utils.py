""" This file contains our SqlAlchemy connection generator function which generates
session factories for our databases. It also has a few utility functions that get uses
throughout the application. """
from datetime import datetime
from typing import Union
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from collections.abc import Hashable
import functools
from multiprocessing import Lock

# from sqlalchemy.ext.compiler import compiles
# from sqlalchemy.sql.expression import Insert
# @compiles(Insert)
# def _prefix_insert_with_ignore(insert, compiler, **kw):
#     return compiler.visit_insert(insert.prefix_with("IGNORE"))


def to_json(data):
    if isinstance(data, (str, int, float, list, tuple, bool)):
        return data
    elif isinstance(data, datetime):
        # return data.strftime("%Y/%m/%d %H:%M")
        return data.timestamp()

    return data


class SqlAlchemyConnGenerator:
    _lock: Lock
    """
    Stores configuration information for sql database connection and implements helper
    methods for the generation of a session maker, sessions and engines.
    Defaults to using the SingletonThreadPool for use in multi-threaded applications.
    """

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
            if isinstance(self._sqlite_db, bool):
                return "sqlite://"
            else:
                return f"sqlite:///{self._sqlite_db}"
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


class Memoized(object):
    """Decorator. Caches a function's return value each time it is called.
   If called later with the same arguments, the cached value is returned
   (not reevaluated).
   """

    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __call__(self, *args):
        if not isinstance(args, Hashable):
            # un-cacheable. a list, for instance.
            # better to not cache than blow up.
            return self.func(*args)
        if args in self.cache:
            return self.cache[args]
        else:
            value = self.func(*args)
            self.cache[args] = value
            return value

    def __repr__(self):
        """Return the function's docstring."""
        return self.func.__doc__

    def __get__(self, obj, objtype):
        """Support instance methods."""
        return functools.partial(self.__call__, obj)


def get_date_key(key: Union[datetime, int, str] = None) -> int:
    if isinstance(key, datetime):
        int(key.strftime("%Y%m%d"))
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
