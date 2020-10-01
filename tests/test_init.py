from .fixtures import db
import clok


def test_init(db):
    clok.init()
