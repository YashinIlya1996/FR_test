import datetime as dt
from rest_framework import generics

from .models import Mailing, Client
from .serializers import MailingSerializer, MailingGeneralStatisticSerializer, MailingDetailStatisticSerializer
from .serializers import ClientSerializer
from .servises import annotate_mailing_with_message_counters
from .tasks import celery_create_messages_without_sending, celery_send_all_planned_messages


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

    def post(self, request, *args, **kwargs):
        """ Messages create here because in post_save signals don't keep m2m fields.
            m2m_change signals can't help because m2m_fields may be empty """
        response = super().post(request, *args, **kwargs)
        stop_datetime = dt.datetime.fromisoformat(f"{response.data['stop_date']} {response.data['stop_time']}")
        if stop_datetime > dt.datetime.now():
            celery_create_messages_without_sending.apply_async(
                args=[response.data.get("id")],
                expires=stop_datetime,
                link=celery_send_all_planned_messages.s()
            )
        return response


class MailingUDView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Mailing.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return MailingDetailStatisticSerializer
        else:
            return MailingSerializer

    def get_queryset(self):
        if self.request.method == 'GET':
            return annotate_mailing_with_message_counters()
        else:
            return Mailing.objects.all()
