from django.shortcuts import render
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from loader.models import Environments
import requests


def main(request):

    envs = Environments.objects.all().exclude(name="")
    return render(request, "management/main.html", {'envs': envs})


def about(request):

    version = "0.11.1"
    response = requests.get(f"https://api.github.com/repos/and-sm/testgr/releases/latest",
                            headers={"Content-Type": "application/json", "User-Agent": "testgr"})

    if response.status_code != 200:
        latest_version = "Unknown"
    else:
        latest_version = response.json()['tag_name']

    return render(request, "management/about.html", {"version": version, "latest_version": latest_version})


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
