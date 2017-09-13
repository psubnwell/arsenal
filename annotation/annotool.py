import os
import io
import re
import itertools
import operator
from collections import namedtuple

import pandas as pd

import nltk
import jieba
import jieba.posseg

from arsenal.basic import basictool
from arsenal.linedoc import linedoctool


def inline2standoff(inline_annotated_text, regex_pattern, parenthesis_index):
    """Extract annotations from a inline-annotated text, with their `start`
    and `end` locations in its raw text.

    Args:
        inline_annotated_text: <str> A text contains inline annotation.
        regex_pattern: <raw str> A regular expression to match the inline
                       annotations in the `inline_annotated_text`.
        parenthesis_index: <dict> A dict contains 3 keys: `record`, `text`
                           and `label`, whose values are their parenthesis
                           locations in the `regex_pattern`.

    Returns:
        A complete list of standoff annotations <list of dict> in the
    `inline_annotated_text`, with `record`, `text`, `label`, `start` and `end` keys.

    (This method is a little bit hard to understand, better to refer to the
    example in the doc.)
    """
    res = re.finditer(regex_pattern, inline_annotated_text)
    # The extracted spans (`start` and `end` values) are respect to the
    # `inline_annotated_text`, waiting to be corrected.
    standoff_annotation_temp = [{
        'record':r.group(parenthesis_index['record'] + 1),
        'text':r.group(parenthesis_index['text'] + 1),
        'label':r.group(parenthesis_index['label'] + 1),
        'start':r.start(),
        'end':r.end()
    } for r in res]
    # Get the true spans w.r.t the raw text.
    standoff_annotation = []
    for i, a in enumerate(standoff_annotation_temp):
        if i == 0:
            standoff_annotation.append({
                'record':a['record'],
                'text':a['text'],
                'label':a['label'],
                'start':a['start'],
                'end':a['start'] + len(a['text'])
            })
        elif i > 0:
            start = standoff_annotation[-1]['end'] + \
                    (a['start'] - standoff_annotation_temp[i-1]['end'])
            end = start + len(a['text'])
            standoff_annotation.append({
                'record':a['record'],
                'text':a['text'],
                'label':a['label'],
                'start':start,
                'end':end
            })
    return standoff_annotation

def inline2raw(inline_annotated_text, annotation):
    """Convert a inline-annotated text to its raw text form, according to the
    given annotations.

    Args:
        inline_annotated_text: <str> A text contains inline annotation.
        annotation: <list of dict> A list of annotations, each of which should
                    have at least `record` and `text` items.

    Returns:
        The raw text without inline annotations.
    """
    raw_text = inline_annotated_text
    for a in annotation:
        raw_text = raw_text.replace(a['record'], a['text'])
    return raw_text

def standoff2inline(raw_text, standoff_annotation):
    """Convert the raw text to the inline-annotated text according to the given
    standoff annotations.

    Args:
        raw_text: <str>
        standoff_annotation: <list of dict> A list of standoff annotations
    contains `reocrd`, `text`, `label`, `start` and `end` items.

    Returns:
        The inline-annotated text.
    """
    # Get the indexes to split the `raw_text`.
    start_index = [a['start'] for a in standoff_annotation]
    end_index = [a['end'] for a in standoff_annotation]
    split_index = list(set(start_index + end_index))
    split_index.sort()
    # Cut the `raw_text` into many sub strings according to the `split_index`.
    substr = basictool.split_with_indexes(raw_text, split_index)
    # Substitute some strings with a complete `record` of annotations.
    for a in standoff_annotation:
        substr[split_index.index(a['start']) + 1] = a['record']
    inline_inline_annotated_text = ''.join(substr)
    return inline_inline_annotated_text

def raw2basicseq(raw_text, language_code, core_num=1):
    if language_code == 'zh':
        if core_num > 1:
            jieba.enable_parallel(core_num)
        pair = list(jieba.posseg.cut(raw_text))
        word_seq = [p.word for p in pair]
        pos_seq = [p.flag for p in pair]
        word_len_seq = [len(w) for w in word_seq]
        start_seq = [sum(word_len_seq[:i]) for i in range(len(word_seq))]
        end_seq = list(map(lambda x, y: x + y, start_seq, word_len_seq))
    elif language_code == 'en':
        word_seq = nltk.word_tokenize(raw_text)
        pair = nltk.pos_tag(word_seq)
        pos_seq = [p[1] for p in pair]
        start_seq = []
        end_seq = []
        idx = 0
        for w in word_seq:
            idx = raw_text.find(w, idx)
            start_seq.append(idx)
            end_seq.append(idx + len(w))
            idx = end_seq[-1]
    else:
        pass
        # Other languages.
    return {'word':word_seq, 'pos':pos_seq, 'start':start_seq, 'end':end_seq}

def basicseq2raw(word_seq, start_seq, end_seq):
    num = len(word_seq)
    space_seq = [(start_seq[i + 1] - end_seq[i]) * ' ' for i in range(num - 1)]
    space_seq.append('')
    return ''.join(list(map(lambda x, y: x + y, word_seq, space_seq)))

