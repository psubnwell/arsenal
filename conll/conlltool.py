import os
import json
import random
import multiprocessing
from itertools import chain

import jieba.posseg
import numpy as np
import pandas as pd

from arsenal.annotation import annotool
from arsenal.conll import conlleval

def seqlist2batch(seq_list):
    key = list(seq_list[0].keys())
    batch = {}
    for k in key:
        batch.update({k:[seq[k] for seq in seq_list]})
    return batch

def batch2seqlist(batch):
    key = list(batch.keys())
    batch_len = len(batch[key[0]])
    seq_list = []
    for i in range(batch_len):
        seq = {}
        for k in key:
            seq.update({k:batch[k][i]})
        seq_list.append(seq)
    return seq_list

def _conll2batch4map(param):
    return annotool.conll2seq(*param)

def conll2batch(conll_text, column_name, column_sep='\t',
                core_num=multiprocessing.cpu_count()):
    param = [[c, column_name, column_sep] for c in conll_text.strip().split('\n\n')]
    pool = multiprocessing.Pool(core_num)
    seq_list = pool.map(_conll2batch4map, param)
    return seqlist2batch(seq_list)

def _batch2conll4map(param):
    return annotool.seq2conll(*param)

def batch2conll(batch, column_name, column_sep='\t',
                core_num=multiprocessing.cpu_count()):
    seq_list = batch2seqlist(batch)
    param = [[seq, column_name, column_sep] for seq in seq_list]
    pool = multiprocessing.Pool(core_num)
    return '\n\n'.join(pool.map(_batch2conll4map, param))



# --------------------------------------------------------------
# Old methods.

def get_nested_column(conll_file, column_sep, column_index):
    """Extract the certain column from conll format file.

    Args:
        conll_file: The path of standard formatted conll corpus file.
        delimiter: The delimiter between different columns, usually '\t' or ' '.
        column_index: Which column to extract.

    Returns:
        A nested list. Each element in list represents a sequence, which is a list of tokens.
    """
    with open(conll_file, 'r') as f:
        block = f.read().strip().split('\n\n')
    return [[line.split(column_sep)[column_index] for line in b.split('\n')] for b in block]

def conll2nested_seq(conll_text, column_name, column_sep='\t'):
    block = conll_text.split('\n\n')
    nested_seq = {}
    for index, name in enumerate(column_name):
        nested_seq.update(
            {name:[[line.split(column_sep)[index] for line in b.split('\n')] for b in block]}
        )
    return nested_seq

def nested_seq2conll(nested_seq, column_name, column_sep='\t'):
    return conlleval.format_nested(
        nested_seq['token'],
        nested_seq['word'],
        nested_seq['start'],
        nested_seq['end'],
        nested_seq['label'],
        nested_seq['pred'])

def k_longest_sequence_index(nested_list, k):
    """Return the longest lists' indexes and their lengths
    in a nested list.

    Args:
        nested_list: A list of lists.
        k: int.

    Returns:
        dict. Has two keys: 'idx' and 'len'.
    """
    seq_len = np.array([len(i) for i in nested_list])
    max2min_index = seq_len.argsort()[::-1]
    k_longest_index = max2min_index[:k]
    k_longest_len = seq_len[k_longest_index]
    return {'idx':k_longest_index, 'len':k_longest_len}

def remove_k_longest_sequence(nested_list, k):
    nested_list = np.array(nested_list)
    return np.delete(nested_list, k_longest_sequence_index(nested_list, k)['idx'])


def flatten_nested_list(nested_list):
    """Flatten (Unnest) a nested list.

    Args:
        nested_list: e.g. [[1,3],[2,4]]

    Returns:
        A flatten (unnested) list.
    """
    return list(chain.from_iterable(nested_list))

def generate_index_dict(item_list, start_index=1):
    """Generate a dict which encodes each item in the list.

    Args:
        item_list:
        start_index: The first index number to use.

    Returns:
        A dict with pairs of items and their indexes.
    """
    index_dict = {}
    index = start_index  # Default starts from 1.
    for item in item_list:
        if item not in index_dict:
            index_dict[item] = index
            index += 1
    return index_dict

