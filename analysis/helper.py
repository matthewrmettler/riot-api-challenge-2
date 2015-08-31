__author__ = 'Matt'

def array_to_str(arr):
    return " ".join(str(x) for x in arr)


def str_to_array(str):
    return map(int, str.split(' '))
