
from datetime import datetime, timedelta

def get_date_label(day_offset):
    """
    Returns a label like 'Jan 14' for a given offset from today.
    offset -1: Yesterday
    offset 0: Today
    offset 1: Tomorrow
    """
    target_date = datetime.now() + timedelta(days=day_offset)
    return target_date.strftime("%b %d")
