import os
import re
import multiprocessing
from tqdm import tqdm
import jieba
import jieba.posseg as pseg

def read_linedoc(linedoc_file, delimiter='\n'):
    """Read the linedoc txt file and check if the line is blank.

    Args:
        linedoc: <str> Path of the linedoc txt file.
        delimiter: <str> The delimiter between the lines, default '\n'
                   (means no delimiters between lines.).
                   e.g. '\n----------\n'

    Returns:
        A list of documents.
    """
    with open(linedoc_file, 'r') as f:
        doc_list = f.read().split(delimiter)
    # Remove the spaces at the start and end of documents.
    doc_list = [d.strip() for d in doc_list]
    # Define the filter function.
    def is_not_blank (my_string):
        # my_string is NOT None AND my_string is NOT empty or blank.
        return bool(my_string and my_string.strip())
    # Filter the blank elements.
    return list(filter(is_not_blank, doc_list))

def read_multi_linedoc(linedoc_dir):
    """Read multiple linedoc txt files under a dir and gather them together.

    Args:
        linedoc_dir: <str> The path of the dir which contains multiple linedocs.
                     The function will search all linedoc files under this path.
    Returns:
        A list of documents which are gathered from multiple linedoc txt files.
    """
    doc_list = []
    # `os.walk` will walk the dir and return dirpaths, dirnames, filenames.
    for dirpath, dirname, filename in os.walk(linedoc_dir):
        if filename != []:
            print('Gathering the documents under {} =>'.format(dirpath))
            for f in tqdm(filename):
                filepath = os.path.join(dirpath, f)
                doc_list += read_linedoc(filepath)
    return doc_list


def remove_symbol(doc_list, basic_sym='default', user_sym=r"\s"):
    """[Unverified] Remove the certain symbols in the documents.
    Basically this function has a self-maintained symbol list.

    en_sym = r"-~!@#$%^&*()_+`=\[\]\\\{\}\"|;':/<>?·！@#￥%……&*"
    zh_sym = r"（）——+【】、；‘：“”、《》？「『」』"
    basic_sym = en_sym + zh_sym + ...

    Usually, we don't recommend user to modify this self-maintained list.
    If you want to use another brand new symbol list, use `basic_sym` param.
    If you want to use additional symbol besides the self-maintained one,
    use `user_sym` param.

    Notice that we don't have comma or period inside the self-maintained list.

    Args:
        doc_list: <list of str>
        basic_sym: <raw str> e.g. r"\[\]". Default 'default', means loading the
            self-maintained symbol list.
        user_sym: <raw str> 

    Returns:
        A list of documents that exclude certain symbols.
    """
    if basic_sym == 'default':
        en_sym = r"-~!@#$%^&*()_+`=\[\]\\\{\}\"|;':/<>?·！@#￥%……&*"
        zh_sym = r"（）——+【】、；‘’：“”、《》？「『」』［］"
        basic_sym = en_sym + zh_sym
    sym = r"[{}]".format(basic_sym + user_sym)
    print('Removing symbols =>')
    for i, doc in tqdm(enumerate(doc_list)):
        doc_list[i] = re.sub(sym, '', doc)
    return doc_list


def possegment(doc_list, pos_list=['nr', 'r', 'ns', 'm', 'eng', 'x'],
               core_num=min(multiprocessing.cpu_count(),4)):
    """Segment each document in the list with part-of-speech filtering.

    Args:
        doc_list: <list of str>
        core_num: <int> The number of CPU cores to work.

    Returns:
        A list of documents which have been segmented and pos filtered.
    """
    doc_num = len(doc_list)
    # Combine the docs in order to speed up.
    text = '\n'.join(doc_list)
    text_seg = []

    doc_id = 0  # Initialize the count.
    jieba.enable_parallel(core_num)
    pairs = pseg.cut(text)
    for word, flag in pairs:
        # The condition of pos filtering.
        # We treat human names, place names, numbers ... as the same ones.
        # Notice '\n' should be kept since it's the delimiter between lines.
        if flag in pos_list and word != '\n':
            # Substitute these words with their pos tags.
            text_seg.append('[{}]'.format(flag))
            # Aggregate the same flags.
            try:
                if text_seg[-1] == text_seg[-2]:
                    text_seg.pop()
            except IndexError:
                pass
        elif word == '\n':
            text_seg.append(word)
            doc_id += 1
            if doc_id % 10000 == 0:
                print('Processing {}/{}'.format(doc_id, doc_num))
        else:
            text_seg.append(word)
    return ' '.join(text_seg).split(' \n ')

def raw2pseg(linedoc_raw_file, core_num):
    basedir = os.path.dirname(linedoc_raw_file)
    doc_list = read_linedoc(linedoc_raw_file)
    doc_list = remove_symbol(doc_list)
    doc_list = possegment(doc_list, core_num=4)
    with open(basedir + '/pseg.txt', 'w') as f:
        f.write('\n'.join(doc_list))
