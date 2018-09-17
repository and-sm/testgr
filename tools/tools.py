from datetime import datetime
from django.utils.timezone import make_aware


def normalize_unix_time(time, remove_date=False):
    try:
        time_from_timestamp = make_aware(datetime.fromtimestamp(time))
        time = datetime.strptime(str(time_from_timestamp), "%Y-%m-%d %H:%M:%S.%f+00:00")
        if remove_date:
            return time.strftime('%H:%M:%S')
    except TypeError:
        return None
    return time.strftime('%H:%M:%S %d-%b-%Y')
