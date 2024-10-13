from contextlib import contextmanager
from dateutil.relativedelta import relativedelta
from datetime import datetime
import os, time, string, pytz, random


UTC_TZ = pytz.UTC
CHARLOTTE_TZ = pytz.timezone('America/New_York')



@contextmanager
def time_it(info: str, end_text: str=' seconds'):
    """Time the time it takes for the `with` block to execute fully in seconds"""
    start_time = time.time()
    yield
    end_time = time.time()
    print(f"{info} {end_time - start_time:.4f}{end_text}")
    
def get_date_range(start_date: datetime=None, months=0, days=0, hours=0) -> tuple[str, str]:
    """
    Return a tuple with the `(start date, end date)` in format `%Y-%m-%d`
    If the start date is not specified, `None`, it will default to today.
    
    Args:
        start_date (Optional[datetime] | None): The starting date. If `None`, defaults to today.
        months (int): The number of months to add/subtract (default is 0).
        days (int): The number of days to add/subtract (default is 0).
        hours (int): The number of hours to add/subtract (default is 0).
        minutes (int): The number of minutes to add/subtract (default is 0).

    Returns:
        tuple: A tuple containing two dates (start date, end date) formatted as strings `%Y-%m-%d`.
    """
    
    # Use today if no start_date is provided
    if start_date is None:
        start_date = datetime.now()

    end_date = start_date + relativedelta(months=months, days=days, hours=hours)
    
    # Return the formatted start and end date as a tuple
    return (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))

def localize_date(due_date_naive: datetime) -> str:
    """
    Adjusts a due date to America/New_York Timezone, considering daylight saving time (DST).

    Args:
        due_date_naive (datetime): The due date in ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ). Has to be UTC.

    Returns:
        str: The adjusted due date as a string in ISO 8601 format (YYYY-MM-DD HH:MM:SSZ). 
    """
    # Set the naive datetime to be aware (UTC time zone)
    due_date_aware = UTC_TZ.localize(due_date_naive)
    # Convert to Charlotte (Eastern Time)
    due_date_local = due_date_aware.astimezone(CHARLOTTE_TZ)
    
    return due_date_local.strftime("%Y-%m-%d %H:%M:%S")

def generate_random_string(length: int=15) -> str:
    """Generates a random string of 15 characters (digits and letters)."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))



#################################################################
#                                                               #
#                        GET VARIABLES                          #
#                                                               #
#################################################################

def get_canvas_url() -> str:
    """
    Returns the base URL for Canvas to make API calls against.

    :return str: The base URL for Canvas.
    """
    return os.environ.get('CANVAS_BASE_URL', 'https://uncc.instructure.com')

def get_frontend_url() -> str:
    # env 'FRONTEND_URL' is for deployment, second is for local testing
    return os.environ.get('FRONTEND_URL', 'http://localhost:4200')