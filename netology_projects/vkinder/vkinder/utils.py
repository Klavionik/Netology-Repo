import re
import os
import sys

import progressbar

from .globals import photo_sizes, END, V, R


def cleanup(text):
    """
    Takes a given text and processes it to prepare for match scoring.

    1) Removes meaningless characters from the text
    2) Replaces all occurences of a newline with a comma
    3) Splits the text using comma as a delimiter
    4) Converts every string of the splitted text for lowercase
    and removes whitespace characters on both ends of a string

    :param text: Text string
    :return: List of strings
    """
    special_characters = re.compile(r'[\"^;!/|()«»]', re.IGNORECASE)
    newline = re.compile(r'\n')
    no_spec_char = special_characters.sub('', text)
    no_newlines = newline.sub(',', no_spec_char)
    final = [key.lower().strip() for key in no_newlines.split(',')]

    return final


def common(iterable1, iterable2):
    """
    Takes two iterable objects and returns the number of their common objects.

    :param iterable1: An iterable object
    :param iterable2: An iterable object
    :return: int
    """
    return len(set(iterable1) & set(iterable2))


def find_largest_photo(links):
    """
    Given the 'sizes' array of a VK API `Photo` object, returns a
    link to the largest photo in the array.

    :param links: `Sizes` array (a list of dicts)
    :return: Largest photo url (a string)
    """

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


def next_ids(ids, amount=12):
    """
    Splits a list of matches ids in chunks.

    :param ids: List of matches ids
    :param amount: Amount of ids yielded per iteration
    """
    for index in range(0, len(ids), amount):
        yield ids[index:index + amount]


def verify_bday(value):
    """
    Validates if a given date string conforms to the format used for get_usr_age function.

    :param value: Birth date of the current user
    :return: :class:re.Match object if the given argument is correct,
    None if not correct or not a string
    """
    pattern = re.compile(r'^\d?\d\.\d\.\d{4}$')

    try:
        verification = re.match(pattern, value)
    except TypeError:
        return None
    else:
        return verification


def progress_bar(text):
    """
    Displays a fancy progress bar.

    :param text: Progress bar text
    :return: :module:`progressbar2` progress bar
    """
    bar = \
        progressbar.ProgressBar(widgets=[f'{V}{text}{END}',
                                         progressbar.Percentage(),
                                         progressbar.Bar
                                         (marker=progressbar.AnimatedMarker(
            fill='#',
            fill_wrap=(
                f'{R}',
                '\033[0m',
            ),
            marker_wrap=(
                f'{R}',
                '\033[0m',
            ),
        ))])
    return bar


def clean_screen():
    if sys.platform == "win32":
        os.system("cls")
    elif sys.platform == "linux":
        os.system("clear")
