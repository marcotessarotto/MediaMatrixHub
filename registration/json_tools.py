import json


def parse_json_file_to_dict_by_matricola(file_name):
    """
    Parses a JSON file and returns a dictionary of its content, indexed by the 'matricola'.

    Args:
    file_name (str): The path to the JSON file to be parsed.

    Returns:
    dict: The parsed JSON data as a dictionary with 'matricola' as keys.
    """
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            data = json.load(file)
            # Create a new dictionary with 'matricola' as the key
            new_data = {details[0]: details for name, details in data.items()}
        return new_data
    except FileNotFoundError:
        print(f"The file {file_name} was not found.")
        return {}
    except json.JSONDecodeError:
        print("Failed to decode JSON, please check the file format.")
        return {}
    except Exception as e:
        print(f"An error occurred: {e}")
        return {}

# Example usage:
# result = parse_json_file_to_dict_by_matricola('path_to_your_file.json')
# print(result)


__preloaded_dict = {}

def lookup_subscriber_json_data_by_matricola(matricola):
    """
    Lookup a person by their 'matricola'.

    Args:
    matricola (str): The 'matricola' of the person to lookup.

    Returns:
    list: The details of the person with the given 'matricola'.
    """
    global __preloaded_dict
    if not __preloaded_dict:
        __preloaded_dict = parse_json_file_to_dict_by_matricola('registration/res/persfvg_dump_persone_entita.json')
    return __preloaded_dict.get(matricola, None)

__preloaded_dict2 = {}

def get_dump_final_json():
    global __preloaded_dict2
    if not __preloaded_dict2:
        file_name = 'registration/res/persfvg_dump_final.json'

        try:
            with open(file_name, 'r', encoding='utf-8') as file:
                data = json.load(file)
            return data
        except FileNotFoundError:
            print(f"The file {file_name} was not found.")
            return {}
        except json.JSONDecodeError:
            print("Failed to decode JSON, please check the file format.")
            return {}
        except Exception as e:
            print(f"An error occurred: {e}")
            return {}

    return __preloaded_dict2

__preloaded_dict3 = {}

def get_dump_persone_entita_json():
    global __preloaded_dict3
    if not __preloaded_dict3:
        file_name = 'registration/res/persfvg_dump_persone_entita.json'

        try:
            with open(file_name, 'r', encoding='utf-8') as file:
                data = json.load(file)
            return data
        except FileNotFoundError:
            print(f"The file {file_name} was not found.")
            return {}
        except json.JSONDecodeError:
            print("Failed to decode JSON, please check the file format.")
            return {}
        except Exception as e:
            print(f"An error occurred: {e}")
            return {}

    return __preloaded_dict3


__parent_structure = {}
__children_structures = {}
__structure_name = {}
__preloaded_data = False

def get_uaf_children_recursively(uaf):

    global __parent_structure, __children_structures, __structure_name, __preloaded_data

    if not __preloaded_data:
        __parent_structure = {}

        __children_structures = {}

        __structure_name = {}

        data2 = get_dump_final_json()

        for k, v in data2.items():

            # print(f"key: {k}")
            # print(f"value: {v[3]}")

            parent_uaf = v[3]

            # key is the uaf
            # parent uaf is v[3]

            __parent_structure[k] = parent_uaf
            __structure_name[k] = v[0]

            if parent_uaf not in __children_structures:
                __children_structures[parent_uaf] = [k]
            else:
                if k != parent_uaf:
                    if k not in __children_structures[parent_uaf]:
                        __children_structures[parent_uaf].append(k)

    # print()
    # # print(children_structures)
    # for k, v in __children_structures.items():
    #     print(f"{k}: {v}")
    # print()
    # print()
    #
    # for k, v in __parent_structure.items():
    #     print(f"{k}: {v}")
    # # print number of keys in
    #
    # print()
    # for k, v in __structure_name.items():
    #     print(f"{k}: {v}")

    # given a uaf, return recursive list of children uafs and itself
    def get_recursive_children(uaf):

        result = []
        result2 = []

        if uaf in __children_structures:
            result = __children_structures[uaf]

            for uaf2 in result:
                result2.extend(get_recursive_children(uaf2))

        # join result and result2
        result.extend(result2)
        # add uaf itself to the result
        result.append(uaf)

        # return a list of unique uafs
        result = list(set(result))

        return result

    r = get_recursive_children(uaf)

    # print(f"uaf {uaf} and its children: {r}")
    # print(f"length: {len(r)}")

    return r



def get_all_employees_uaf(uaf):
    list_of_uafs = get_uaf_children_recursively(uaf)

    print(f"length of list_of_uafs: {len(list_of_uafs)}")

    dump_persone_entita = get_dump_persone_entita_json()

    print(f"length of dump_persone_entita: {len(dump_persone_entita)}")

    employees = []

    for k,v in dump_persone_entita.items():
        # print(k)
        # print(v)
        try:
            employee_uaf = v[6]

            if not employee_uaf:
                print(f"skipped(2): {k}")
                continue

            if employee_uaf in list_of_uafs:
                employees.append(v)
        except IndexError:
            print(f"skipped: {k}")
            pass

    return employees