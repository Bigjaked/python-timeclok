import os

# User directory options
USR_DIR = os.path.expanduser("~")
APPLICATION_DIRECTORY = f"{USR_DIR}/.timeclok/"
DATABASE_FILE = f"{APPLICATION_DIRECTORY}/time-clok.db"
CREDENTIALS_FILE = f"{APPLICATION_DIRECTORY}/credentials.json"

# Date Defines
SECONDS_PER_HOUR = 60.0 * 60.0

DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
TIME_FORMATS = (
    "%I:%M:%S%p",  # 07:45:00PM
    "%-I:%M:%S%p",  # 7:45:00PM
    "%H:%M:%S",  # 17:45:00
    "%-H:%M:%S",  # 9:45:00
    "%I:%M%p",  # 07:45PM
    "%-I:%M%p",  # 7:45PM
    "%H:%M",  # 17:45
)
DATE_TIME_FORMATS = []
for fmt in TIME_FORMATS:
    DATE_TIME_FORMATS.append(f"{DATE_FORMAT} {fmt}")
