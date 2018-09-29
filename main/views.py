from django.shortcuts import render
from loader.models import TestJobs, Tests


def index(request):

    running_jobs_count = TestJobs.objects.filter(status='1').count()
    return render(request, "main/index.html", {"running_jobs_count": running_jobs_count})


def job(request, job_uuid):

    job_object = TestJobs.objects.get(uuid=job_uuid)
    uuid = job_object.uuid
    start_time = job_object.get_start_time()
    if job_object.stop_time:
        stop_time = job_object.get_stop_time()
    else:
        stop_time = None
    if job_object.time_taken:
        time_taken = job_object.get_time_taken()
    else:
        time_taken = None
    env = job_object.env
    status = job_object.status
    tests = job_object.tests

    # Statistics
    test_count = tests.count()
    not_started = tests.filter(status=1).count()
    passed = tests.filter(status=3).count()
    failed = tests.filter(status=4).count()
    skipped = tests.filter(status=5).count()
    aborted = tests.filter(status=6).count()

    # Framework type
    fw = job_object.fw_type

    # Running jobs count
    running_jobs_count = TestJobs.objects.filter(status='1').count()

    return render(request, "main/job.html", {'uuid': uuid,
                                             'start_time': start_time,
                                             'stop_time': stop_time,
                                             'time_taken': time_taken,
                                             'env': env,
                                             'status': status,
                                             'tests': tests,
                                             'test_count': test_count,
                                             'passed': passed,
                                             'failed': failed,
                                             'skipped': skipped,
                                             'not_started': not_started,
                                             'aborted': aborted,
                                             'fw': fw,
                                             'running_jobs_count': running_jobs_count})


def test(request, test_uuid):

    test_object = Tests.objects.get(uuid=test_uuid)
    uuid = test_object.uuid
    start_time = test_object.start_time.strftime('%H:%M:%S %d-%b-%Y')
    if test_object.stop_time:
        stop_time = test_object.stop_time.strftime('%H:%M:%S %d-%b-%Y')
    else:
        stop_time = None
    if test_object.time_taken:
        time_taken = test_object.get_time_taken()
    else:
        time_taken = None
    env = test_object.job.env
    status = test_object.status
    msg = test_object.msg
    identity = test_object.identity

    # Running jobs count
    running_jobs_count = TestJobs.objects.filter(status='1').count()

    return render(request, "main/test.html", {'uuid': uuid,
                                              'start_time': start_time,
                                              'stop_time': stop_time,
                                              'time_taken': time_taken,
                                              'env': env,
                                              'status': status,
                                              'msg': msg,
                                              'identity': identity,
                                              'running_jobs_count': running_jobs_count})
