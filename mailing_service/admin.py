from django.contrib import admin
from .models import Mailing, Client, Message, ClientTag, OperatorCode


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    filter_horizontal = ['filter_operator_codes', 'filter_client_tags']


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    pass


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    pass


@admin.register(OperatorCode)
class MessageAdmin(admin.ModelAdmin):
    pass


@admin.register(ClientTag)
class MessageAdmin(admin.ModelAdmin):
    pass