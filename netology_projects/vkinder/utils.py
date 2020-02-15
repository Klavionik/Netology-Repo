import re
from datetime import datetime
from netology_projects.vkinder.globals import photo_sizes


def cleanup(text):
    special_characters = re.compile(r'[\"^;!/|()«»]', re.IGNORECASE)
    newline = re.compile(r'\n')
    no_spec_char = special_characters.sub('', text)
    no_newlines = newline.sub(',', no_spec_char)
    final = [key.lower().strip() for key in no_newlines.split(',')]

    return final


def common(iterable1, iterable2):
    return len(set(iterable1) & set(iterable2))


def find_largest_photo(links):
    def size_type_to_int(size):
        return photo_sizes[size]

    return sorted(links, key=lambda x: size_type_to_int(x['type']), reverse=True)[0]['url']


def flatten(d):
    """
    Flattens a dictionary containing other dictionaries.

    :param d: Dictionary of dictionaries
    :return: Flat dictionary
    """
    flat = {}
    for key, value in d.items():
        if isinstance(value, dict):
            for subkey, subvalue in d[key].items():
                flat[key + '.' + subkey] = subvalue
        else:
            flat[key] = value

    return flat


def verify_bday(value):
    """
    Validates if a given date string conforms to the format used for get_usr_age function.

    :param value: Birth date of the current user
    :return: :class:re.Match object if the given argument is correct,
    None if not correct or not a string
    """
    pattern = re.compile(r'^\d\.\d\.\d{4}$')

    try:
        verification = re.match(pattern, value)
    except TypeError:
        return None
    else:
        return verification


def next_ids(ids, amount=12):
    """
    Splits a list of matches ids in chunks of 25.

    :param ids: List of matches ids
    :param amount: Amount of ids yielded per iteration
    """
    for index in range(0, len(ids), amount):
        yield ids[index:index + amount]


def get_usr_age(bday):
    """
    Takes a user's birth date and returns their age.

    :param bday: birth date formatted as d.m.yyyy
    :return: exact user age
    """
    if not verify_bday(bday):
        bday = input('\nBirth date is incomplete or incorrect.'
                     '\nPlease, enter your birth date as d.m.yyyy\n').rstrip()
    bday = datetime.strptime(bday, '%d.%m.%Y')
    today = datetime.today()
    return today.year - bday.year - ((today.month, today.day) < (bday.month, bday.day))
