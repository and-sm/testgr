from loader.redis import Redis


def running_jobs_count():
    redis = Redis()
    job_list_from_redis = redis.lrange("running_jobs", 0, -1)
    count = len(job_list_from_redis)
    if count > 0:
        return count
    return None