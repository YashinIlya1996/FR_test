from rest_framework import serializers

from .models import Mailing, Client, Message, ClientTag, OperatorCode
from .servises import check_valid_number, create_related_if_not_exist


class MessageSerializer(serializers.ModelSerializer):
    """ It's using with detail mailing statistic"""
    status = serializers.ReadOnlyField(
        source='get_status_display',
        read_only=True
    )
    phone_number = serializers.SlugRelatedField(
        source='client',
        slug_field="phone_number",
        read_only=True,
    )

    class Meta:
        model = Message
        fields = ("id", "send_date_time", "status", "phone_number")


class MailingSerializer(serializers.ModelSerializer):
    """ Serializer to post/update Mailing, just represents model """
    filter_operator_codes = serializers.SlugRelatedField(
        slug_field="code",
        allow_null=True,
        required=False,
        queryset=OperatorCode.objects,
        many=True
    )
    filter_client_tags = serializers.SlugRelatedField(
        slug_field="tag",
        allow_null=True,
        required=False,
        queryset=ClientTag.objects,
        many=True
    )
    start_time = serializers.TimeField(required=False)
    stop_time = serializers.TimeField(required=False)

    class Meta:
        model = Mailing
        fields = [
            'id',
            'start_date',
            'start_time',
            'stop_date',
            'stop_time',
            'message',
            'filter_operator_codes',
            'filter_client_tags',
        ]


class MailingGeneralStatisticSerializer(MailingSerializer):
    """ Serializer to represent short statistic in list """
    total_message_count = serializers.IntegerField()
    success_message_count = serializers.IntegerField()
    fail_message_count = serializers.IntegerField()
    planned_message_count = serializers.IntegerField()

    class Meta:
        model = MailingSerializer.Meta.model
        fields = MailingSerializer.Meta.fields + [
            'total_message_count',
            'success_message_count',
            'fail_message_count',
            'planned_message_count',
        ]


class MailingDetailStatisticSerializer(MailingGeneralStatisticSerializer):
    """ Serializer to represent full statistic in retrieve get view """
    messages = MessageSerializer(many=True)

    class Meta:
        model = MailingGeneralStatisticSerializer.Meta.model
        fields = MailingGeneralStatisticSerializer.Meta.fields + ['messages']


class ClientSerializer(serializers.ModelSerializer):
    """ Can representation client with related fields tag and operator_code.
        Required field is only phone_number to create or update client,
        if related fields are not passed, they wil be set to null.
        If related fields does not exist, they will be created"""
    operator_code = serializers.SlugRelatedField(
        slug_field="code",
        allow_null=True,
        queryset=OperatorCode.objects,
        required=False
    )
    tag = serializers.SlugRelatedField(
        slug_field="tag",
        allow_null=True,
        queryset=ClientTag.objects,
        required=False
    )

    class Meta:
        model = Client
        fields = '__all__'

    def is_valid(self, raise_exception=True):
        if number := self.initial_data.get("phone_number"):
            check_valid_number(str(number))
        create_related_if_not_exist(self.initial_data)
        return super().is_valid(raise_exception=True)
