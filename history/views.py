from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import render
from loader.models import TestJobs
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from helpers import helpers


@login_required()
def history(request):

    job_objects = TestJobs.objects.filter(~Q(status=1)).order_by('-id')

    paginator = Paginator(job_objects, 15)  # Show {num} contacts per page
    page = request.GET.get('page')

    # Running jobs count
    running_jobs_count = helpers.running_jobs_count()

    try:
        items = paginator.get_page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        items = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        items = paginator.page(paginator.num_pages)

    return render(request, 'history/history.html', {'job_objects': items, 'running_jobs_count': running_jobs_count})