def standoff2tagseq(word_seq, start_seq, standoff_annotation, tag_format):
    num = len(word_seq)
    tag_seq = ['O'] * len(word_seq)
    for a in standoff_annotation:
        for i in range(num):
            if a['start'] >= start_seq[i] and a['start'] < start_seq[min(i+1, num-1)]:
                if tag_format == 'IO':
                    tag_seq[i] = 'I-' + a['label']
                elif tag_format == 'BIO':
                    tag_seq[i] = 'B-' + a['label']
            elif start_seq[i] > a['start'] and start_seq[i] < a['end']:
                tag_seq[i] = 'I-' + a['label']
            else:
                pass
    return {'tag':tag_seq}

def tagseq2standoff(raw_text, word_seq, start_seq, end_seq, tag_seq,
                    tag_format):
    num = len(word_seq)
    standoff_annotation = []
    if tag_format == 'IO':
        start_tag = [next(g) for k, g in itertools.groupby(
            enumerate(tag_seq), key=operator.itemgetter(1)
        )]
        label = [t[2:] for s, t in start_tag if t != 'O']
        span = [(s, min(start_tag[i + 1][0] - 1, num))
                 for i, (s, t) in enumerate(start_tag) if t != 'O']
        standoff_annotation = [{
            'text': raw_text[start_seq[span[i][0]]:end_seq[span[i][1]]],
            'label': label[i],
            'start': start_seq[span[i][0]],
            'end': end_seq[span[i][1]]
        } for i in range(len(label))]
        for a in standoff_annotation:
            a['record'] = '<label="{}", text="{}">'.format(a['label'], a['text'])
    return standoff_annotation

def wordseq2tokenseq(word_seq, pos_seq, replace_pos):
    token_seq = word_seq.copy()
    for i, pos in enumerate(pos_seq):
        if pos in replace_pos:
            token_seq[i] = '[{}]'.format(pos)
    return {'token': token_seq}

def inline2seq(inline_annotated_text, regex_pattern, parenthesis_index,
               language_code, tag_format, core_num=1):
    standoff_annotation = inline2standoff(inline_annotated_text, regex_pattern, parenthesis_index)
    raw_text = inline2raw(inline_annotated_text, standoff_annotation)
    basic_seq = raw2basicseq(raw_text, language_code, core_num)
    tag_seq = standoff2tagseq(basic_seq['word'], basic_seq['start'],
                              standoff_annotation, tag_format)
    return {**basic_seq, **tag_seq}

def seq2inline(word_seq, start_seq, end_seq, tag_seq, tag_format):
    raw_text = basicseq2raw(word_seq, start_seq, end_seq)
    standoff_annotation = tagseq2standoff(raw_text, word_seq, start_seq,
                                          end_seq, tag_seq, tag_format='IO')
    return standoff2inline(raw_text, standoff_annotation)

def seq2conll(seq, column_name, column_sep='\t', sep_punc=False, eos_mark=False):
    df = pd.DataFrame(seq, columns=column_name)
    if eos_mark == True:
        seq_len = df.shape[0]
        df.loc[seq_len] = '[EOS]'
        df.loc[seq_len, ['tag']] = 'O'
    buffer = io.StringIO()
    df.to_csv(buffer, sep=column_sep, header=False, index=False)
    conll_text = buffer.getvalue().strip().replace('\n ', '\n')
    if sep_punc != False:
        line = conll_text.split('\n')
        sep_idx = [i + 1 for i, l in enumerate(line) \
                   if df.loc[i, ['word']].item() in sep_punc \
                   and df.loc[i + 1, ['word']].item() != '[EOS]']
        # Descending the `sep_idx` to insert blank lines.
        for i in sep_idx[::-1]:
            line.insert(i, '\n')
        conll_text = '\n'.join(line).replace('\n\n\n', '\n\n')
    return conll_text

def conll2seq(conll_text, column_name, column_sep='\t', remove_sep_line=True,
              remove_eos_mark=True):
    if remove_sep_line == True:
        conll_text.replace('\n\n', '\n')
    buffer = io.StringIO(conll_text)
    df = pd.read_csv(buffer, sep=column_sep, header=None, names=column_name)
    if remove_eos_mark == True:
        df = df[:-1]
    return df.to_dict(orient='list')

