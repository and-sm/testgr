from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

import json

from loader.methods.nose2 import Nose2Loader
from loader.methods.pytest import PytestLoader


@csrf_exempt
def loader(request):

    if request.method == 'GET':
        return HttpResponse("Incorrect request")
    elif request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        data = json.loads(body_unicode)

        if '1' in data['fw']:
            data_loader = Nose2Loader(data)
        elif '2' in data['fw']:
            data_loader = PytestLoader(data)
        else:
            data_loader = None

        if 'startTestRun' in data['type']:
            return data_loader.get_start_test_run()
        if 'stopTestRun' in data['type']:
            return data_loader.get_stop_test_run()
        if 'startTestItem' in data['type']:
            return data_loader.get_start_test()
        if 'stopTestItem' in data['type']:
            return data_loader.get_stop_test()

