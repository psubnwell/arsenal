import os
import random
from itertools import chain
import nltk
from keras.preprocessing.sequence import pad_sequences

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

def generate_index_dict(my_list, start_index=1, unknown={'<UNK>':0}):
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
    if (unknown != False) and (unknown != None):
        index_dict = {**unknown, ** index_dict}
    elif (unknown == False) or (unknown == None):
        pass
    return index_dict

def element2index(my_list, index_dict):
    """Map the corresponding index for a item list.

    Args:
        item_list:
        index_dict: A dict with pairs of items and their indexes.

    Returns:
        A index list.
    """
    index_list = []
    for item in my_list:
        try:
            index_list.append(index_dict[item])
        except KeyError:
            index_list.append(index_dict['<UNK>'])
    return index_list

def padding_sequence_batch_generator(x, y, batch_size, shuffle=False):
    # Shuffle.
    if shuffle == True:
        z = list(zip(x,y))
        random.shuffle(z)
        x, y = zip(*z)
    # Add data to make the number of sequences integral multiple of batch size.
    makeup_num = batch_size - len(x) % batch_size

    x += [[0]] * makeup_num
    y += [[0]] * makeup_num
    # Generate the padding batch.
    for i in range(seq_num // batch_size + 1):
        x_batch = x[i * batch_size:(i + 1) * batch_size]
        y_batch = y[i * batch_size:(i + 1) * batch_size]
        len_batch = [len(s) for s in x_batch]  # Why should use np.array?

        x_batch = pad_sequences(x_batch, padding='post')
        y_batch = pad_sequences(y_batch, padding='post')

        yield x_batch, y_batch, len_batch


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
