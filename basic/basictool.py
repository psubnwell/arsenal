import os
from itertools import chain
import nltk

CURR_FILE_PATH = os.path.realpath(__file__)
CURR_DIR_PATH = os.path.dirname(CURR_FILE_PATH)


def load_default_stopword(language_code):
    if language_code == 'en':
        stopword = nltk.corpus.stopwords.words('english')
    elif language_code == 'zh':
        with open(CURR_DIR_PATH + '/中文停用词表_1208.txt', 'r') as f:
            stopword = f.read().strip().split('\n')
    else:
       pass  # Other languages.
    return stopword

def load_default_replace_pos(language_code):
    if language_code == 'en':
        replace_pos = ['NNP', 'CD', 'NN']
    elif language_code == 'zh':
        replace_pos = ['nr', 'ns', 'm', 'eng']
    else:
        pass  # Other languages.
    return replace_pos

def load_default_sep_punc(language_code):
    if language_code == 'en':
        sep_punc = [',', '.', ';', '?', '!']
    elif language_code == 'zh':
        sep_punc = ['，', '。', '；', '？', '！']
    else:
        pass  # Other languages.
    return sep_punc

def filter_blank_string(string_list):
    """Filter the blank strings in the list.

    Args:
        string_list: <list of str>

    Returns:
        A list without blank strings.
    """
    def is_not_blank(my_string):
        # Notice any non-empty string can be regarded as True in Python.
        return bool(my_string and my_string.strip())
    return list(filter(is_not_blank, string_list))

def flatten_nested_list(nested_list):
    """Flatten (Unnest) a nested list.

    Args:
        nested_list: e.g. [[1,3],[2,4]]

    Returns:
        A flatten (unnested) list.
    """
    return list(chain.from_iterable(nested_list))

def generate_index_dict(my_list, start_index=1):
    """Generate a dict which encodes each item in the list.

    Args:
        my_list:
        start_index: The first index number to use.

    Returns:
        A dict with pairs of items and their indexes.
    """
    my_list = list(set(my_list))
    index_dict = {}
    for index, item in enumerate(my_list):
        index_dict[item] = index + start_index
    return index_dict

def allocate_list(my_list, index_dict):
    """Map the corresponding index for a item list.

    Args:
        item_list:
        index_dict: A dict with pairs of items and their indexes.

    Returns:
        A index list.
    """
    return [index_dict[item] for item in my_list]

def allocate_nested_list(my_nested_list, index_dict):
    """Map the corresponding index for a nested item list.

    Args:
        my_nested_list:
        index_list: A dict with pairs of items and their indexes.

    Returns:
        A nested index list.
    """
    return [allocate_list(sub_list, index_dict) for sub_list in my_nested_list]


def split_with_indexes(my_string, index):
    """Split the string by the given indexes.

    Args:
        my_string: <str>
        index: <list of int> The list of indexes to split.

    Returns:
        A list of split sub-strings.
    """
    # Ensure `index` is a list of int.
    if type(index) != list:
        index = [index]
    # Add the head index and tail index since the listcomp expression need them.
    index = [0] + index + [len(my_string)]
    return [my_string[index[i-1]:idx] for i, idx in enumerate(index) if i > 0]

def item_select(key, value, key_select):
    """[Unverified]
    """
    d = dict(zip(key, value))
    value_select = []
    for each_k in key_select:
        value_select.append(d[each_k])
    return value_select