def analyze_keyword(annotation, stopword, filter_flag):
    """[Unverified] Get the keywords and their IDF values and covering percentages.

    Args:
        annotation: <list of Annotation namedtuples> The more the better.
        label: <str> The specific label of Annotation namedtuples you want to
               focus and analyze its keywords.

    Returns:
        A IDFOutput namedtuple with keys: `keyword`, `idf`, `percent`.
    Each value is a sorted list.
    """
    label = list(set([a['label'] for a in annotation]))
    filter_flag = ['[{}]'.format(f) for f in filter_flag]
    stopword += filter_flag
    theme_dict = {}
    for l in label:
        text = [a['text'] for a in annotation if a['label'] == l]
        text_seg = linedoctool.possegment(text)
        text_token = [t.split(' ') for t in text_seg]
        # Calculate the IDF values.
        s = SnowNLP(text_token)
        # Remove words like '[x]', sice they are not true words but filtered flags.
        for sw in stopword:
            s.idf.pop(sw, None)
        keyword = list(s.idf.keys())
        idf = list(s.idf.values())
        # Sort the `keyword` and `idf` together. Lower IDF means more important.
        # Notice this is the opposite with the traditional TF-IDF way.
        idf_sorted, keyword_sorted = zip(*sorted(zip(idf, keyword)))
        # $ IDF = log_2 (D / D_w) $, where
        #     D is the number of total documents,
        #     D_w is the number of documents contain the keyword.
        # $ coverage = D_w / D = 1 / (2 ^ IDF) $.
        # The higher the `coverage`, the more important the keywords.
        coverage_sorted = [1 / 2**idf for idf in idf_sorted]
        Keyword = namedtuple('Keyword', ['keyword', 'coverage'])
        theme_dict.update({l: Keyword(keyword_sorted, coverage_sorted)})
    return theme_dict



if __name__ == '__main__':
    inline_annotated_text_zh = """被告人邱某以“掐死你”的语言[nameCN=抢劫罪,value=威胁罗某，捂住易某的嘴巴，抢得金项链]就跑，因而构成抢劫罪。"""
    regex_pattern = r'(\[nameCN=(.+?),value=(.+?)\])'
    parenthesis_index = {'record':0, 'text':2, 'label':1}
    # standoff_annotation = inline2standoff(inline_annotated_text_zh, regex_pattern, parenthesis_index)
    # raw_text = inline2raw(inline_annotated_text_zh, standoff_annotation)
    # basic_seq = raw2basicseq(raw_text, 'zh')
    # tag_seq = standoff2tagseq(basic_seq['word'], basic_seq['start'], standoff_annotation, 'IO')
    seq = inline2seq(inline_annotated_text_zh, regex_pattern, parenthesis_index, language_code='zh', tag_format='IO', core_num=4)
    token_seq = wordseq2tokenseq(seq['word'], seq['pos'],
                                 replace_pos=['nr', 'ns', 'm', 'eng'])
    conll_text = seq2conll({**token_seq, **seq}, column_name=['token', 'word', 'pos', 'start', 'end', 'tag'], sep_punc=basictool.ZH_SEP_PUNC, eos_mark=True)
    print(conll_text)

    raw_text = basicseq2raw(seq['word'], seq['start'], seq['end'])
    standoff_annotation = tagseq2standoff(
        raw_text, seq['word'], seq['start'], seq['end'], seq['tag'],
        tag_format='IO'
    )
    inline_annotated_text = standoff2inline(raw_text, standoff_annotation)
    print(raw_text)
    for i in standoff_annotation:
        print(i)
    print(inline_annotated_text)

    print('\n--------------------------------------\n')

    inline_annotated_text_en = """<NE id="i0" type="building">The Massachusetts State House</NE> in <NE id="i1" type="city">Boston, MA</NE> houses the offices of many important state figures, including <NE id="i2" type="title">Governor</NE> <NE id="i3" type="person">Deval Patrick</NE> and those of the <NE id="i4" type="organization">Massachusetts General Court</NE>."""
    regex_pattern = r'(<..\sid.+?type="(.+?)">(.+?)</..>?)'
    parenthesis_index = {'record':0, 'text':2, 'label':1}
    # standoff_annotation = inline2standoff(inline_annotated_text_en, regex_pattern, parenthesis_index)
    # raw_text = inline2raw(inline_annotated_text_en, standoff_annotation)
    # basic_seq = raw2basicseq(raw_text, 'en')
    # tag_seq = standoff2tagseq(basic_seq['word'], basic_seq['start'], standoff_annotation, 'IO')
    seq = inline2seq(inline_annotated_text_en, regex_pattern, parenthesis_index, language_code='en', tag_format='IO', core_num=4)
    token_seq = wordseq2tokenseq(seq['word'], seq['pos'],
                                 replace_pos=['NNP', 'PRP', 'CD', 'NN'])
    conll_text = seq2conll({**token_seq, **seq}, column_name=['token', 'word', 'pos', 'start', 'end', 'tag'], sep_punc=basictool.EN_SEP_PUNC, eos_mark=True)
    print(conll_text)

    raw_text = basicseq2raw(seq['word'], seq['start'], seq['end'])
    standoff_annotation = tagseq2standoff(
        raw_text, seq['word'], seq['start'], seq['end'], seq['tag'],
        tag_format='IO'
    )
    inline_annotated_text = standoff2inline(raw_text, standoff_annotation)
    print(raw_text)
    for i in standoff_annotation:
        print(i)
    print(inline_annotated_text)

