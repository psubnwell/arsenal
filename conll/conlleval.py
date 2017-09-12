import os
import subprocess
import re

from arsenal.conll import conlltool

def format_nested(token, word, start, end, groundtruth, prediction, delimiter='\t'):
    """Format the output data to fit the requirement of the conlleval.pl.

    Args:
        word: A NESTED word list. (NESTED means the list of lists.)
        groundtruth: A NESTED groundtruth list.
        prediction: A NESTED prediction list.
        delimiter: The delimiter to seperate the data above.

    Return:
        the formatted str block of output data. Unnested blocks are seperated with a blank line.
    """
    out = ''
    for st, sw, ss, se, sg, sp in zip(token, word, start, end, groundtruth, prediction):
        out += format(st, sw, ss, se, sg, sp, delimiter) + '\n'
    return out

def format(token, word, start, end, groundtruth, prediction, delimiter='\t'):
    """Format the output data to fit the requirement of the conlleval.pl.

    Args:
        word: A word list.
        groundtruth: A groundtruth list.
        prediction: A prediction list.
        delimiter: The delimiter to seperate the data above.

    Returns:
        the formatted str block of output data.
    """
    out = ''
    for t, w, s, e, g, p in zip(token, word, start, end, groundtruth, prediction):
        out += delimiter.join((t, w, s, e, g, p)) + '\n'
    return out

def execute(conlleval_pl, input_file):
    """Execute the perl script conlleval.pl.

    Args:
        conlleval_pl: The path of script conlleval.pl.
        input_file: The path of the input file of conlleval.pl.

    Returns:
        A dict of precision, recall and f1_score.
    """
    proc = subprocess.Popen(['perl', conlleval_pl, '-d', '\t'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    # proc.communicate() requires bytes-like object, not str.
    stdout, _ = proc.communicate(open(input_file, 'rb').read())

    return parse(stdout.decode())

def parse(conlleval_stdout):
    """Parse the standard output of the conlleval.pl.

    Args:
        conlleval_stdout: The stdout of the conlleval.pl.

    Returns:
        A dict of precision, recall and f1_score.
    """
    for line in conlleval_stdout.split('\n'):
        if 'accuracy' in line:
            p = float(re.findall(r'precision:\s*(\d+\.\d+)%', line)[0])
            r = float(re.findall(r'recall:\s*(\d+\.\d+)%', line)[0])
            f = float(re.findall(r'FB1:\s*(\d+\.\d+)', line)[0])
    return {'p':p, 'r':r, 'f1':f}

def evaluate(nested_seq, column_name, output_file):
    """Evaluate the performance on the dataset.

    Args:
        word: A NESTED word list. (NESTED means the list of lists.)
        groundtruth: A NESTED groundtruth list.
        prediction: A NESTED prediction list.
        output_file: The file to save the formatted eval dataset.

    Returns:
        A dict of precision, recall and f1_score.
    """
    with open(output_file, 'w') as fout:
        # fout.write(format_nested(token, word, start, end, groundtruth, prediction))
        fout.write(conlltool.nested_seq2conll(nested_seq, column_name))
    # __file__ is the path of this .py file.
    # But __file__ sometimes return abs path and sometimes related path.
    # So use os.path.realpath() to get the abs path.
    conlleval_pl = os.path.dirname(os.path.realpath(__file__)) + '/conlleval.pl'
    return execute(conlleval_pl, output_file)
