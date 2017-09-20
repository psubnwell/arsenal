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

## Sub-package: `annotation`

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

**Example (TL;DR):**

```
In [1]: from arsenal.annotation import annotool

In [2]: inline_annotated_text = """<NE id="i0" type="building">The Massachusetts State House</NE> in <NE id="i1" type="city">Boston, MA</NE> houses the offices of many important state figures, including <NE id="i2" type="title">Governor</NE> <NE id="i3" type="person">Deval Patrick</NE> and those of the <NE id="i4" type="organization">Massachusetts General Court</NE>."""

In [3]: regex_pattern = r'(<..\sid.+?type="(.+?)">(.+?)</..>?)'

In [4]: parenthesis_index = {'record':0, 'text':2, 'label':1}

In [5]: conll_text = annotool.inline2conll(inline_annotated_text, regex_pattern, parenthesis_index, language_code='en', tag_format='BIO')

In [6]: print(conll_text)
The	DT	0	3	B-building
Massachusetts	NNP	4	17	I-building
State	NNP	18	23	I-building
House	NNP	24	29	I-building
in	IN	30	32	O
Boston	NNP	33	39	B-city
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
Governor	NNP	106	114	B-title
Deval	NNP	115	120	B-person
Patrick	NNP	121	128	I-person
and	CC	129	132	O
those	DT	133	138	O
of	IN	139	141	O
the	DT	142	145	O
Massachusetts	NNP	146	159	B-organization
General	NNP	160	167	I-organization
Court	NNP	168	173	I-organization
.	.	173	174	O
```

**Example (English):**

Refer to [./annotation/README.md](./annotation/README.md)

**Example (Chinese):**

关于中文的转换方法和英文基本一样，两者共享同一套方法。

详见 [./annotation/README.md](./annotation/README.md)

## Sub-package: `conll`

## Sub-package: `batch`

This toolkit is designed for parallel acceleration.

## Sub-package: `wordvec`
