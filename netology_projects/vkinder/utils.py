import re
from datetime import datetime


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


def next_ids(ids, amount=25):
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
