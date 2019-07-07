from datetime import datetime
import pytz


# https://stackoverflow.com/a/12589821
# https://stackoverflow.com/a/18724165
def unix_time_to_datetime(timestamp):
    # print("Timestamp: " + str(timestamp))
    timestamp = int(str(timestamp).replace('.', '')[0:13])
    # print("Timestamp updated: " + str(timestamp))
    user_tz = pytz.timezone("UTC")
    utc_dt = datetime.utcfromtimestamp(timestamp/1000).replace(microsecond=(timestamp % 1000) * 1000)\
        .replace(tzinfo=pytz.utc)
    # print("utc_dt: " + str(utc_dt))
    dt = user_tz.normalize(utc_dt.astimezone(user_tz))
    # print("dt: " + str(dt))
    return dt


def normalize_time(obj):
    seconds = obj.total_seconds()
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    if not hours:
        hours = ""
    else:
        hours = str(int(hours)) + "h "
    if not minutes:
        minutes = ""
    else:
        minutes = str(int(minutes)) + "m "
    return hours + minutes + str(int(seconds)) + "s"


def get_hash(obj):
    return hash(obj)


def compare_hash(hash1, hash2):
    if hash1 == hash2:
        return True
    return False
