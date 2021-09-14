from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authentication import SessionAuthentication
from loader.models import Environments, TestJobs, TestsStorage, Bugs
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from management.models import Settings
from api.serializers import EnvironmentsSerializer, TestsStorageSerializer, BugsSerializer, SettingsSerializer
from django.http import Http404


class Environment(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = (IsAuthenticated, IsAdminUser)

    def get_object(self, pk):
        try:
            return Environments.objects.get(pk=pk)
        except Environments.DoesNotExist:
            raise Http404

    def post(self, request, pk):
        existing_obj = self.get_object(pk)
        serializer = EnvironmentsSerializer(existing_obj, data=request.data)
        if serializer.is_valid():
            running_jobs = TestJobs.objects.filter(status='1', env=pk).count()
            if "new_name" in request.data.keys():
                if running_jobs > 0:
                    return Response(status=status.HTTP_403_FORBIDDEN)
                serializer.save(remapped_name=request.data['new_name'])
                # # Redis
                # redis = Redis()
                # running_jobs = redis.lrange("running_jobs", 0, 1)
                # for job in running_jobs:
                #     job_str = redis.get_value_from_key_as_str(job)
                #     for k, v in job_str.items():
                #         if k == "env":
                #             if v == existing_obj.name:
                #                 old_data = redis.get(job)
                #                 new_data = old_data[:]
                #                 new_data = ast.literal_eval(new_data.decode("utf-8"))
                #                 new_data["env"] = request.data['new_name']
                #                 redis.set(job, str(new_data).encode("utf-8"))
                return Response(status=status.HTTP_200_OK)
            elif "delete" in request.data.keys():
                if running_jobs > 0:
                    return Response(status=status.HTTP_403_FORBIDDEN)
                serializer.save(remapped_name=None)
                return Response(status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class Job(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = (IsAuthenticated,)

    def get_object(self, uuid):
        try:
            return TestJobs.objects.get(uuid=uuid)
        except TestJobs.DoesNotExist:
            raise Http404

    def delete(self, request, uuid):
        job = self.get_object(uuid=uuid)
        if job.status != 1:
            job.delete()
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return Response(status=status.HTTP_200_OK)


class Users(APIView):
    authentication_classes = [SessionAuthentication, IsAdminUser]
    permission_classes = (IsAuthenticated, )

    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    def delete(self, request, pk):
        user = self.get_object(pk=pk)
        if request.user.pk == user.pk:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if request.user.is_superuser:
            user.delete()
        elif request.user.is_staff:
            if user.is_superuser:
                return Response(status=status.HTTP_403_FORBIDDEN)
            user.delete()
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return Response(status=status.HTTP_200_OK)


class UsersRegenerateToken(APIView):
    authentication_classes = [SessionAuthentication, IsAdminUser]
    permission_classes = (IsAuthenticated, )

    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        user = self.get_object(pk=pk)
        if request.user.is_superuser:
            old_token = Token.objects.get(user=user)
            old_token.delete()
            new_token = Token.objects.create(user=user)
        elif request.user.is_staff:
            if user.is_superuser:
                return Response(status=status.HTTP_403_FORBIDDEN)
            old_token = Token.objects.get(user=user)
            old_token.delete()
            new_token = Token.objects.create(user=user)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return Response(status=status.HTTP_200_OK, data={"token": str(new_token)})


class TestsStorageItem(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = (IsAuthenticated, )

    def get_object(self, pk):
        try:
            return TestsStorage.objects.get(pk=pk)
        except TestsStorage.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        data = TestsStorage.objects.get(pk=pk)
        serializer = TestsStorageSerializer(data)
        return Response(serializer.data)

    def post(self, request, pk):
        serializer = TestsStorageSerializer(self.get_object(pk), data=request.data)
        if serializer.is_valid():
            if "suppress" in request.data.keys():
                serializer.save(data=request.data['suppress'])
                return Response(status=status.HTTP_200_OK)
            if "note" in request.data.keys():
                serializer.save(data=request.data['note'])
                return Response(status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class BugItem(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = (IsAuthenticated,)

    def get_test_storage_item(self, pk):
        try:
            return TestsStorage.objects.get(pk=pk)
        except TestsStorage.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        data = Bugs.objects.filter(test=pk)
        serializer = BugsSerializer(data, many=True)
        return Response(serializer.data)


class BugsManagement(APIView):

    def put(self, request, pk):
        serializer = BugsSerializer(data=request.data)
        if serializer.is_valid():
            tstorage_item = BugItem().get_test_storage_item(pk)
            if "bug" in request.data.keys() and request.data['bug'] != "":
                serializer.save(bug=request.data['bug'].strip(), test=tstorage_item)
                return Response(data=serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        item = Bugs.objects.get(pk=pk)
        item.delete()
        return Response(status=status.HTTP_200_OK)


class SettingsView(APIView):

    def post(self, request):
        serializer = SettingsSerializer(data=request.data)
        try:
            serializer.instance = Settings.objects.get(pk=1)
        except Settings.DoesNotExist:
            pass
        try:
            if serializer.is_valid():
                serializer.save(pk=1, running_jobs_age=request.data['running_jobs_age'].strip())
                return Response(data=serializer.data, status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_400_BAD_REQUEST)


