from django.shortcuts import render, redirect
from loader.models import TestJobs, Tests
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseForbidden, JsonResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.utils.datastructures import MultiValueDictKeyError
from django.contrib.auth.decorators import login_required
from datetime import timezone, datetime
from tools.tools import unix_time_to_datetime

import json
import redis


def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    else:
        if request.method == "POST":
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user is not None and user.is_active:
                login(request, user)
                return redirect('index')
            else:
                return render(request, "main/login.html")
        else:
            return render(request, "main/login.html")


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required()
@never_cache
def index(request):

    running_jobs_count = TestJobs.objects.filter(status='1').count()

    latest_jobs = TestJobs.objects.select_related('env').order_by('-stop_time').exclude(status='1')[:10]

    latest_jobs_items = []

    for job in latest_jobs:
        job_item = dict()
        job_item['uuid'] = job.uuid
        job_item['time_taken'] = job.get_time_taken()
        job_item['stop_time'] = job.stop_time.strftime('%H:%M:%S %d-%b-%Y')
        job_item['status'] = job.status
        job_item['tests_passed'] = job.tests_passed
        job_item['tests_failed'] = job.tests_failed
        job_item['tests_aborted'] = job.tests_aborted
        job_item['tests_skipped'] = job.tests_skipped
        job_item['tests_not_started'] = job.tests_not_started
        job_item['tests_percentage'] = job.tests_percentage()
        job_item['env'] = job.get_env()
        job_item['status'] = job.status
        latest_jobs_items.append(job_item)

    running_jobs = TestJobs.objects.filter(status='1').order_by('-start_time')
    running_jobs_items = []
    for job in running_jobs:
        job_item = dict()
        job_item['uuid'] = job.uuid
        job_item['start_time'] = job.start_time.strftime('%H:%M:%S %d-%b-%Y')
        job_item['env'] = job.get_env()
        job_item['tests_passed'] = job.tests_passed
        job_item['tests_failed'] = job.tests_failed
        job_item['tests_aborted'] = job.tests_aborted
        job_item['tests_skipped'] = job.tests_skipped
        job_item['tests_not_started'] = job.tests_not_started
        running_jobs_items.append(job_item)

    return render(request, "main/index.html", {"running_jobs_count": running_jobs_count,
                                               "latest_jobs_items": latest_jobs_items,
                                               "running_jobs_items": running_jobs_items})


@login_required()
@never_cache
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
    env = job_object.get_env()

    status = job_object.status
    tests = job_object.tests.select_related('test')

    # Statistics
    test_count = tests.count()
    not_started = tests.filter(status=1).count()
    passed = tests.filter(status=3).count()
    failed = tests.filter(status=4).count()
    skipped = tests.filter(status=5).count()
    aborted = tests.filter(status=6).count()

    negative_tests = failed + aborted

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
                                             'negative_tests': negative_tests,
                                             'fw': fw,
                                             'running_jobs_count': running_jobs_count,
                                             # 'tests_percentage': job_object.tests_percentage()
                                             })


@login_required()
def test(request, test_uuid):

    test_object = Tests.objects.get(uuid=test_uuid)
    uuid = test_object.uuid
    if test_object.start_time:
        start_time = test_object.start_time.strftime('%H:%M:%S %d-%b-%Y')
    else:
        start_time = None
    if test_object.stop_time:
        stop_time = test_object.stop_time.strftime('%H:%M:%S %d-%b-%Y')
    else:
        stop_time = None
    if test_object.time_taken:
        time_taken = test_object.get_time_taken()
    else:
        time_taken = None
    env = test_object.job.get_env()
    status = test_object.status
    msg = test_object.msg
    identity = test_object.test.identity

    if test_object.test.description:
        description = test_object.test.description
    else:
        description = ""

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
                                              'description': description,
                                              'running_jobs_count': running_jobs_count})


@login_required()
@csrf_exempt
def job_force_stop(request):

    if request.method == "POST":
        body_unicode = request.body.decode('utf-8')
        data = json.loads(body_unicode)
        uuid = data['uuid']
    else:
        return HttpResponseForbidden()

    # Redis
    # Remove job uuid from "running_jobs" key immediately
    r = redis.StrictRedis(host='localhost', port=6379)
    job = "job_" + uuid
    r.lrem("running_jobs", 0, job)
    r.delete("job_" + uuid)

    job_object = TestJobs.objects.get(uuid=uuid)
    job_object.status = 4
    job_object.stop_time = unix_time_to_datetime(int(datetime.now(tz=timezone.utc).timestamp() * 1000))
    job_object.time_taken = job_object.stop_time - job_object.start_time
    job_object.save()
    # Tests
    for test_item in job_object.tests.all():
        if test_item.status == 1 or test_item.status == 2:
            test_item.status = 6
            test_item.save()

    return JsonResponse({"status": "ok"})
