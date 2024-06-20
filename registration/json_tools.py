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


