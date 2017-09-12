import os
import io
import re
from collections import namedtuple
import itertools
import operator

import pandas as pd
import jieba
import jieba.posseg
from snownlp import SnowNLP
from arsenal.basic import stringtool
from arsenal.linedoc import linedoctool

def get_annotation_set(annotated_text, regex_pattern, parentheses_index):
    """Extract and analyze the annotations.

    Args:
        annotated_text: <str> A text with inline annotations.
        regex_pattern: <raw str> A raw string of regular expression.
                       The regex should include at least three parentheses`()`
                       to indicate the `record`, `text`, `label` (see below).
        parentheses_index: <tuple of int> A tuple to indicate the index of
                       (`record`, `text`, `label`) in the regex.

                       `record`: A original and complete record of annotation.
                       `text`: The raw text of the inline annotation.
                       `label`: The label of the inline annotation.

    Returns:
        A list of Annotation (namedtuple). (No repeat.)

    Example:
    >>> annotated_text = '今天，[value=川普,tag=人名][value=总统,tag=头衔]正式开启对[value=中国,tag=国家]的国事访问。'
    >>> regex_pattern = r'(\[value=(.+?),tag=(.+?)\])'
    >>> parentheses_index = (0, 1, 2)  # respect to `record`, `text`, `label`.
    >>> get_annotation_set(annotated_text, regex_pattern, parentheses_index)
    [Annotation(record='[value=川普,tag=人名]', text='川普', label='人名'),
     Annotation(record='[value=总统,tag=头衔]', text='总统', label='头衔'),
     Annotation(record='[value=中国,tag=国家]', text='中国', label='国家')]
    """
    res = re.findall(regex_pattern, annotated_text)
    Annotation = namedtuple('Annotation', ['record', 'text', 'label'])
    return list(set([Annotation(r[parentheses_index[0]],
                                r[parentheses_index[1]],
                                r[parentheses_index[2]]) for r in res]))

def get_annotation_keyword(annotation, label):
    """[Unverified] Get the keywords and their IDF values and covering percentages.

    Args:
        annotation: <list of Annotation namedtuples>
        label: <str> The specific label of Annotation namedtuples you want to
               focus and extract its keywords.

    Returns:
        A IDFOutput namedtuple with keys: `keyword`, `idf`, `percent`.
    Each value is a sorted list.
    """
    text = [a.text for a in annotation if a.label == label]
    text_seg = linedoctool.possegment(text)
    text_token = [t.split(' ') for t in text_seg]
    # Calculate the IDF values.
    s = SnowNLP(text_token)
    keyword = list(s.idf.keys())
    idf = list(s.idf.values())
    # Sort the `keyword` and `idf` together. Lower IDF means more important.
    # Notice this is the opposite with the traditional TF-IDF way.
    keyword_sorted, idf_sorted = zip(*sorted(zip(keyword, idf)))
    # $IDF = log_2 (D / D_w)$, where D is the number of total documents,
    # D_w is the number of documents contain the keyword.
    # $percent = D_w / D = 1 / 2 ^ IDF$.
    # The higher the `percent`, the more important the keywords
    percent_sorted = [1 / 2**i for i in idf_sorted]
    IDFOutput = namedtuple('IDFOutput', ['keyword', 'idf', 'percent'])
    return IDFOutput(keyword_sorted, idf_sorted, percent_sorted)

