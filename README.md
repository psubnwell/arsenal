# Arsenal

> My personal toolkit.

> 我的私人工具箱。

## Prerequisite

* `Python3` only.
* `pip3 install numpy pandas nltk jieba`

## Installation

Download this repo and put it wherever you like, then add the path to 
`PYTHONPATH` environment variable. For example, put `arsenal` under `/my/path/`,
then edit `~/.bash_profile`(or `~/.bashrc`) to attach this line:
```
export PYTHONPATH="/my/path:$PYTHONPATH"
```
Reopen a terminal window and see if it works:
```
$ python3
>>> from arsenal.annotation import annotool
```

## Package: Annotation

This toolkit is designed to analyze the annotations in the corpus used in the 
natural language processing (NLP) task. 

For a overview of different kinds of annotations and related pros and cons, 
please refer to the book: *Natural Language Annotation for Machine Learning*.

**Features:**

1) Basically, it supplies the methods to convert between different formats: 
inline annotation, standoff annotation, CoNLL format, etc.

2) Theoretically, most methods are compatible with multiple languages. 
So different language can share the same methods 
(except some language-specific methods e.g. tokenizing, POS tagging.) 
But Chinese and English are originally supported and tested.

**Examples:**

1) Convert inline-annotated text to conll-formatted text. (English example)

<pre  style="white-space: pre-wrap; word-break: keep-all;">
In [1]: from arsenal.annotation import annotool

In [2]: inline_annotated_text_en = """<NE id="i0" type="building">The Massachusetts State House</NE> in <NE id="i1" type="city">Boston, MA</NE> houses the offices of many important state figures, including <NE id="i2" type="title">Governor</NE> <NE id="i3" type="person">Deval Patrick</NE> and those of the <NE id="i4" type="organization">Massachusetts General Court</NE>."""

In [3]: regex_pattern = r'(<..\sid.+?type="(.+?)">(.+?)</..>?)'

In [4]: parenthesis_index = {'record':0, 'text':2, 'label':1}

In [5]: standoff_annotation = annotool.inline2standoff(inline_annotated_text_en, regex_pattern, parenthesis_index)

In [6]: print(standoff_annotation)
[{'record': '<NE id="i0" type="building">The Massachusetts State House</NE>', 'text': 'The Massachusetts State House', 'label': 'building', 'start': 0, 'end': 29}, 
 {'record': '<NE id="i1" type="city">Boston, MA</NE>', 'text': 'Boston, MA', 'label': 'city', 'start': 33, 'end': 43}, 
 {'record': '<NE id="i2" type="title">Governor</NE>', 'text': 'Governor', 'label': 'title', 'start': 106, 'end': 114}, 
 {'record': '<NE id="i3" type="person">Deval Patrick</NE>', 'text': 'Deval Patrick', 'label': 'person', 'start': 115, 'end': 128}, 
 {'record': '<NE id="i4" type="organization">Massachusetts General Court</NE>', 'text': 'Massachusetts General Court', 'label': 'organization', 'start': 146, 'end': 173}]

In [7]: raw_text = annotool.inline2raw(inline_annotated_text_en, standoff_annotation)

In [8]: print(raw_text)
The Massachusetts State House in Boston, MA houses the offices of many important state figures, including Governor Deval Patrick and those of the Massachusetts General Court.

In [9]: basic_seq = annotool.raw2basicseq(raw_text, 'en')

In [10]: print(basic_seq)
{'word': ['The', 'Massachusetts', 'State', 'House', 'in', 'Boston', ',', 'MA', 'houses', 'the', 'offices', 'of', 'many', 'important', 'state', 'figures', ',', 'including', 'Governor', 'Deval', 'Patrick', 'and', 'those', 'of', 'the', 'Massachusetts', 'General', 'Court', '.'], 
 'pos': ['DT', 'NNP', 'NNP', 'NNP', 'IN', 'NNP', ',', 'NNP', 'NNS', 'DT', 'NNS', 'IN', 'JJ', 'JJ', 'NN', 'NNS', ',', 'VBG', 'NNP', 'NNP', 'NNP', 'CC', 'DT', 'IN', 'DT', 'NNP', 'NNP', 'NNP', '.'], 
 'start': [0, 4, 18, 24, 30, 33, 39, 41, 44, 51, 55, 63, 66, 71, 81, 87, 94, 96, 106, 115, 121, 129, 133, 139, 142, 146, 160, 168, 173], 
 'end': [3, 17, 23, 29, 32, 39, 40, 43, 50, 54, 62, 65, 70, 80, 86, 94, 95, 105, 114, 120, 128, 132, 138, 141, 145, 159, 167, 173, 174]}

In [11]: tag_seq = annotool.standoff2tagseq(basic_seq['word'], basic_seq['start'], standoff_annotation, tag_format='IO')

In [12]: print(tag_seq)
{'tag': ['I-building', 'I-building', 'I-building', 'I-building', 'O', 'I-city', 'I-city', 'I-city', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'I-title', 'I-person', 'I-person', 'O', 'O', 'O', 'O', 'I-organization', 'I-organization', 'I-organization', 'O']}

In [13]: seq = {**basic_seq, **tag_seq}

In [14]: conll_text = annotool.seq2conll(seq, column_name=['word', 'pos', 'start', 'end', 'tag'], sep_punc=[',', '.', ';', '?', '!'], eos_mark=True)  # same as `sep_punc=basictool.load_default_sep_punc('en')`_

In [15]: print(conll_text)
The	DT	0	3	I-building
Massachusetts	NNP	4	17	I-building
State	NNP	18	23	I-building
House	NNP	24	29	I-building
in	IN	30	32	O
Boston	NNP	33	39	I-city
,	,	39	40	I-city

MA	NNP	41	43	I-city
houses	NNS	44	50	O
the	DT	51	54	O
offices	NNS	55	62	O
of	IN	63	65	O
many	JJ	66	70	O
important	JJ	71	80	O
state	NN	81	86	O
figures	NNS	87	94	O
,	,	94	95	O

including	VBG	96	105	O
Governor	NNP	106	114	I-title
Deval	NNP	115	120	I-person
Patrick	NNP	121	128	I-person
and	CC	129	132	O
those	DT	133	138	O
of	IN	139	141	O
the	DT	142	145	O
Massachusetts	NNP	146	159	I-organization
General	NNP	160	167	I-organization
Court	NNP	168	173	I-organization
.	.	173	174	O
[EOS]	[EOS]	[EOS]	[EOS]	O
</pre>

2) Convert conll-formatted text to inline-annotated text. (English example)
