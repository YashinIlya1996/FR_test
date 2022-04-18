import random

from django.core.management.base import BaseCommand
from mailing_service.models import Client, ClientTag, OperatorCode


class Command(BaseCommand):
    help = "Create testing data in DB"
    tagnames = {
        "usual": 40,
        "good": 10,
        "bad": 10,
        "great": 5,
        "vip": 1,
        "poor": 10,
        "reach": 3,
        "best": 2,
        "worst": 2,
    }

    def handle(self, *args, **options):
        self.create_operator_codes()
        self.create_client_tags()
        self.create_clients()

    def create_operator_codes(self):
        OperatorCode.objects.all().delete()
        codes = []
        for code in range(900, 1000):
            codes.append(OperatorCode(code=code))
        OperatorCode.objects.bulk_create(codes)
        self.stdout.write("OperatorCode created")

    def create_client_tags(self):
        ClientTag.objects.all().delete()
        tags = []
        for tag in Command.tagnames.keys():
            tags.append(ClientTag(tag=tag))
        ClientTag.objects.bulk_create(tags)
        self.stdout.write("ClientTag created")

    def create_clients(self, count=500):
        Client.objects.all().delete()
        clients = []
        numbers = set()
        codes = list(OperatorCode.objects.values_list('code', flat=True))

        def create_phone_number():
            return 7 * 10 ** 11 + random.randint(0, 10 ** 11 - 1)

        while len(numbers) < count:
            numbers.add(create_phone_number())

        for number in numbers:
            clients.append(Client(
                phone_number=number,
                operator_code=OperatorCode.objects.get(code=random.choice(codes)),
                tag=ClientTag.objects.get(tag=random.choices(tuple(Command.tagnames.keys()),
                                                             tuple(Command.tagnames.values()))[0]),
            ))

        Client.objects.bulk_create(clients)
        self.stdout.write("Clients created")