def generate_word_index_dict(conll_file, column_delimiter='\t', column_index=0):
    """[Script] Generate a word-index dict directly from a conll formatted txt file.

    Args:
        conll_file: path of a conll formatted txt file.

    Returns:
        word_index_dict.json under the same dir.
    """
    basedir = os.path.dirname(conll_file)
    word = get_nested_column(conll_file, column_delimiter, column_index)
    word_unnested = flatten_nested_list(word)
    word_index_dict = generate_index_dict(word_unnested)
    print('Total {} words.'.format(len(word_index_dict)))
    with open(basedir + '/word_index_dict.json', 'w') as f:
        f.write(json.dumps(word_index_dict, ensure_ascii=False))

def generate_label_index_dict(conll_file, column_delimiter='\t', column_index=-1):
    """[Script] Generate a label-index dict directly from a conll formatted txt file.

    Args:
        conll_file: path of a conll formatted txt file.

    Returns:
        label_index_dict.json under the same dir.
    """
    basedir = os.path.dirname(conll_file)
    label = get_nested_column(conll_file, column_delimiter, column_index)
    label_unnested = flatten_nested_list(label)
    label_index_dict = generate_index_dict(label_unnested)
    print('Total {} labels.'.format(len(label_index_dict)))
    with open(basedir + '/label_index_dict.json', 'w') as f:
        f.write(json.dumps(label_index_dict, ensure_ascii=False))

def map_index4list(item_list, index_dict):
    """Map the corresponding index for a item list.

    Args:
        item_list:
        index_dict: A dict with pairs of items and their indexes.

    Returns:
        A index list.
    """
    return [index_dict[item] for item in item_list]

def map_index4nested_list(nested_item_list, index_dict):
    """Map the corresponding index for a nested item list.

    Args:
        nested_item_list:
        index_list: A dict with pairs of items and their indexes.

    Returns:
        A nested index list.
    """
    return [map_index4list(item_list, index_dict) for item_list in nested_item_list]

def partition_dataset(conll_file, percentage):
    """[Script] Partition the dataset according to the partition dict.

    Args:
        conll_file: path of the whole dataset.
        partition_dict: list.
            Include three percentage, e.g., [0.8, 0.2, 0.0] 
            which indicates the train, valid, test percentage.
            percentage can be 0, but you should still specify it.

    Returns:
        Partitioned dataset .txt files under the same dir.
    """
    basedir = os.path.dirname(conll_file)

    train_txt = basedir + '/train.txt'
    valid_txt = basedir + '/valid.txt'
    test_txt = basedir + '/test.txt'

    train_per = percentage[0]
    valid_per = percentage[1] + train_per
    test_per = percentage[2] + valid_per

    with open(conll_file, 'r') as f_all, \
         open(train_txt, 'w') as f_train, \
         open(valid_txt, 'w') as f_valid, \
         open(test_txt, 'w') as f_test:
        dataset_all = f_all.read().split('\n\n')
        length = len(dataset_all)
        # Filter empty line.
        condition = lambda t:(t != '') and (t != '\n')
        dataset_all = list(filter(condition, dataset_all))
        # Shuffle the dataset.
        # random.shuffle(dataset_all)
        # Partition the dataset.
        dataset_train = dataset_all[:int(length * train_per)]
        dataset_valid = dataset_all[int(length * train_per):int(length * valid_per)]
        dataset_test = dataset_all[int(length * valid_per):]
        # Print the length of partitioned dataset.
        print('Total {} sequences in train set.'.format(len(dataset_train)))
        print('Total {} sequences in valid set.'.format(len(dataset_valid)))
        print('Total {} sequences in test set.'.format(len(dataset_test)))
        # Write to file.
        f_train.write('\n\n'.join(dataset_train).strip())
        f_valid.write('\n\n'.join(dataset_valid).strip())
        f_test.write('\n\n'.join(dataset_test).strip())
