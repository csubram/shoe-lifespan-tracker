import json


def read_from_json_file_named(filename):
    with open(filename, 'r') as in_file:
        dictionary_representation = json.load(in_file)

    return dictionary_representation


def write_data_to_json_file(data, filename):
    with open(filename, 'w+') as out_file:
        out_file.write(json.dumps(data, indent=2))
