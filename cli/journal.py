from datetime import datetime

import typer
from typer import Argument, Option

from core.models import Journal, journal_row_header
from sqlalchemy.orm.exc import NoResultFound

app = typer.Typer()


@app.command()
def status(period: str = Option("day", help="the period to print a summary for")):
    if period.lower() == "day":
        records = Journal.get_by_date_key()
        print(f"Printing Journal entries for current Day...")
        print(journal_row_header())
        for i in records:
            print(i)


@app.command()
def clear(period: int = Argument(None, help="the period to clear")):
    if period is not None:
        records = Journal.get_by_date_key(period)
    else:
        records = Journal.get_by_date_key()
    print(f"Deleting {len(records)} records...")
    print(journal_row_header())
    for r in records:
        print(r)
        r.delete()


@app.command()
def delete(id_=Argument(None, help="The id of the time_clock record to delete")):
    if id_ is not None:
        try:
            Journal.delete_by_id(id_)
        except NoResultFound:
            print(f"Record ({id_}) does not exist")