def locate_annotation(raw_text, annotation):
    """Add the `start` and `end` locations to the annotations.
    Notice that the match process is GREEDY!

    Args:
        raw_text: <str>
        annotation: <list of namedtuples> The namedtuples should have `record`,
    `text` and `label` values.

    Returns:
        A list of StandoffAnnotation namedtuples (with `start` and `end`
    locations).
    """
    # Make sure `annotation` is a list of Annotation.
    if type(annotation) != list:
        annotation = [annotation]
    regex_pattern = r'({})'.format('|'.join([a.text for a in annotation]))
    res = re.finditer(regex_pattern, raw_text)
    StandoffAnnotation = namedtuple('StandoffAnnotation',
                                    ['record', 'text', 'label', 'start', 'end'])
    # For each match result, compare and return the match annotation.
    return [StandoffAnnotation(
        record=[a.record for a in annotation if a.text == r.group(0)][0],
        text=[a.text for a in annotation if a.text == r.group(0)][0],
        label=[a.label for a in annotation if a.text == r.group(0)][0],
        start=r.start(),
        end=r.end()
        ) for r in res]

# ---------------------------------------------------------------

def get_standoff_annotation(annotated_text, regex_pattern, parentheses_index):
    """Extract the annotations with their `start` and `end` locations in the
    raw text.

    Args:
        annotated_text: <str>
        regex_pattern: <raw str> 
    """
    res = re.finditer(regex_pattern, annotated_text)
    # Since `re.finditer()`'s parentheses indexes are diff from `re.findall()`,
    # for the compatibility we manually add one on each of them.
    parentheses_index = [i + 1 for i in parentheses_index]

    StandoffAnnotation = namedtuple('StandoffAnnotation',
                                    ['record', 'text', 'label', 'start', 'end'])
    # Extract all annotations, but the `start` and `end` are the locations
    # of the `annotated_text`, not of the `raw_text`. So they're `temp`.
    # Notice: the `r.group()` is the same as `r[]`, but Python 3.5 needs former.
    standoff_annotation_temp = [StandoffAnnotation(r.group(parentheses_index[0]),
                                                   r.group(parentheses_index[1]),
                                                   r.group(parentheses_index[2]),
                                                   r.start(), r.end())
                                for r in res]
    # Get the true locations of `start` and `end` in the `raw_text`.
    # The code may look messy, just ignore it.
    standoff_annotation = []
    for i, a in enumerate(standoff_annotation_temp):
        if i == 0:
            # The first annotation's `start` should keep.
            standoff_annotation.append(
                StandoffAnnotation(a.record, a.text, a.label,
                                   a.start, a.start + len(a.text))
            )
        elif i > 0:
            # Each annotation's `start` requires the result of the one before.
            start = standoff_annotation[-1].end + \
                    (a.start - standoff_annotation_temp[i-1].end)
            end = start + len(a.text)
            standoff_annotation.append(
                StandoffAnnotation(a.record, a.text, a.label,
                                   start, end)
            )
    return standoff_annotation

def get_raw_text(annotated_text, annotation):
    """Convert the annotated text to the raw text according to the given
    annotations.

    Args:
        annotated_text: <str>
        annotation: <list of namedtuple> A list of namedtuples that contain
                    at least `record` and `text` keys.

    Returns:
        The raw text without annotations.
    """
    raw_text = annotated_text
    for a in annotation:
        raw_text = raw_text.replace(a.record, a.text)
    return raw_text

def get_annotated_text(raw_text, annotation):
    """[Unverified] Convert the raw text to the annotated text according to the given
    annotations. 其实应该叫做standoff2inline().

    Args:
        raw_text: <str>
        annotation: <list of namedtuple> A list of namedtuples that contain
                    at least `record` and `text` values.
                    1) If only `record` and `text` values are given, then the
                       match process will be "GREEDY", which means all strings
                       same as the given `text` will be annotated.
                    2) If `record`, `text`, `start`, `end` values are given,
                       then only the string with exact start and end locations
                       will be annotated. (privileged)

    Returns:
        The annotated text.
    """
    try:  # Annotation namedtuples have `start` and `end` values.
        # Get the indexes to split the raw text.
        start_index = [a.start for a in annotation]
        end_index = [a.end for a in annotation]
        split_index = list(set(start_index + end_index))
        split_index.sort()
        # Split the raw text into many parts according to the indexes.
        substr = stringtool.split_with_indexes(raw_text, split_index)
        for a in annotation:
            substr[split_index.index(a.start) + 1] = a.record
        annotated_text = ''.join(substr)
    except AttributeError:  # Annotation namedtuples have no `start` or `end`.
        annotated_text = raw_text
        for a in annotation:
            annotated_text = annotated_text.replace(a.text, a.record)
    return annotated_text

