import magic

from rest_framework.exceptions import ParseError
from rest_framework.parsers import FileUploadParser, BaseParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.http import JsonResponse
from django.core.files.base import ContentFile
from loader.models import Files
from loader.models import TestJobs
from django.core.exceptions import ObjectDoesNotExist


# class TextUploadParser(FileUploadParser):
#     media_type = 'text/*'
#
#
# class ZipUploadParser(FileUploadParser):
#     media_type = 'application/zip'


# TODO config
mime_types = ["application/x-7z-compressed",
              "application/zip",
              "application/vnd.ms-excel",
              "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
              "application/x-tar",
              "application/pdf",
              "application/json",
              "application/gzip",
              "text/csv",
              "text/plain",
              "text/html",
              "text/xml",
              "application/x-bzip2",
              "application/x-bzip",
              "application/xml"]

class UploadView(APIView):
    # parser_classes = [ZipUploadParser, TextUploadParser]

    def post(self, request, uuid):
        if 'file' not in request.data:
            raise ParseError("Empty content")

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

            if mime_type not in mime_types:
                return JsonResponse({"detail": "Incorrect file type"}, status=400)

            instance = Files(file=file_obj)
            instance.save()
            job.attachments = instance
            job.save()

            return Response(status=status.HTTP_201_CREATED)

        except ObjectDoesNotExist:
            return JsonResponse({"detail": "Incorrect file type"}, status=400)
