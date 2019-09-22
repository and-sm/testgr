from django.shortcuts import render
from loader.models import Environments
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .forms import AddUserForm
import requests


@login_required()
@staff_member_required
def main(request):

    envs = Environments.objects.all().exclude(name="")
    return render(request, "management/main.html", {'envs': envs})


@login_required()
@staff_member_required
def about(request):

    version = "0.13.0"
    response = requests.get(f"https://api.github.com/repos/and-sm/testgr/releases/latest",
                            headers={"Content-Type": "application/json", "User-Agent": "testgr"})
    if response.status_code != 200:
        latest_version = "Unknown"
    else:
        latest_version = response.json()['tag_name']
    return render(request, "management/about.html", {"version": version, "latest_version": latest_version})


@login_required()
@staff_member_required
def users(request):
    users = User.objects.all()
    return render(request, "management/users.html", {"users": users})


@login_required()
@staff_member_required
def users_add(request):

    if request.method == 'POST':
        form = AddUserForm(request.POST)

        if form.is_valid():

            # user = form.save(commit=False)
            username = form.cleaned_data["username"],
            password = form.cleaned_data["password"],
            is_staff = form.cleaned_data["staff"]
            try:
                form.check_for_spaces()
                validate_password(password[0])
                form.check_password()
            except ValidationError as e:
                form.add_error('password', e)
                return render(request, 'management/users_add.html', {'form': form})

            user_obj = User.objects.create(username=username[0], password=password[0], is_staff=is_staff)
            user_obj.set_password(password[0])
            user_obj.save()
            return HttpResponseRedirect('/management/users')
    else:
        form = AddUserForm()

    return render(request, 'management/users_add.html', {'form': form})



