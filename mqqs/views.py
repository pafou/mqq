from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from mqqs.serializers import MqqSerializer
from mqqs.models import Mqq


class MqqList(APIView):
    """
    List all mq queue and create new ones. 
    Next step: call system command to create mq queue.
    """

    def get(self, request, format=None):
        mqqs = Mqq.objects.all()
        serializer = MqqSerializer(mqqs, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = MqqSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MqqDetail(APIView):
    """
    Retrieve, update or delete a mqq instance.
    """
    def get_object(self, pk):
        try:
            return Mqq.objects.get(pk=pk)
        except Mqq.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        mqq = self.get_object(pk)
        serializer = MqqSerializer(mqq)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        mqq = self.get_object(pk)
        serializer = MqqSerializer(mqq, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        mqq = self.get_object(pk)
        mqq.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)