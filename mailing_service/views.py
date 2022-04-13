from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Mailing, Client, Message
from .serializers import MailingSerializer, ClientSerializer, MessageSerializer


class MailingListView(APIView):
    def get(self, request):
        mailings = Mailing.objects.all()
        serializer = MailingSerializer(mailings, many=True)
        return Response(serializer.data)


class ClientListView(APIView):
    def get(self, request):
        clients = Client.objects.all()
        serializer = ClientSerializer(clients, many=True)
        return Response(serializer.data)


class ClientCreateView(APIView):
    def post(self, request):
        client = ClientSerializer(data=request.data)
        if client.is_valid(raise_exception=True):
            client.save()
            return Response(status=201, data=client.data)
        return Response(status=418)