def standoff2inline(raw_text, standoff_annotation, greedy=False):
    """[Unverified] Convert the raw text to the annotated text according to the given
    standoff annotations.

    Args:
        raw_text: <str>
        standoff_annotation: <list of StandoffAnnotation namedtuples>
                             contains `record`, `text`, `start` and `end`.
                             If `greedy`=True, then `start` and `end` can
                             be omitted.
        greedy: <boolean> If False (default), then only the string with exact
                `start` and `end` locations will be annotated.
                If True, then the match process will be "GREEDY", which means
                all strings same as the given `text` will be annotated.

    Returns:
        The annotated text.
    """
    if greedy == False:
        # Only the string with exact `start` and `end` locations will be
        # annotated.
        # Get the indexes to split the raw text.
        start_index = [a.start for a in standoff_annotation]
        end_index = [a.end for a in standoff_annotation]
        split_index = list(set(start_index + end_index))
        split_index.sort()
        # Split the raw text into many parts according to the indexes.
        substr = stringtool.split_with_indexes(raw_text, split_index)
        for a in standoff_annotation:
            substr[split_index.index(a.start) + 1] = a.record
        inline_annotated_text = ''.join(substr)
    elif greedy == True:
        # All strings same as the given `text` will be annotated.
        inline_annotated_text = raw_text
        for a in standoff_annotation:
            inline_annotated_text = inline_annotated_text.replace(a.text, a.record)
    return inline_annotated_text


def inline2standoff(inline_annotated_text, regex_pattern, parentheses_index):
    """A high-level encapsulated function to convert inline annotated input to
    standoff annotated output.

    Args:
        inline_annotated_text: <str>
        regex_pattern: ...

    Returns:
        A StandoffOutput namedtuple contains the `raw_text` <str> and
    `standoff_annotation` <list of StandoffAnnotation namedtuples>.
    """
    standoff_annotation = get_standoff_annotation(inline_annotated_text,
                                                  regex_pattern,
                                                  parentheses_index)
    raw_text = get_raw_text(inline_annotated_text, standoff_annotation)
    StandoffOutput = namedtuple('StandoffOutput', ['raw_text', 'standoff_annotation'])
    return StandoffOutput(raw_text, standoff_annotation)


# ------------------------------------------------------

def standoff2taggedseq(raw_text, standoff_annotation, tag_format):
    """Convert the standoff annotated input to a sequence of tags.

    Args:
        raw_text: <str>
        standoff_annotation: <list of namedtuples>
        tag_format: <str>: Options: 'IO' or 'BIO'.

    Returns:
        A dict contains `word`, `flag` and `tag` keys whose values are lists
    (sequences of words, flags and tags).
    """
    pair = list(jieba.posseg.cut(raw_text))
    word = [p.word for p in pair]
    flag = [p.flag for p in pair]
    word_len = [len(w) for w in word]
    start = [sum(word_len[:i]) for i in range(len(word))]
    end = map(lambda x, y: x + y, start, word_len)
    # Generate tag sequence.
    tag = ['O'] * len(word)
    for a in standoff_annotation:
        for i in range(len(word)):
            if a.start >= start[i] and a.start < start[i+1]:
                if tag_format == 'IO':
                    tag[i] = 'I-' + a.label
                elif tag_format == 'BIO':
                    tag[i] = 'B-' + a.label
            elif start[i] > a.start and start[i] < a.end:
                tag[i] = 'I-' + a.label
            else:
                pass
    return {'word':word, 'flag':flag, 'tag':tag}

