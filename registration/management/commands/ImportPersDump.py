import json

from django.core.management import BaseCommand

from registration.logic import create_subscriber
from registration.models import Subscriber


class Command(BaseCommand):
    def add_arguments(self, parser):
        # parser.add_argument("file_path1", type=str,)
        parser.add_argument("file_path2", type=str,)

    def handle(self, *args, **options):

        # file_path1 = options["file_path1"]
        file_path2 = options["file_path2"]

        # with open(file_path1, "r") as file:
        #     # read json from file
        #     json_str1 = file.read()
        #
        #     # parse json string
        #     data1 = json.loads(json_str1)

        # print(data1)

        with open(file_path2, "r") as file:
            # read json from file
            json_str2 = file.read()

            # parse json string
            data2 = json.loads(json_str2)

        # print(data2)

        counter = 0

        not_valid = {}

        for k, v in data2.items():

            print(f"key: {k}")
            print(f"value: {v}")

            matricola = v[0]
            email = v[1]
            surname = v[3]
            name = v[4]

            print()
            print(f"matricola: {matricola}")
            print(f"email: {email}")
            print(f"surname: {surname}")
            print(f"name: {name}")
            print()

            if not email:
                print(f"Skipping subscriber with  key={k} matricola: {matricola} and email: {email}.")

                not_valid[k] = v
                continue

            # check if an instance of Subscriber with the same matricola and email already exists

            if Subscriber.objects.filter(matricola=matricola, email=email).exists():
                print(f"Subscriber with matricola: {matricola} and email: {email} already exists.")
                continue

            # if not, create a new instance of Subscriber
            create_subscriber(email, name, surname, matricola)

            print(f"Subscriber with matricola: {matricola} and email: {email} created.")

            counter += 1


        print(f"Total subscribers created: {counter}")

        print()

        print(not_valid)



