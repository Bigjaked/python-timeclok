import json
import os
from datetime import datetime

import typer
from sqlalchemy.orm.exc import NoResultFound
from typer import Argument, Option


from core.database import BaseModel, DB
from core.defines import APPLICATION_DIRECTORY, DATABASE_FILE, SECONDS_PER_HOUR
from core.models import Clok, Journal, clock_row_header, Job, State
from core.utils import get_date_key, get_month, get_week, to_json, get_date
from typing import Union

app = typer.Typer()


KEY = Option(
    None,
    help="Specify a key to display, use period to specify key kind. date_key: "
    "'20201010', week_key: '1-52', month_key: '1-12'. default is the current "
    "datekey.",
)


def get_records_for_period(period: str, key: Union[str, int, datetime]) -> [Clok]:
    if period.lower() == "day":
        records = Clok.get_by_date_key(key)
    elif period.lower() == "week":
        records = Clok.get_by_week_key(key)
    elif period.lower() == "month":
        records = Clok.get_by_month_key(key)
    else:
        print(f"Error: period must be one of (day, week, month) not {period}")
        raise ValueError()
    return records


@app.command()
def init():
    if not os.path.exists(APPLICATION_DIRECTORY):
        os.mkdir(APPLICATION_DIRECTORY)
    if not os.path.exists(DATABASE_FILE):
        print(f"Creating TimeClok Database and default job.....")
        DB.create_tables(BaseModel)
        j = Job(name="default")
        j.save()
        s = State()
        s.save()
        s.set_job(j)


@app.command()
def dump(file_path: str = Argument(None)):
    if file_path is None:
        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = f"{APPLICATION_DIRECTORY}/time-clock-dump-{date_str}.json"
    print(f"Dumping the database to > {file_path}")
    dump_dict = {"clok": Clok.dump()}
    s = json.dumps(dump_dict, default=to_json)
    with open(file_path, "w") as f:
        f.write(s)


@app.command(name="in")
def in_(
    when: datetime = Option(None, help="Set a specific time to clock in"),
    out: datetime = Option(None, help="Set time to clock out"),
    m: str = Option(None, help="Journal Message to add to record"),
):
    if when is not None and out is not None:
        print(f"Creating entry for {when:%Y-%m-%d}: {when:%H:%M:%S} to {out:%H:%M:%S}")
        c = Clok(
            time_in=when,
            time_out=out,
            date_key=get_date_key(when),
            month_key=get_month(when),
            week_key=get_week(when),
        )
        c.update_span()
        c.save()
        if m is not None:
            c.add_journal(m)
    elif when is not None and out is None:
        Clok.clock_in_when(when, verbose=True)
        if m is not None:
            Clok.get_last_record().add_journal(m)
        State.set_clok(Clok.get_last_record())
    else:
        Clok.clock_in(verbose=True)
        if m is not None:
            Clok.get_last_record().add_journal(m)
        State.set_clok(Clok.get_last_record())


@app.command()
def out(
    when: datetime = Option(None, help="Set a specific time to clock in"),
    m: str = Option(None, help="Journal Message to add to record"),
):
    last = Clok.get_last_record()

    if when is not None:
        c = Clok.clock_out_when(when, verbose=True)
        if m is not None:
            c.add_journal(m)
    elif (datetime.now() - last.time_in).total_seconds() / (60 * 60) > 12:
        typer.confirm(
            "The last clocked in time is more than 12 hours ago, are you\n"
            "are you sure you want to clok out now?"
        )
    else:
        Clok.clock_out(verbose=True)
    if m is not None:
        Clok.get_last_record().add_journal(m)


@app.command()
def journal(
    msg: str = Argument(None, help="The journal message to record"),
    delete: int = Option(None, help="Delete a message by id"),
    show: bool = Option(False, help="display records for day/week/month/date_key"),
    period: str = Option(
        "day",
        help="The type of time period key to display messages. [day,week,"
        "month] can be combined with 'show' or 'key'.",
    ),
    key: str = KEY,
):
    if msg is not None:
        Clok.get_last_record().add_journal(msg)

    if show:
        records = get_records_for_period(period, key)
        print(f"Printing Journal entries for {key or period.lower()}")
        for i in records:
            print(i)
    if delete is not None:
        print(Journal.get_by_id(delete))
        typer.confirm(f"Are you sure that you want to delete this record? ({delete})?")
        Journal.delete_by_id(delete)


@app.command()
def show(
    period: str = Argument("week", help="the period to print a summary for"),
    key: int = KEY,
    journal: bool = Option(False, help="Print the journal entries as well"),
):
    records = get_records_for_period(period, key)
    total_hours = sum([i.time_span for i in records]) / SECONDS_PER_HOUR

    print(clock_row_header())
    for i in records:
        s, hours = i.print(journal)
        if hours:
            total_hours += hours
        print(s)
    print(f"Total Hours Worked: {round(total_hours,3)}")


@app.command()
def jobs(
    show: bool = Option(True, help="display records for day/week/month/date_key"),
    add: str = Option(None, help="Add a new job, job names are stored lowercase only"),
    switch: str = Option(None, help="Switch to a different job and clock out current"),
):
    if add or switch:
        show = False
    if show:
        print(Job.print_header())
        current_job = State.get().job
        for j in Job.query().all():
            if j.id == current_job.id:
                print(f"{j} <- Current")
            else:
                print(j)
    elif add is not None:
        try:
            j = Job.query().filter(Job.name == add).one()
            print(f"Job '{add.lower()}' already exists.")
        except NoResultFound:
            print(f"Creating job '{add.lower()}'")
            j = Job(name=add)
            j.save()
    elif switch is not None:
        try:
            s = State.get()
            c = Clok.get_last_record()
            if c is not None:
                if c.time_out is None:
                    print(f"Clocking you out of '{s.job.name}' at {get_date()}")
                    Clok.clock_out()
            print(f"Switching to job '{switch.lower()}'")
            j = Job.query().filter(Job.name == switch.lower()).one()
            State.set_job(j)
        except NoResultFound:
            print(f"Job '{switch}' not found")


@app.command()
def clear(period: int = Argument(None, help="the period to clear")):
    p = get_date_key(period)
    typer.confirm(
        f"Are you sure that you want to delete the records for this day ({p})?"
    )
    if period is not None:
        records = Clok.get_by_date_key(period)
    else:
        records = Clok.get_by_date_key()
    print(f"Deleting {len(records)} records...")
    print(clock_row_header())
    for r in records:
        print(r)
        r.delete()
    Clok.db().commit()


@app.command()
def delete(id_=Argument(None, help="The id of the time_clock record to delete")):
    if id_ is not None:
        typer.confirm(f"Are you sure that you want to delete this record? ({id_})?")
        try:
            Clok.delete_by_id(id_)
        except NoResultFound:
            print(f"Record ({id_}) does not exist")


if __name__ == "__main__":
    init()
    app()
