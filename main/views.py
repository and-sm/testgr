from django.shortcuts import render, redirect
from loader.models import TestJobs, Tests, Screenshots
from loader.redis import Redis
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime
from datetime import timezone as timezone_native
from tools.tools import unix_time_to_datetime
from helpers import helpers

import json


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

    running_jobs_count = helpers.running_jobs_count()

    latest_jobs = TestJobs.objects.select_related('env').order_by('-stop_time').exclude(status='1')[:10]

    latest_jobs_items = []

    for job in latest_jobs:
        job_item = dict()
        job_item['uuid'] = job.uuid
        job_item['time_taken'] = job.get_time_taken()
        job_item['stop_time'] = job.get_stop_time()
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
        job_item['start_time'] = job.get_start_time()
        job_item['env'] = job.get_env()
        job_item['tests_passed'] = job.tests_passed
        job_item['tests_failed'] = job.tests_failed
        job_item['tests_aborted'] = job.tests_aborted
        job_item['tests_skipped'] = job.tests_skipped
        # Fix for None
        if job.tests_not_started is None:
            job.tests_not_started = 0
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
    elif job_object.status == 4 and job_object.time_taken is None:
        time_taken = 0
    else:
        time_taken = None
    env = job_object.get_env()

    status = job_object.status
    tests = job_object.tests.select_related('test')

    # Statistics
    not_started = int(job_object.tests_not_started or 0)
    passed = int(job_object.tests_passed or 0)
    failed = int(job_object.tests_failed or 0)
    skipped = int(job_object.tests_skipped or 0)
    aborted = int(job_object.tests_aborted or 0)
    test_count = int(not_started or 0) + int(passed or 0) + int(failed or 0) + int(skipped or 0) + int(aborted or 0)

    # Framework type
    fw = job_object.fw_type

    # Running jobs count
    running_jobs_count = helpers.running_jobs_count()

    # Custom data
    if job_object.custom_data:
        custom_data = job_object.custom_data
    else:
        custom_data = None

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
                                             'running_jobs_count': running_jobs_count,
                                             'custom_data': custom_data
                                             # 'tests_percentage': job_object.tests_percentage()
                                             })


