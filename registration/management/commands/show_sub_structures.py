import json

from django.core.management import BaseCommand

from registration.logic import create_subscriber
from registration.models import Subscriber


class Command(BaseCommand):
    def add_arguments(self, parser):
        # parser.add_argument("file_path1", type=str,)
        parser.add_argument("file_path2", type=str,)
        parser.add_argument("uaf", type=str,)

    def handle(self, *args, **options):
        file_path2 = options["file_path2"]

        uaf = options['uaf']
        print(f"Processing UAF: {uaf}")



        with open(file_path2, "r") as file:
            # read json from file
            json_str2 = file.read()

            # parse json string
            data2 = json.loads(json_str2)

        print(f"Loaded data from file: {data2}")


        counter = 0

        not_valid = {}

        matricola_email = {}

        parent_structure = {}

        children_structures = {}

        structure_name = {}

        for k, v in data2.items():

            print(f"key: {k}")
            print(f"value: {v[3]}")

            parent_uaf = v[3]

            # key is the uaf
            # parent uaf is v[3]

            parent_structure[k] = parent_uaf
            structure_name[k] = v[0]

            if parent_uaf not in children_structures:
                children_structures[parent_uaf] = [k]
            else:
                if k != parent_uaf:
                    if k not in children_structures[parent_uaf]:
                       children_structures[parent_uaf].append(k)


        print()
        # print(children_structures)
        for k, v in children_structures.items():
            print(f"{k}: {v}")
        print()
        print()

        for k,v in parent_structure.items():
            print(f"{k}: {v}")
        # print number of keys in

        print()
        for k,v in structure_name.items():
            print(f"{k}: {v}")


        # given a uaf, return recursive list of children uafs and itself
        def get_recursive_children(uaf):

            def get_uaf_children(uaf):
                try:
                    return children_structures[uaf]
                except KeyError:
                    return []

            result = []
            result2 = []

            if uaf in children_structures:
                result = children_structures[uaf]

                for uaf2 in result:
                    result2.extend(get_uaf_children(uaf2))

            print()
            print(result)
            print(result2)

            # join result and result2
            result.extend(result2)
            # add uaf itself to the result
            result.append(uaf)

            return result


        r = get_recursive_children(uaf)

        print(f"uaf {uaf} and its children: {r}")
        print(f"length: {len(r)}")

        # return result
