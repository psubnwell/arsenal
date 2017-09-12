# Arsenal

> My personal toolkit.
> 我的私人工具箱。

## Prerequisite

* Python3 only.
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

## Annotation

This toolkit is designed to analyze the annotation in the corpus used in the 
natural language processing(NLP) task. See the examples below to know how to 
use it for your own tasks.

(TODO)
