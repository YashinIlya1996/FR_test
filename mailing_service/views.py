from django.shortcuts import get_object_or_404

from rest_framework import generics
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Mailing, Client, Message, ClientTag, OperatorCode
from .serializers import MailingSerializer
from .serializers import ClientSerializer
from .servises import check_valid_number


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
    queryset = Mailing.objects.all()
    serializer_class = MailingSerializer


class MailingUDView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Mailing.objects.all()
    serializer_class = MailingSerializer
