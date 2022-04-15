from rest_framework import generics

from .models import Mailing, Client, Message
from .serializers import MailingSerializer, MailingGeneralStatisticSerializer, MailingDetailStatisticSerializer
from .serializers import ClientSerializer
from .servises import annotate_mailing_with_message_counters


class ClientListCreateView(generics.ListCreateAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer


class ClientUDView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer


class MailingListCreateView(generics.ListCreateAPIView):
    def get_queryset(self):
        if self.request.method == 'GET':
            return annotate_mailing_with_message_counters()
        else:
            return Mailing.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return MailingGeneralStatisticSerializer
        else:
            return MailingSerializer


class MailingUDView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Mailing.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return MailingDetailStatisticSerializer
        else:
            return MailingGeneralStatisticSerializer

    def get_queryset(self):
        if self.request.method == 'GET':
            return annotate_mailing_with_message_counters()
        else:
            return Mailing.objects.all()
