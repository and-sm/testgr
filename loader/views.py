import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from loader.methods.nose2 import Nose2Loader
from loader.methods.pytest import PytestLoader
from concurrent.futures.thread import ThreadPoolExecutor

pool = ThreadPoolExecutor(max_workers=1)


@csrf_exempt
def loader(request):
    if request.method != 'POST':
        return HttpResponse(status=403)

    body_unicode = request.body.decode('utf-8')
    try:
        data = json.loads(body_unicode)
    except json.JSONDecodeError:
        return HttpResponse(status=400)

    loaders = {
        '1': Nose2Loader,
        '2': PytestLoader,
    }

    current_loader = loaders.get(data.get('fw'))
    if current_loader is None:
        return HttpResponse(status=400)

    actions = {
        'startTestRun': current_loader.start_test_run,
        'stopTestRun': current_loader.stop_test_run,
        'startTestItem': current_loader.start_test,
        'stopTestItem': current_loader.stop_test,
    }

    action = actions.get(data.get('type'))
    if action is None:
        return HttpResponse(status=400)

    pool.submit(action, data)
    return HttpResponse(status=200)
