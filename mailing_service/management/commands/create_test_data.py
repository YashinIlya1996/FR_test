import random
import datetime as dt
from string import ascii_lowercase

from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string
from mailing_service.models import Mailing, Client, Message, ClientTag, OperatorCode


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
        self.create_mailings()

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

    def create_mailings(self, count=50):
        Mailing.objects.all().delete()
        Message.objects.all().delete()
        MIN_START_DATE = dt.datetime.now() + dt.timedelta(days=1)
        MAX_START_DATE = MIN_START_DATE + dt.timedelta(days=90)
        ALLOWED_CHARS_IN_MESSAGE = ascii_lowercase + " " * 10

        def create_random_date_time(start: dt.datetime, stop: dt.datetime) -> dt.datetime:
            return start + (stop - start) * random.random()

        def get_random_objects_from_db(model, count=1):
            return model.objects.order_by('?')[:count]

        mailings = []
        for _ in range(count):
            tags_count = random.choice([0, random.randint(1, 5)])
            codes_count = random.choice([0, random.randint(1, 10)])
            start = create_random_date_time(MIN_START_DATE, MAX_START_DATE)
            stop = create_random_date_time(start, MAX_START_DATE)
            new_mailing = Mailing.objects.create(
                start_date=start.date(),
                start_time=start.time(),
                stop_date=stop.date(),
                stop_time=stop.time(),
                message=get_random_string(
                    random.randint(15, 100), allowed_chars=ALLOWED_CHARS_IN_MESSAGE
                ).lstrip().capitalize()
            )
            if codes_count:
                new_mailing.filter_operator_codes.add(*get_random_objects_from_db(OperatorCode, codes_count))
            if tags_count:
                new_mailing.filter_client_tags.add(*get_random_objects_from_db(ClientTag, tags_count))

        self.stdout.write("Mailings created")

    @staticmethod
    def get_external_api_response():
        return random.choices((200, 400), (97, 3))
