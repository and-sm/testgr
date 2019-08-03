from django.http import HttpResponse, JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from loader.models import Environments
from api.serializers import EnvironmentsSerializer


@api_view(['POST'])
def environment(request, pk):

    try:
        env = Environments.objects.get(pk=pk)
    except Environments.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "POST":
        serializer = EnvironmentsSerializer(env, data=request.data)
        if serializer.is_valid():
            if "new_name" in request.data.keys():
                serializer.save(remapped_name=request.data['new_name'])
                return Response(status=status.HTTP_200_OK)
            elif "delete" in request.data.keys():
                serializer.save(remapped_name=None)
                return Response(status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class Environment(APIView):

    def get_object(self, pk):
        try:
            return Environments.objects.get(pk=pk)
        except Environments.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def post(self, request, pk):
        serializer = EnvironmentsSerializer(self.get_object(pk), data=request.data)
        if serializer.is_valid():
            if "new_name" in request.data.keys():
                serializer.save(remapped_name=request.data['new_name'])
                return Response(status=status.HTTP_200_OK)
            elif "delete" in request.data.keys():
                serializer.save(remapped_name=None)
                return Response(status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_400_BAD_REQUEST)
