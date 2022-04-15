from rest_framework import serializers

from .models import Mailing, Client, Message, ClientTag, OperatorCode
from .servises import check_valid_number, create_related_if_not_exist


class MailingSerializer(serializers.ModelSerializer):
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
        fields = '__all__'


class ClientSerializer(serializers.ModelSerializer):
    """ Can representation client with related fields tag and operator_code.
        Required field is only phone_number to create or update client,
        if related fields are not passed, they wil be set to null"""
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
        return super().is_valid(raise_exception=False)


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'
