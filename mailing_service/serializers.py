from rest_framework import serializers

from .models import Mailing, Client, Message, ClientTag, OperatorCode
from .servises import check_valid_number


class MailingSerializer(serializers.ModelSerializer):
    filter_operator_codes = serializers.SlugRelatedField(slug_field="code", queryset=OperatorCode.objects.all(),
                                                         many=True)
    filter_client_tags = serializers.SlugRelatedField(slug_field="tag", queryset=ClientTag.objects.all(), many=True)

    class Meta:
        model = Mailing
        fields = '__all__'


class ClientSerializer(serializers.ModelSerializer):
    tag = serializers.SlugRelatedField(slug_field="tag", queryset=ClientTag.objects.all(), default=None)
    operator_code = serializers.SlugRelatedField(slug_field="code", queryset=OperatorCode.objects.all(), default=None)

    class Meta:
        model = Client
        fields = '__all__'

    def is_valid(self, raise_exception=True):
        if number := self.initial_data.get("phone_number"):
            check_valid_number(str(number))
        return super().is_valid(raise_exception=True)


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'
