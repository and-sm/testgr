import magic
import json

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.http import JsonResponse
from loader.models import Files
from loader.models import TestJobs, Tests
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.conf import settings


class UploadForJobView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = (IsAuthenticated,)

    def post(self, request, uuid):
        try:
            json_body = json.loads(request.body.decode("utf-8"))
            test = Tests.objects.get(uuid=uuid)
            file = ContentFile(str(json_body), name="file.json")
            instance = Files(file=file)
            instance.test = test
            instance.save()
            return Response(status=status.HTTP_201_CREATED)
        except:
            if 'file' in request.data:
                try:
                    job = TestJobs.objects.get(uuid=uuid)

                    file_obj = request.data['file']

                    """
                    Get MIME by reading the header of the file
                    """
                    initial_pos = file_obj.tell()
                    file_obj.seek(0)
                    mime_type = magic.from_buffer(file_obj.read(1024), mime=True)
                    file_obj.seek(initial_pos)

                    if mime_type not in settings.UPLOAD_MIME_TYPES:
                        return JsonResponse({"detail": "Incorrect file type"}, status=400)

                    instance = Files(file=file_obj)
                    instance.job = job
                    instance.save()

                    return Response(status=status.HTTP_201_CREATED)

                except ObjectDoesNotExist:
                    return JsonResponse({"detail": "Incorrect file type"}, status=400)
            return JsonResponse({"detail": "Incorrect file content"}, status=400)


class UploadForTestView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = (IsAuthenticated,)

    def post(self, request, uuid):

        try:
            json_body = json.loads(request.body.decode("utf-8"))
            test = Tests.objects.get(uuid=uuid)
            file = ContentFile(str(json_body), name="file.json")
            instance = Files(file=file)
            instance.test = test
            instance.save()
            return Response(status=status.HTTP_201_CREATED)
        except:
            if 'file' in request.data:
                try:
                    test = Tests.objects.get(uuid=uuid)

                    file_obj = request.data['file']

                    """
                    Get MIME by reading the header of the file
                    """
                    initial_pos = file_obj.tell()
                    file_obj.seek(0)
                    mime_type = magic.from_buffer(file_obj.read(1024), mime=True)
                    file_obj.seek(initial_pos)

                    if mime_type not in settings.UPLOAD_MIME_TYPES:
                        return JsonResponse({"detail": "Incorrect file type"}, status=400)

                    instance = Files(file=file_obj)
                    instance.test = test
                    instance.save()

                    return Response(status=status.HTTP_201_CREATED)

                except ObjectDoesNotExist:
                    return JsonResponse({"detail": "Incorrect file type"}, status=400)

