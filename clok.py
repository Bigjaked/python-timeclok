import json
import os
from datetime import datetime
from typing import Union

import typer
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from typer import Argument, Option

from core.database import BaseModel, DB, add_items_to_database
from core.defines import APPLICATION_DIRECTORY, DATABASE_FILE, SECONDS_PER_HOUR
from core.models import Clok, Job, Journal, State, clock_row_header
from core.date_utils import (
    get_date,
    get_date_key,
    get_month,
    get_week,
    parse_date_and_time,
    parse_date_time_junction,
    format_hours,
)
from core.utils import to_json


app = typer.Typer()


KEY = Option(
    None,
    help="Specify a key to display, use period to specify key kind. date_key: "
    "'20201010', week_key: '1-52', month_key: '1-12'. default is the current "
    "datekey.",
)
WEEK = Option(False, help="Shortcut to set the period to week")
MONTH = Option(False, help="Shortcut to set the period to month")
ALL_JOBS = Option(False, help="Display records for all jobs")


def get_records_for_period(
    period: str, key: Union[str, int, datetime], all_jobs=False
) -> [Clok]:
    if period.lower() == "day":
        records = Clok.get_by_date_key(key, all_jobs=all_jobs)
    elif period.lower() == "week":
        records = Clok.get_by_week_key(key, all_jobs=all_jobs)
    elif period.lower() == "month":
        records = Clok.get_by_month_key(key, all_jobs=all_jobs)
    else:
        print(f"Error: period must be one of (day, week, month) not {period}")
        raise ValueError()
    return records


@app.command()
def init(testing=False):
    """Initialize the database with the default job"""
    if not os.path.exists(APPLICATION_DIRECTORY):
        os.mkdir(APPLICATION_DIRECTORY)
    if not os.path.exists(DATABASE_FILE) or testing:
        print(f"Creating TimeClok Database and default job.....")
        DB.create_tables(BaseModel)
        try:
            j = Job(name="default")
            j.save()
            s = State()
            s.save()
            s.set_job(j)
        except IntegrityError:
            DB.session.rollback()


@app.command(name="import")
def import_(
    file_path: str = Argument(
        None,
        help="the path of the file to import. Only json files are supported at this "
        "time.",
    )
):
    """Import an exported json file to the database."""
    if os.path.isfile(file_path):
        with open(file_path) as f:
            dump_obj = json.loads(f.read())
        time_clok_jobs = dump_obj["time_clok_jobs"]
        time_clok = dump_obj["time_clok"]
        time_clok_state = dump_obj["time_clok_state"]
        time_clok_journal = dump_obj["time_clok_journal"]

        jobs = []
        for job in time_clok_jobs:
            jobs.append(Job(**job))
        add_items_to_database(jobs)

        cloks = []
        for clok in time_clok:
            cloks.append(Clok(**clok))
        add_items_to_database(cloks)

        journals = []
        for journal in time_clok_journal:
            journals.append(Journal(**journal))
        add_items_to_database(journals)
        try:
            s = State(**time_clok_state[0])
            s.save()
        except IntegrityError:
            pass

    else:
        raise FileNotFoundError(f"'{file_path}' does not exist.")


@app.command()
def dump(file_path: str = Argument(None)):
    """Export the database to a json file"""
    if file_path is None:
        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = f"{APPLICATION_DIRECTORY}/time-clock-dump-{date_str}.json"
    print(f"Dumping the database to > {file_path}")
    dump_dict = {
        "time_clok_jobs": Job.dump(),
        "time_clok_state": State.dump(),
        "time_clok": Clok.dump(),
        "time_clok_journal": Journal.dump(),
    }
    s = json.dumps(dump_dict, default=to_json)
    with open(file_path, "w") as f:
        f.write(s)


