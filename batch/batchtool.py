import os
import multiprocessing
from tqdm import tqdm
import jieba
import jieba.posseg
import nltk

from arsenal.annotation import annotool

def _tokenize(text, language_code):
    """Tokenize a text. You can add more language supports.
    """
    seq = annotool.raw2basicseq(text, language_code, pos=False)
    word_seq = seq['word']
    return word_seq

def _tokenize4map(param):
    """[Do NOT modify this method.] A method to pass multiple parameters
    for `multiprocessing.Pool.map()` method.
    """
    return _tokenize(*param)

def tokenize(doc_list, language_code, core_num=multiprocessing.cpu_count()):
    """Tokenize each doc in the `doc_list` with parallel acceleration.

    Args:
        doc_list: <list of str>
        language_code: <str> Supported options: 'en', 'zh'.
        core_num: <int> Default the total number of CPU.

    Returns:
        A list of lists of tokenized words.
    """
    param = [[d, language_code] for d in doc_list]
    pool = multiprocessing.Pool(core_num)
    return pool.map(_tokenize4map, param)

def _tokenize_replace_pos(text, language_code, replace_pos):
    """[Do NOT modify this method.] If you want add supports to more languages,
    please refer to `arsenal.annotation.annotool.raw2basicseq()`.
    """
    seq = annotool.raw2basicseq(text, language_code, pos=True)
    word_seq = seq['word']
    pos_seq = seq['pos']
    for i, pos in enumerate(pos_seq):
        if pos in replace_pos:
            word_seq[i] = '[{}]'.format(pos)
    return word_seq

def _tokenize_replace_pos4map(param):
    """DO NOT MODIFY THIS METHOD. A method to pass multiple parameters
    for `multiprocessing.Pool.map()` method.
    """
    return _tokenize_replace_pos(*param)

def tokenize_replace_pos(doc_list, language_code, replace_pos,
                         core_num=multiprocessing.cpu_count()):
    """Tokenize each doc in the `doc_list` and replace the word with `[POS]`
    if its POS belongs to the `replace_pos`.

    Args:
        doc_list: <list of str>
        language_code: <str> Supported Options: 'en', 'zh'.
        replace_pos: <list of str> A list of POS's which you want to replace.
                     Example (for English): ['NN', 'NNP', 'CD']
                     You can use
                     `arsenal.basic.basictool.load_default_replace_pos(language_code)`
                     to load default list.

    Returns:
        A list of lists of tokenized words with specific POS replaced.
    """
    param = [[d, language_code, replace_pos] for d in doc_list]
    pool = multiprocessing.Pool(core_num)
    return pool.map(_tokenize_replace_pos4map, param)
