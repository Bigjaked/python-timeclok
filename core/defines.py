import os

# User directory options
USR_DIR = os.path.expanduser("~")
APPLICATION_DIRECTORY = f"{USR_DIR}/.timeclock/"
DATABASE_FILE = f"{APPLICATION_DIRECTORY}/time-clock.db"

# Date Defines
SECONDS_PER_HOUR = 60.0 * 60.0
