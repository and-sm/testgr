from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authentication import SessionAuthentication
from loader.models import Environments, TestJobs
from api.serializers import EnvironmentsSerializer


class Environment(APIView):
    permission_classes = (IsAuthenticated, IsAdminUser)

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


class Job(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = (IsAuthenticated, IsAdminUser)

    def get_object(self, uuid):
        try:
            return TestJobs.objects.get(uuid=uuid)
        except TestJobs.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, uuid):
        job = self.get_object(uuid=uuid)
        if job.status != 1:
            job.delete()
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return Response(status=status.HTTP_200_OK)


