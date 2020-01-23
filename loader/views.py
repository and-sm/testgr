import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from loader.methods.nose2 import Nose2Loader
from loader.methods.pytest import PytestLoader
from concurrent.futures.thread import ThreadPoolExecutor

pool = ThreadPoolExecutor(max_workers=1)


@csrf_exempt
def loader(request):

    if request.method == 'GET':
        return HttpResponse(status=403)
    elif request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        data = json.loads(body_unicode)

        # Nose2
        if 'startTestRun' in data['type'] and '1' in data['fw']:
            pool.submit(Nose2Loader.start_test_run, data)
            return HttpResponse(status=200)
        if 'stopTestRun' in data['type'] and '1' in data['fw']:
            pool.submit(Nose2Loader.stop_test_run, data)
            return HttpResponse(status=200)
        if 'startTestItem' in data['type'] and '1' in data['fw']:
            pool.submit(Nose2Loader.start_test, data)
            return HttpResponse(status=200)
        if 'stopTestItem' in data['type'] and '1' in data['fw']:
            pool.submit(Nose2Loader.stop_test, data)
            return HttpResponse(status=200)

        # Pytest
        if 'startTestRun' in data['type'] and '2' in data['fw']:
            pool.submit(PytestLoader.start_test_run, data)
            return HttpResponse(status=200)
        if 'stopTestRun' in data['type'] and '2' in data['fw']:
            pool.submit(PytestLoader.stop_test_run, data)
            return HttpResponse(status=200)
        if 'startTestItem' in data['type'] and '2' in data['fw']:
            pool.submit(PytestLoader.start_test, data)
            return HttpResponse(status=200)
        if 'stopTestItem' in data['type'] and '2' in data['fw']:
            pool.submit(PytestLoader.stop_test, data)
            return HttpResponse(status=200)

