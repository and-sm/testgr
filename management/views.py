from django.shortcuts import render
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt

from loader.models import Environments


def main(request):

    envs = Environments.objects.all().exclude(name="")
    return render(request, "management/main.html", {'envs': envs})


def about(request):

    version = "0.10.2"
    return render(request, "management/about.html", {"version": version})


@csrf_exempt
def api_remap_env(request):

    if request.method == 'POST':
        env_id = request.POST['id']
        new_name = request.POST['new_name']
        if new_name is not "":
            try:
                obj = Environments.objects.get(pk=env_id)
                obj.remapped_name = new_name
                obj.save()
                return HttpResponse(status=200)
            except ObjectDoesNotExist:
                return HttpResponse(status=403)
        else:
            return HttpResponse(status=403)
    else:
        return HttpResponse(status=403)


@csrf_exempt
def api_delete_env(request):

    if request.method == 'POST':
        env_id = request.POST['id']
        try:
            obj = Environments.objects.get(pk=env_id)
            obj.remapped_name = None
            obj.save()
            return HttpResponse(status=200)
        except ObjectDoesNotExist:
            return HttpResponse(status=403)
    else:
        return HttpResponse(status=403)