def reduce_taggedseq(word, flag, tag):
    reduced_word = []
    reduced_flag = []
    reduced_tag = []
    for i, (w, f, t) in enumerate(zip(word, flag, tag)):
        if (i > 0) and ((f, t) == (flag[i-1], tag[i-1])):
            reduced_word[-1] += w
        else:
            reduced_word.append(w)
            reduced_flag.append(f)
            reduced_tag.append(t)
    return {'word':reduced_word, 'flag':reduced_flag, 'tag':reduced_tag}

def filter_flag(word, flag, filter_list=['nr', 'r', 'ns', 'm', 'eng', 'x']):
    if type(word) != list:
        word = [word]
    if type(flag) != list:
        pos = [flag]
    word_filtered = word
    for i, f in enumerate(flag):
        if f in filter_list:
            word_filtered[i] = f
    return word_filtered

def taggedseq2conll(taggedseq, column_name):
    df = pd.DataFrame(taggedseq, columns=column_name)
    buffer = io.StringIO()
    df.to_csv(buffer, sep='\t', header=False, index=False)
    return buffer.getvalue()

def conll2taggedseq(conll, column_name):
    """[Unverified]
    """
    buffer = io.StringIO(conll)
    df = pd.read_csv(buffer, sep='\t', header=False, names=column_name)
    return df.to_dict()

def taggedseq2standoff(word, tag, tag_format, record_template, brace_index):
    """
    Args:
        word: <list of str>
        tag: <list of str>
        tag_format: <str> Options: 'IO' or 'BIO'
        record_template: <str> The template of the record you want to display.
                         Example: '[text={0}, label={1}]'
        brace_index: <dict> The indexes of the braces used in the
                     `record_template`. The keys should be `text` and `label`.
                     Example: {'text':0, 'label':1}

    Returns:
        A StandoffOutput namedtuple contains the `raw_text` <str> and
    `standoff_annotation` <list of StandoffAnnotation namedtuples>.
    """
    raw_text = ''.join(word)
    word_len = [len(w) for w in word]
    start = [sum(word_len[:i]) for i in range(len(word))]
    end = map(lambda x, y: x + y, start, word_len)

    StandoffAnnotation = namedtuple('StandoffAnnotation',
                                    ['record', 'text', 'label', 'start', 'end'])
    tag_set = list(set(tag))
    label_set = list(set([t[2:] for t in tag_set]))

    # if tag_format == 'IO':
    # TODO


# def standoff2inline
# --------------------------------------------------------

def inline2standoff_greedy(inline_annotated_text, regex_pattern, parentheses_index):
    annotation = get_annotation_set(inline_annotated_text, regex_pattern, parentheses_index)
    raw_text = get_raw_text(inline_annotated_text, annotation)
    standoff_verbose_annotation = locate_annotation(raw_text, annotation)
    StandoffOutput = namedtuple('StandoffOutput', ['raw_text', 'standoff_annotation'])
    return StandoffOutput(raw_text, standoff_verbose_annotation)

def inline2standoff(inline_annotated_text, regex_pattern, parentheses_index, greedy=False):
    StandoffOutput = namedtuple('StandoffOutput', ['raw_text', 'standoff_annotation'])
    if greedy == False:
        # Step 1: Directly extract the annotated records.
        standoff_annotation = get_standoff_annotation(inline_annotated_text,
                                                      regex_pattern,
                                                      parentheses_index)
        raw_text = get_raw_text(inline_annotated_text, standoff_annotation)
    elif greedy == True:
        # Step 1: Get a non-redundant list of Annotations.
        annotation = get_annotation_set(inline_annotated_text,
                                        regex_pattern,
                                        parentheses_index)
        # Step 2: Get the raw (unannotated) text.
        raw_text = get_raw_text(inline_annotated_text, annotation)
        # Step 3: Search the raw text according to the list in Step 1.
        # The results are verbosed obviously.
        standoff_annotation = locate_annotation(raw_text, annotation)
