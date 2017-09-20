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

Let's say we want to convert inline annotated text to conll-formatted text, 
and then convert it back.

We should write a regular expression `regex_pattern` to extract inline 
annotations. 
Use parenthesis in `regex_pattern` to indicate which part is `reocrd`, 
`text` and `label`.

Here `record` means the whole complete annotation, so its parenthesis is the 
outermost one, and its index is always 0. 
Also, you should use parentheses to point out the locations of 
`text` and `label` in the `regex_pattern` and `parenthesis_index`.

```
In [1]: from arsenal.annotation import annotool

In [2]: inline_annotated_text = """<NE id="i0" type="building">The Massachusetts State House</NE> in <NE id="i1" type="city">Boston, MA</NE> houses the offices of many important state figures, including <NE id="i2" type="title">Governor</NE> <NE id="i3" type="person">Deval Patrick</NE> and those of the <NE id="i4" type="organization">Massachusetts General Court</NE>."""

In [3]: regex_pattern = r'(<..\sid.+?type="(.+?)">(.+?)</..>?)'

In [4]: parenthesis_index = {'record':0, 'text':2, 'label':1}
```

Use `inline2standoff()` and `inline2raw()` to convert `inline_annotated_text` 
to `standoff_annotation` and `raw_text`.

```
In [5]: standoff_annotation = annotool.inline2standoff(inline_annotated_text, regex_pattern, parenthesis_index)

In [6]: print(standoff_annotation)
[{'record': '<NE id="i0" type="building">The Massachusetts State House</NE>', 'text': 'The Massachusetts State House', 'label': 'building', 'start': 0, 'end': 29}, 
 {'record': '<NE id="i1" type="city">Boston, MA</NE>', 'text': 'Boston, MA', 'label': 'city', 'start': 33, 'end': 43}, 
 {'record': '<NE id="i2" type="title">Governor</NE>', 'text': 'Governor', 'label': 'title', 'start': 106, 'end': 114}, 
 {'record': '<NE id="i3" type="person">Deval Patrick</NE>', 'text': 'Deval Patrick', 'label': 'person', 'start': 115, 'end': 128}, 
 {'record': '<NE id="i4" type="organization">Massachusetts General Court</NE>', 'text': 'Massachusetts General Court', 'label': 'organization', 'start': 146, 'end': 173}]

In [7]: raw_text = annotool.inline2raw(inline_annotated_text, standoff_annotation)

In [8]: print(raw_text)
The Massachusetts State House in Boston, MA houses the offices of many important state figures, including Governor Deval Patrick and those of the Massachusetts General Court.
```

Use `raw2basicseq()` and `standoff2seq()` to convert `raw_text` and 
`standoff_annotation` to several sequences.

We need specify the language to tokenize and POS tag the text. 
The default tool is `nltk` for English text and `jieba` for Chinese text. 
You can implement this method by yourself.

```
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
```

Use `seq2conll()` to convert these sequences to `conll_text` according to 
their column names. 
Many arguments like `sep_punc` and `eos_mark` is optional.

```
In [14]: conll_text = annotool.seq2conll(seq, column_name=['word', 'pos', 'start', 'end', 'tag'], sep_punc=[',', '.', ';', '?', '!'], eos_mark=True)  # same as `sep_punc=basictool.load_default_sep_punc('en')`

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
```

If we want to convert `conll_text` back to `inline_annotated_text`, 
similar methods are also available. 
You can recoginze them from their name easily.

**Examples (Chinese):**

关于中文的转换方法和英文基本一样，两者共享同一套方法。因此仅做简单展示：

```
In [1]: from arsenal.annotation import annotool

In [2]: inline_annotated_text = """我要订一张[label=起飞时间,value=明天早上]从[label=出发城市,value=杭州]飞往[label=抵达城市,value=哈尔滨]的[label=航班公司,value=厦航]机票。"""

In [3]: regex_pattern = r'(\[label=(.+?),value=(.+?)\])'

In [4]: parenthesis_index = {'record':0, 'text':2, 'label':1}

In [5]: standoff_annotation = annotool.inline2standoff(inline_annotated_text, regex_pattern, parenthesis_index)

In [6]: print(standoff_annotation)
[{'record': '[label=起飞时间,value=明天早上]', 'text': '明天早上', 'label': '起飞时间', 'start': 5, 'end': 9}, 
 {'record': '[label=出发城市,value=杭州]', 'text': '杭州', 'label': '出发城市', 'start': 10, 'end': 12}, 
 {'record': '[label=抵达城市,value=哈尔滨]', 'text': '哈尔滨', 'label': '抵达城市', 'start': 14, 'end': 17}, 
 {'record': '[label=航班公司,value=厦航]', 'text': '厦航', 'label': '航班公司', 'start': 18, 'end': 20}]

In [7]: raw_text = annotool.inline2raw(inline_annotated_text, standoff_annotation)

In [8]: print(raw_text)
我要订一张明天早上从杭州飞往哈尔滨的厦航机票。
```

在转化为序列过程中需要分词、词性标注等，默认中文使用`jieba`，英文使用`nltk`，
其他语言需要自己实现这个方法。

```
In [9]: basic_seq = annotool.raw2basicseq(raw_text, 'zh')

In [10]: print(basic_seq)
{'word': ['我', '要订', '一张', '明天', '早上', '从', '杭州', '飞往', '哈尔滨', '的', '厦航', '机票', '。'], 
'pos': ['r', 'v', 'm', 't', 't', 'p', 'ns', 'v', 'ns', 'uj', 'j', 'n', 'x'], 
'start': [0, 1, 3, 5, 7, 9, 10, 12, 14, 17, 18, 20, 22], 
'end': [1, 3, 5, 7, 9, 10, 12, 14, 17, 18, 20, 22, 23]}

In [11]: tag_seq = annotool.standoff2tagseq(basic_seq['word'], basic_seq['start'], standoff_annotation, tag_format='BIO')

In [12]: print(tag_seq)
{'tag': ['O', 'O', 'O', 'B-起飞时间', 'I-起飞时间', 'O', 'B-出发城市', 'O', 'B-抵达城市', 'O', 'B-航班公司', 'O', 'O']}

In [13]: seq = {**basic_seq, **tag_seq}
```

可以对序列进行个性化处理来适应不同的需要，如人名、地名有时候对任务不重要，
反而会大大加大词表增加计算量，可以用`wordseq2tokenseq()`方法来滤去人名地名，等。
这里暂不做演示。

```
In [14]: conll_text = annotool.seq2conll(seq, column_name=['word', 'pos', 'start', 'end', 'tag'])

In [15]: print(conll_text)
我	r	0	1	O
要订	v	1	3	O
一张	m	3	5	O
明天	t	5	7	B-起飞时间
早上	t	7	9	I-起飞时间
从	p	9	10	O
杭州	ns	10	12	B-出发城市
飞往	v	12	14	O
哈尔滨	ns	14	17	B-抵达城市
的	uj	17	18	O
厦航	j	18	20	B-航班公司
机票	n	20	22	O
。	x	22	23	O
```

还可以将该`conll_text`转化回分离式标注（standoff annotation），甚至再转化回
嵌入式标注（inline annotation）。示例代码后续添加。
