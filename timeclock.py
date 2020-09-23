#!/home/bigjake/.local/share/virtualenvs/timeclock-VkAi0thm/bin/python
import json
import os
from datetime import datetime

import typer
from typer import Argument

from cli import clock_in, journal
from core.database import BaseModel, DB
from core.defines import APPLICATION_DIRECTORY, DATABASE_FILE
from core.models import Clock, Journal
from core.utils import to_json


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
    dump_dict = {"clock": Clock.dump(), "journal": Journal.dump()}
    s = json.dumps(dump_dict, default=to_json)
    with open(file_path, "w") as f:
        f.write(s)


app.add_typer(clock_in.app, name="clock")
app.add_typer(journal.app, name="journal")
if __name__ == "__main__":
    app()
