import os
import subprocess
import re

def format_nested(word, groundtruth, prediction, delimiter=' '):
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
    for sw, sg, sp in zip(word, groundtruth, prediction):
        out += format(sw, sg, sp, delimiter) + '\n'
    return out

def format(word, groundtruth, prediction, delimiter=' '):
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
    for w, g, p in zip(word, groundtruth, prediction):
        out += delimiter.join((w, g, p)) + '\n'
    return out

def exec(conlleval_pl, input_file):
    """Execute the perl script conlleval.pl.

    Args:
        conlleval_pl: The path of script conlleval.pl.
        input_file: The path of the input file of conlleval.pl.

    Returns:
        A dict of precision, recall and f1_score.
    """
    proc = subprocess.Popen(['perl', conlleval_pl], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
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

def eval(word, groundtruth, prediction, output_file):
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
        fout.write(format_nested(word, groundtruth, prediction))
    return exec('./conlleval.pl', output_file)