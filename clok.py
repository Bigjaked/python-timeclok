import json
import os
from datetime import datetime

import typer
from sqlalchemy.orm.exc import NoResultFound
from typer import Argument, Option

from cli import journal
from core.database import BaseModel, DB
from core.defines import APPLICATION_DIRECTORY, DATABASE_FILE, SECONDS_PER_HOUR
from core.models import Clock, Journal, clock_row_header
from core.utils import get_date_key, get_month, get_week, to_json


app = typer.Typer()


@app.command()
def init():
    if not os.path.exists(APPLICATION_DIRECTORY):
        os.mkdir(APPLICATION_DIRECTORY)
    if not os.path.exists(DATABASE_FILE):
        DB.create_tables(BaseModel)


@app.command()
def dump(file_path: str = Argument(None)):
    if file_path is None:
        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = f"{APPLICATION_DIRECTORY}/time-clock-dump-{date_str}.json"
    print(f"Dumping the database to > {file_path}")
    dump_dict = {"clock": Clock.dump(), "journal": Journal.dump()}
    s = json.dumps(dump_dict, default=to_json)
    with open(file_path, "w") as f:
        f.write(s)


@app.command(name="in")
def in_(
    when: datetime = Option(None, help="Set a specific time to clock in"),
    out: datetime = Option(None, help="Set time to clock out"),
    first: bool = Option(
        False,
        help="This is the first clock in of the day,"
        " so set it five minutes in the past",
    ),
):
    if when is not None and out is not None:
        print(
            f"Creating entry for period: {when:%Y-%m-%d %H:%M:%S} to "
            f"{out:%Y-%m-%d %H:%M:%S}"
        )
        a = Clock(
            time_in=when,
            time_out=out,
            date_key=get_date_key(when),
            month_key=get_month(when),
            week_key=get_week(when),
        )
        a.update_span()
        a.save()
    elif when is not None and out is None:
        Clock.clock_in_when(when, verbose=True)
    else:
        if first:
            Clock.first_clock_in(5, verbose=True)
        else:
            Clock.clock_in(verbose=True)


@app.command()
def out(when: datetime = Option(None, help="Set a specific time to clock in"),):
    if when is not None:
        Clock.clock_out_when(when, verbose=True)
    else:
        Clock.clock_out(verbose=True)


@app.command()
def status(
    period: str = Argument("week", help="the period to print a summary for"),
    key: int = Option(None, help="the key to display, defaults to current period"),
):
    if period.lower() == "day":
        records = Clock.get_by_date_key(key)
    elif period.lower() == "week":
        records = Clock.get_by_week_key(key)
    elif period.lower() == "month":
        records = Clock.get_by_month_key(key)
    else:
        print(f"Error: period must be one of (day, week, month) not {period}")
        raise ValueError()

    total_hours = sum([i.time_span for i in records]) / SECONDS_PER_HOUR

    print(clock_row_header())
    for i in records:
        print(i)
    print(f"Total Hours Worked: {round(total_hours,3)}")


@app.command()
def clear(period: int = Argument(None, help="the period to clear")):
    p = get_date_key(period)
    typer.confirm(
        f"Are you sure that you want to delete the records for this day ({p})?"
    )
    if period is not None:
        records = Clock.get_by_date_key(period)
    else:
        records = Clock.get_by_date_key()
    print(f"Deleting {len(records)} records...")
    print(clock_row_header())
    for r in records:
        print(r)
        r.delete()
    Clock.db().commit()


@app.command()
def delete(id_=Argument(None, help="The id of the time_clock record to delete")):
    if id_ is not None:
        try:
            Clock.delete_by_id(id_)
        except NoResultFound:
            print(f"Record ({id_}) does not exist")


app.add_typer(journal.app, name="journal")
if __name__ == "__main__":
    app()
