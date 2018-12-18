from django.shortcuts import render
from loader.models import TestJobs, Tests, Environments
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse


def search(request):

    job_count = TestJobs.objects.all().count()

    environments = Environments.objects.all()
    tests = Tests.objects.values("test").distinct()

    return render(request, "search/search.html", {"job_count": job_count,
                                                  "environments": environments,
                                                  "tests": tests})


@csrf_exempt
def filter_data(request):

    environments = request.POST.get('environments')
    tests = request.POST.get('tests')

    args_list = []
    if environments and environments != 'all':
        Q1 = Q(env=environments)
        args_list.append(Q1)
    else:
        Q1 = ''
    if tests and tests != 'all':
        Q2 = Q(tests__test=tests)
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

    query_set = TestJobs.objects.filter(*(args,)).order_by('-stop_time')
    # will excute, query_set.filter(Q1 | Q2 | Q3)
    # comma , in last after args is mandatory to pass as args here

    datatable_dict = []

    for item in query_set:

        # Stop Time
        stop_time = "<a href=\"job/" + item.uuid + "\" target=\"_blank\">" + item.get_stop_time() + "</a>"

        # Time Taken
        time_taken = "<a href=\"job/" + item.uuid + "\" target=\"_blank\">" + item.get_time_taken() + "</a>"

        # Environment
        env = "<a href=\"job/" + item.uuid + "\" target=\"_blank\">" + item.get_env() + "</a>"

        # Status
        status = item.status

        if status == 1:
            status = "<td><a href=\"job/" + item.uuid + "\" class=\"ui blue basic label\" target=\"_blank\">" \
                                                        "Running</a></td>"
        elif status == 2:
            status = "<td><a href=\"job/" + item.uuid + "\" class=\"ui green basic label\" target=\"_blank\">" \
                                                        "Passed</a></td>"
        elif status == 3:
            status = "<td><a href=\"job/" + item.uuid + "\" class=\"ui red basic label\" target=\"_blank\">" \
                                                        "Failed</a></td>"
        elif status == 4:
            status = "<td><a href=\"job/" + item.uuid + "\" class=\"ui yellow basic label\" target=\"_blank\">" \
                                                        "Stopped</a></td>"

        uuid = item.uuid

        datatable_dict.append({'Stop Date': stop_time, 'Time Taken': time_taken,
                               'Environment': env, 'Status': status, 'uuid': uuid})

    test_data = {"data": datatable_dict}

    return JsonResponse(test_data)