from datetime import datetime

import typer
from typer import Option, Argument

from core.defines import SECONDS_PER_HOUR
from core.models import Clock, clock_row_header
from core.utils import get_date_key, get_month, get_week
from sqlalchemy.orm.exc import NoResultFound

app = typer.Typer()


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

    elif when is not None:
        Clock.clock_in_when(when)
    else:
        if first:
            Clock.first_clock_in(5)
        else:
            Clock.clock_in()


@app.command()
def out(when: datetime = Option(None, help="Set a specific time to clock in"),):
    if when is not None:
        Clock.clock_out_when(when)
    else:
        Clock.clock_out()


@app.command()
def status(period: str = Option("day", help="the period to print a summary for")):
    if period.lower() == "day":
        records = Clock.get_by_date_key()
        total_hours = sum([i.time_span for i in records]) / SECONDS_PER_HOUR
        print(clock_row_header())
        for i in records:
            print(i)
        print(f"Total Hours Worked: {round(total_hours,3)}")


@app.command()
def clear(period: int = Argument(None, help="the period to clear")):
    if period is not None:
        records = Clock.get_by_date_key(period)
    else:
        records = Clock.get_by_date_key()
    print(f"Deleting {len(records)} records...")
    print(clock_row_header())
    for r in records:
        print(r)
        r.delete()


@app.command()
def delete(id_=Argument(None, help="The id of the time_clock record to delete")):
    if id_ is not None:
        try:
            Clock.delete_by_id(id_)
        except NoResultFound:
            print(f"Record ({id_}) does not exist")
