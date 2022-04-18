from rest_framework import generics
from django.template.response import SimpleTemplateResponse

from .models import Mailing, Client
from .serializers import MailingSerializer, MailingGeneralStatisticSerializer, MailingDetailStatisticSerializer
from .serializers import ClientSerializer
from .servises import annotate_mailing_with_message_counters, start_new_mailing, update_mailing


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
        """ Messages create here in func 'start_new_mailing' because in post_save signals don't keep m2m fields.
            m2m_change signals can't help because m2m_fields may be empty """
        response = super().post(request, *args, **kwargs)
        start_new_mailing(response)
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

    def put(self, request, *args, **kwargs):
        mailing_id = kwargs["pk"]
        old_mailing = Mailing.objects.prefetch_related('filter_operator_codes', 'filter_client_tags').get(
            pk=mailing_id)

        # m2m_relations changed in pre-saved object too, because saving is lazy
        old_filter_client_tags = set(old_mailing.filter_client_tags.values_list('tag', flat=True))
        old_filter_operator_codes = set(old_mailing.filter_operator_codes.values_list('code', flat=True))
        response = super(MailingUDView, self).put(request, *args, **kwargs)
        updated_mailing = Mailing.objects.get(pk=kwargs["pk"])
        update_mailing(mailing_id, old_filter_client_tags, old_filter_operator_codes, old_mailing, updated_mailing,
                       response)
        return response

    def patch(self, request, *args, **kwargs):
        mailing_id = kwargs["pk"]
        old_mailing = Mailing.objects.prefetch_related('filter_operator_codes', 'filter_client_tags').get(
            pk=mailing_id)

        # m2m_relations changed in pre-saved object too, because saving is lazy
        old_filter_client_tags = set(old_mailing.filter_client_tags.values_list('tag', flat=True))
        old_filter_operator_codes = set(old_mailing.filter_operator_codes.values_list('code', flat=True))
        response = super(MailingUDView, self).patch(request, *args, **kwargs)
        updated_mailing = Mailing.objects.get(pk=kwargs["pk"])
        update_mailing(mailing_id, old_filter_client_tags, old_filter_operator_codes, old_mailing, updated_mailing,
                       response)
        return response


def about(request):
    return SimpleTemplateResponse(template='about.html')