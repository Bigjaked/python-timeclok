import pytest
from core.database import DB
from core.models import Clok, Job, Journal, State
import clok


@pytest.fixture()
def db():
    DB.sqlite_db = True
    print(DB.db_uri)
    clok.init(True)
    print(f"clok: {Clok.count()}")
    print(f"Journal: {Journal.count()}")
    print(f"job: {Job.count()}")
    print(f"state: {State.count()}")