@app.command(name="in")
def in_(
    when: str = Argument(None, help="Set a specific time to clock in"),
    out: str = Option(None, help="Set time to clock out"),
    m: str = Option(None, help="Journal Message to add to record"),
):
    """Clock into a job, or add a job day"""
    if when is not None and len(when.split("-")) > 3:
        when, out = parse_date_time_junction(when)
    else:
        if out is not None:
            out = parse_date_and_time(out)
        if when is not None:
            when = parse_date_and_time(when)

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
    when: str = Option(None, help="Set a specific time to clock out"),
    id: str = Option(None, help="The id of the clok instance to clok out of."),
    m: str = Option(None, help="Journal Message to add to record"),
):
    """Clock out from a job"""
    if when:
        when = parse_date_and_time(when)

    if id is not None and when is not None:
        clok = Clok.clok_out_by_id(id, when, verbose=True)
    else:
        clok = Clok.get_last_record()
        if (datetime.now() - clok.time_in).total_seconds() / (60 * 60) > 12:
            typer.confirm(
                "The last clocked in time is more than 12 hours ago, are you\n"
                "are you sure you want to clok out now?"
            )

        if when is not None:
            clok = Clok.clock_out_when(when, verbose=True)
        else:
            clok = Clok.clock_out(verbose=True)
    if m is not None:
        clok.add_journal(m)


@app.command()
def journal(
    msg: str = Argument(None, help="The journal message to record"),
    delete: int = Option(None, help="Delete a message by id"),
    show: bool = Option(True, help="display records for day/week/month/date_key"),
    period: str = Option(
        "day",
        help="The type of time period key to display messages. [day,week,"
        "month] can be combined with 'show' or 'key'.",
    ),
    key: str = KEY,
    id: int = Option(None, help="Add a journal to a specific clok record"),
    week: bool = WEEK,
    month: bool = MONTH,
    all_jobs: bool = ALL_JOBS,
):
    """Show and manage journal entries"""
    if delete is not None:
        id = delete
    if msg is not None:
        if id is not None:
            c = Clok.get_by_id(id)
            if c is not None:
                c.add_journal(msg)
            else:
                raise ValueError(f"Sorry I couldn't find that id :({id})")
        else:
            Clok.get_last_record().add_journal(msg)
    if week:
        period = "week"
    elif month:
        period = "month"

    if show:
        records = get_records_for_period(period, key, all_jobs=all_jobs)
        print(f"Printing Journal entries for the {key or period.lower()}.")
        for i in records:
            for journal in i.journal_entries:
                print(journal)

    if delete is not None:
        print(Journal.get_by_id(id))
        typer.confirm(f"Are you sure that you want to delete this record? ({id})?")
        Journal.delete_by_id(id)


@app.command()
def show(
    period: str = Argument("week", help="the period to print a summary for"),
    key: int = KEY,
    journal: bool = Option(False, help="Print the journal entries as well"),
    week: bool = WEEK,
    month: bool = MONTH,
    all_jobs: bool = ALL_JOBS,
):
    """Display a period of clok ins, the default is the current week"""
    if week:
        period = "week"
    elif month:
        period = "month"

    if period.startswith("d"):
        period = "day"
    elif period.startswith("w"):
        period = "week"
    elif period.startswith("m"):
        period = "month"
    records = get_records_for_period(period, key, all_jobs=all_jobs)
    total_hours = sum([i.time_span for i in records]) / SECONDS_PER_HOUR

    print(clock_row_header())
    for i in records:
        s, hours = i.print(journal)
        if hours:
            total_hours += hours
        print(s)
    print(f"Total Hours Worked: {format_hours(total_hours)}")


@app.command()
def jobs(
    show: bool = Option(True, help="display records for day/week/month/date_key"),
    add: str = Option(None, help="Add a new job, job names are stored lowercase only"),
    switch: str = Option(None, help="Switch to a different job and clock out current"),
):
    """Show and manage different jobs"""
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
def switch(job: str = Argument("default", help="The job to switch too.")):
    """This is a shortcut to jobs --switch"""
    jobs(show=False, add=None, switch=job)


@app.command()
def delete(id_=Argument(None, help="The id of the time_clock record to delete")):
    """Delete a record by record ID."""
    if id_ is not None:
        c = Clok.get_by_id(id_)
        if c is not None:
            print(clock_row_header())
        typer.confirm(f"Are you sure that you want to delete this record? ({id_})?")
        try:
            Clok.delete_by_id(id_)
        except NoResultFound:
            print(f"Record ({id_}) does not exist")


@app.command()
def repair():

    for j in Journal.query().all():
        print(j.clok_id, j.time, j.entry)
        if j.entry is None or j.entry == "show":
            Journal.delete_by_id(j.id)


if __name__ == "__main__":
    init()
    app()
