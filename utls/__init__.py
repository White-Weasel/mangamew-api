from dataclasses import fields


def get_all_dataclass_data(data):
    result = []
    for att in fields(data):
        result.append(getattr(data, att.name))
    return result


def get_all_dataclass_fields(data):
    result = []
    for att in fields(data):
        result.append(att.name)
    return result
