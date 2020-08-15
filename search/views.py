from django.shortcuts import render
from loader.models import TestJobs, TestsStorage, Environments
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from helpers import helpers


@login_required()
def search(request):

    job_count = TestJobs.objects.all().count()

    environments = Environments.objects.all()
    tests = TestsStorage.objects.all()

    # Running jobs count
    running_jobs_count = helpers.running_jobs_count()

    return render(request, "search/search.html", {"job_count": job_count,
                                                  "environments": environments,
                                                  "tests": tests,
                                                  "running_jobs_count": running_jobs_count})


@login_required()
@csrf_exempt
def filter_data(request):

    environments = request.POST.get('environments')
    tests = request.POST.get('tests')

    args_list = []
    if environments and environments != 'all':
        Q1 = Q(env__name=environments)
        args_list.append(Q1)
    else:
        Q1 = ''
    if tests and tests != 'all':
        Q2 = Q(tests__test__test=tests)  # TestJobs -> Tests.test -> TestsStorage.test
        args_list.append(Q2)
    else:
        Q2 = ''
    '''
    if state and state !=  'all':
        Q3 = Q(state=state)
        args_list.append(Q3)
    else:
        Q3 = ''
    '''
    args = Q()  # defining args as empty Q class object to handle empty args_list
    for each_arg in args_list:
        args.add(each_arg, conn_type='AND')

    query_set = TestJobs.objects.filter(*(args,)).order_by('-stop_time').exclude(status=1)
    # will excute, query_set.filter(Q1 | Q2 | Q3)
    # comma , in last after args is mandatory to pass as args here

    datatable_dict = []

    for item in query_set:

        # Stop Time
        stop_time = item.get_stop_time()

        # Time Taken
        time_taken = item.get_time_taken()

        # Environment
        env = item.get_env()

        # Tests
        tests = ""
        if item.tests_passed:
            tests = '<a href="job/{{ job.uuid }}/#table_success_tests" class="ui green basic label">'\
                    + str(item.tests_passed) + '</a>'
        if item.tests_failed:
                tests += '<a href="job/{{ job.uuid }}/#table_failed_tests" class="ui red basic label">'\
                    + str(item.tests_failed) + '</a>'
        if item.tests_skipped:
                tests += '<a href="job/{{ job.uuid }}/#table_skipped_tests" class="ui yellow basic label">'\
                    + str(item.tests_skipped) + '</a>'
        if item.tests_aborted:
                tests += '<a href="job/{{ job.uuid }}/#table_aborted_tests" class="ui darkred basic label">'\
                    + str(item.tests_aborted) + '</a>'
        if item.tests_not_started:
                tests += '<a href="job/{{ job.uuid }}/#table_not_started_tests" class="ui grey basic label">'\
                    + str(item.tests_not_started) + '</a>'

        uuid = item.uuid

        datatable_dict.append({'Stop DateTime': stop_time, 'Time Taken': time_taken,
                               'Environment': env, 'Tests': tests, 'uuid': uuid})

    test_data = {"data": datatable_dict}

    return JsonResponse(test_data)