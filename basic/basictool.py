import os
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
