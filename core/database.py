"""This file contains database mixins and database session factories for both the local
and cloud databases that can be uses throughout the application. """
import json
from datetime import datetime
from typing import Union

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Query
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError

from core.utils import SqlAlchemyConnGenerator
from core.defines import DATABASE_FILE

# if this is not set to a filename then it will default to an in memory db by passing
# true to the sqlite_db keyword.
DB = SqlAlchemyConnGenerator(sqlite_db=DATABASE_FILE)

BaseModel = declarative_base()


def add_items_to_database(items):
    for item in items:
        _add_item(item)


def _add_item(item):
    try:
        DB.session.add(item)
        DB.session.commit()
    except IntegrityError:
        DB.session.rollback()


class CRUDMixin(object):
    """Mixin that adds convenience methods for CRUD (create, read, update,
    delete) operations."""

    _repr_keys = ["id"]
    _db_instance = None

    @classmethod
    def create(cls, **kwargs):
        """Create a new record and save it the database."""
        instance = cls(**kwargs)
        return instance.save()

    def update(self, commit=True, **kwargs):
        """Update specific fields of a record."""
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        return commit and self.save() or self

    def save(self, commit=True):
        """Save the record."""
        self._db_instance.locked_session.add(self)
        if commit:
            self._db_instance.locked_session.commit()
        return self

    def delete(self, commit=True):
        """Remove the record from the database."""
        self._db_instance.locked_session.delete(self)
        if commit:
            self._db_instance.locked_session.commit()

    def __repr__(self):
        d = {}
        for key in self._repr_keys:
            d[key] = getattr(self, key)
        s = ", ".join([f"{k}: {v}" for k, v in d.items()])
        return f"<{self.__class__.__name__} {s}>"


class Model(CRUDMixin, BaseModel):
    """Base model class that includes CRUD convenience methods."""

    __abstract__ = True
    _db_instance = DB

    @classmethod
    def query(cls) -> Query:
        return cls._db_instance.locked_session.query(cls)

    @classmethod
    def db(cls):
        return cls._db_instance.locked_session

    @classmethod
    def count(self):
        return self.query().count()

    @property
    def columns(self):
        return [column for column in dict(self.__table__.columns).keys()]

    @property
    def to_dict(self):
        d = {}
        for name in self.columns:
            try:
                value = self.__getattribute__(name)
            except AttributeError:
                value = self.__dict__.get(name, None)
            d[name] = value
        return d

    def to_json(self):
        return json.dumps(self.to_dict)


class Tracked(object):
    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, onupdate=datetime.utcnow)


class JsonData(object):
    _data = Column("data", JSON, default={})

    @property
    def data(self) -> Union[dict, None]:
        if isinstance(self._data, dict):
            return self._data
        elif isinstance(self._data, (str, bytes, bytearray)):
            return json.loads(self._data)
        elif self._data is None:
            return None
        else:
            raise TypeError(f"_data not valid: {type(self._data)}, {self._data}")

    @data.setter
    def data(self, data: dict):
        d = self.data
        if self._data is not None:
            self._data = d.update(data)
        else:
            self._data = data


# From Mike Bayer's "Building the app" talk
# https://speakerdeck.com/zzzeek/building-the-app
class SurrogatePK(object):
    """A mixin that adds a surrogate integer 'primary key' column named
    ``id`` to any declarative-mapped class."""

    __table_args__ = {"extend_existing": True}
    id = Column(Integer, primary_key=True, autoincrement=True)

    @classmethod
    def get_by_id(cls, record_id):
        """Get record by ID."""
        if any(
            (
                isinstance(record_id, str) and record_id.isdigit(),
                isinstance(record_id, (int, float)),
            )
        ):
            try:
                return cls.query().filter(cls.id == int(record_id)).one()
            except NoResultFound:
                pass
        return None

    @classmethod
    def delete_by_id(cls, record_id: int):
        if any(
            (
                isinstance(record_id, str) and record_id.isdigit(),
                isinstance(record_id, (int, float)),
            )
        ):
            cls.query().filter(cls.id == int(record_id)).delete()
            cls.db().commit()


def reference_col(tablename, nullable=False, pk_name="id", **kwargs):
    """Column that adds primary key foreign key reference.
    Usage: ::
        category_id = reference_col('category')
        category = relationship('Category', backref='categories')
    """
    return Column(
        ForeignKey("{0}.{1}".format(tablename, pk_name)), nullable=nullable, **kwargs
    )
