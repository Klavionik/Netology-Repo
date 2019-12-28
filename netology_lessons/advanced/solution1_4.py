"""
LESSON 1.4, EX. 1, 2, 3
"""

from datetime import datetime
import hashlib


def logger(original_function):
    def wrapper(*args, **kwargs):
        start = datetime.now()
        name = original_function.__name__
        result = original_function(*args, **kwargs)
        with open(f'{name}.log', 'a') as f:
            log = f"Function has started at: {start}\nName {name}\nArguments: positional {args}; keyword {kwargs}\n" \
                  f"Result {result}\n\n"
            f.write(log)
        return result
    return wrapper


def custom_path_logger(path):
    def decorated(original_function):
        def wrapper(*args, **kwargs):
            start = datetime.now()
            name = original_function.__name__
            result = original_function(*args, **kwargs)
            with open(f'{path}\\{name}.log', 'a') as f:
                log = f"Function has started at: {start}\nName {name}\nArguments: positional {args}; "\
                      f"keyword {kwargs}\nResult {result}\n\n"
                f.write(log)
            return result
        return wrapper
    return decorated


@logger
def md5_hash_gen(filename):
    hash_point = hashlib.md5()
    with open(filename, 'rb') as fhandle:
        file = fhandle.read()
    for line in file:
        hash_point.update(bytes(line))
        yield hash_point.hexdigest()


# @custom_path_logger("C:\\Users\\Jediroman")
# def md5_hash_gen(filename):
#     hash_point = hashlib.md5()
#     with open(filename, 'rb') as fhandle:
#         file = fhandle.read()
#     for line in file:
#         hash_point.update(bytes(line))
#         yield hash_point.hexdigest()
