from rest_framework import generics
from django.db.models import Count, Q

from .models import Mailing, Client, Message
from .serializers import MailingSerializer, MailingGeneralStatisticSerializer, MailingDetailStatisticSerializer
from .serializers import ClientSerializer
from .servises import annotate_mailing_with_message_counters


#
# class MailingListView(APIView):
#     def get(self, request):
#         mailings = Mailing.objects.all()
#         serializer = MailingSerializer(mailings, many=True)
#         return Response(serializer.data)
#
#     def post(self, request):
#         mailing = MailingSerializer(data=request.data)
#         mailing.is_valid(raise_exception=True)
#         mailing.save()
#         return Response({"post": mailing.data})
#
#
# class ClientListAndCreateView(APIView):
#     def get(self, request):
#         clients = Client.objects.all()
#         serializer = ClientSerializer(clients, many=True)
#         return Response(serializer.data)
#
#     def post(self, request):
#         client = ClientSerializer(data=request.data)
#         if client.is_valid(raise_exception=True):
#             client.save()
#             return Response(status=201, data=client.data)
#         return Response(status=418)
#
#
# class ClientView(APIView):
#     def get(self, request, *args, **kwargs):
#         client_pk = kwargs.get("pk")
#         client = get_object_or_404(Client, pk=client_pk)
#         serializer = ClientSerializer(client, many=True)
#         return Response(serializer.data)
#
#     def put(self, request, *args, **kwargs):
#         client_pk = kwargs.get("pk")
#         client = get_object_or_404(Client, pk=client_pk)
#         serializer = ClientSerializer(data=request.data, instance=client)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response({"post": serializer.data})
#
#     def patch(self, request, *args, **kwargs):
#         client_pk = kwargs.get("pk")
#         client = get_object_or_404(Client, pk=client_pk)
#         serializer = ClientSerializer(data=request.data, instance=client, partial=True)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response({"post": serializer.data})
#
#     def delete(self, request, *args, **kwargs):
#         client_pk = kwargs.get("pk")
#         client = get_object_or_404(Client, pk=client_pk)
#         client.delete()
#         return Response({"post": f"delete client {client_pk} ({client.phone_number})"})

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