@login_required()
def test(request, test_uuid):

    test_object = Tests.objects.get(uuid=test_uuid)
    test_job = test_object.job
    test_storage_data = test_object.test
    uuid = test_object.uuid
    if test_object.start_time:
        start_time = test_object.get_start_time()
    else:
        start_time = None
    if test_object.stop_time:
        stop_time = test_object.get_stop_time()
    else:
        stop_time = None
    if test_object.time_taken:
        time_taken = test_object.get_time_taken()
    elif test_object.status == 6 and test_object.time_taken is None:
        time_taken = 0
    else:
        time_taken = None
    env = test_job.get_env()
    if not env:
        env = "Not provided by user"
    elif env == "None":
        env = "Not provided by user"
    status = test_object.status
    msg = test_object.msg
    trace = test_object.trace
    # msg_detailed = test_object.msg_detailed

    identity = test_storage_data.identity
    if test_job.fw_type == 1:
        identity = identity.split(".")
    elif test_job.fw_type == 2:
        identity = identity.split("/")
        for item in identity:
            if "::" in item:
                modified_item = item.split("::")
                identity.remove(item)
                identity.extend(modified_item)
            else:
                pass

    if test_object.test.description:
        description = test_object.test.description
    else:
        description = ""

    if test_object.test.note:
        note = test_object.test.note
    else:
        note = ""

    if test_object.test.suppress:
        suppress = test_object.test.suppress
    else:
        suppress = ""

    if test_storage_data.bugs:
        bugs = test_storage_data.bugs
    else:
        bugs = ""

    # Running jobs count
    running_jobs_count = helpers.running_jobs_count()

    # Last 5 jobs
    data = Tests.objects.filter(test__identity=test_object.test.identity).order_by('-id')[:10]
    last_10_tests = list()
    last_tests_count = 0
    for i in data:
        test_data = list()
        test_data.append(i.uuid)
        test_data.append(i.status)
        test_data.append(i.get_stop_time())
        last_10_tests.append(test_data)
        last_tests_count += 1

    # Last success
    data = Tests.objects.filter(test__identity=test_object.test.identity).filter(status=3).order_by('-id')[:1]
    last_success = list()
    for i in data:
        last_success.append(i.uuid)
        last_success.append(i.status)
        last_success.append(i.get_stop_time())

    # Last fail
    data = Tests.objects.filter(test__identity=test_object.test.identity).filter(status=4).order_by('-id')[:1]
    last_fail = list()
    for i in data:
        last_fail.append(i.uuid)
        last_fail.append(i.status)
        last_fail.append(i.get_stop_time())

    # Previous success
    prev_success = list()
    data = Tests.objects.filter(test__identity=test_object.test.identity,
                                pk__lt=test_object.pk,
                                status=3).order_by('-id')[:1]
    if data is not None:
        for i in data:
            prev_success.append(i.uuid)
            prev_success.append(i.status)
            prev_success.append(i.get_stop_time())

    # Next success
    next_success = list()
    data = Tests.objects.filter(test__identity=test_object.test.identity,
                                pk__gt=test_object.pk,
                                status=3).order_by('id')[:1]
    if data is not None:
        for i in data:
            next_success.append(i.uuid)
            next_success.append(i.status)
            next_success.append(i.get_stop_time())

    # Previous fail
    prev_fail = list()
    data = Tests.objects.filter(test__identity=test_object.test.identity,
                                pk__lt=test_object.pk,
                                status=4).order_by('-id')[:1]
    if data is not None:
        for i in data:
            prev_fail.append(i.uuid)
            prev_fail.append(i.status)
            prev_fail.append(i.get_stop_time())

    # Next fail
    next_fail = list()
    data = Tests.objects.filter(test__identity=test_object.test.identity,
                                pk__gt=test_object.pk,
                                status=4).order_by('id')[:1]
    if data is not None:
        for i in data:
            next_fail.append(i.uuid)
            next_fail.append(i.status)
            next_fail.append(i.get_stop_time())

    # Custom data
    if test_job.custom_data:
        custom_data = sorted(test_job.custom_data.items())
    else:
        custom_data = None

    # Test full path
    full_path = ".".join(identity)

    if test_job.fw_type == 1:
        test_class = test_storage_data.get_test_class_for_nose()
        test_method = test_storage_data.get_test_method_for_nose()
    else:
        test_class = test_storage_data.get_test_class_for_pytest()
        test_method = test_storage_data.get_test_method_for_pytest()

    screenshots = Screenshots.objects.filter(test = test_object)

    return render(request, "main/test.html", {'uuid': uuid,
                                              'start_time': start_time,
                                              'stop_time': stop_time,
                                              'time_taken': time_taken,
                                              'env': env,
                                              'status': status,
                                              'msg': msg,
                                              # 'msg_detailed': msg_detailed,
                                              'identity': identity,
                                              'description': description,
                                              'note': note,
                                              'suppress': suppress,
                                              'bugs': bugs,
                                              'running_jobs_count': running_jobs_count,
                                              'last_10_tests': last_10_tests,
                                              'last_tests_count': last_tests_count,
                                              'last_success': last_success,
                                              'last_fail': last_fail,
                                              'storage_data': test_storage_data,
                                              'test_job': test_job,
                                              'test_class': test_class,
                                              'test_method': test_method,
                                              'trace': trace,
                                              'custom_data': custom_data,
                                              'full_path': full_path,
                                              'prev_f_result': prev_fail,
                                              'next_f_result': next_fail,
                                              'prev_s_result': prev_success,
                                              'next_s_result': next_success,
                                              'screenshots': screenshots})


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
    r = Redis()
    job = "job_" + uuid
    r.connect.lrem("running_jobs", 0, job)
    r.connect.delete("job_" + uuid)

    job_object = TestJobs.objects.get(uuid=uuid)
    job_object.status = 4
    job_object.stop_time = unix_time_to_datetime(int(datetime.now(tz=timezone_native.utc).timestamp() * 1000))
    job_object.time_taken = job_object.stop_time - job_object.start_time

    # Tests
    aborted_tests = 0
    if job_object.tests_in_progress is not None and job_object.tests_in_progress > 0:
        result = Tests.objects.filter(job=job_object, status=2)
        for test_item in result:
            test_item.status = 6
            aborted_tests += 1
            if job_object.tests_in_progress is not None and job_object.tests_in_progress > 0:
                job_object.tests_in_progress = job_object.tests_in_progress - 1
            test_item.save()
    job_object.tests_aborted = aborted_tests
    job_object.save()

    return JsonResponse({"status": "ok"})
