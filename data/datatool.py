import random
import numpy as np
import sklearn.preprocessing
from keras.preprocessing.sequence import pad_sequences

def multi_label_binarizer(y, class_pos=None):
    """Convert multi labels into sparse and binary form.

    Args:
        y: <list of list of int> The multi labels in dense and decimal form.
        class_pos: <list of int> Indicate the positions of labels.

    Returns:
        (y, class_pos)
        y: <ndarray> The multi labels in sparse and binary form.
        class_pos: <ndarray> Indicate the positions of labels.

    Examples:
    >>> multi_label_binarizer([[1,2],[5]])
    (array([[1, 1, 0],
            [0, 0, 1]]),  # The sparse and binary label IDs.
     array([1, 2, 5]))  # The corresponding positions of labels.

    >>> multi_label_binarizer([[1,2],[5]], list(range(6)))
    (array([[0, 1, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 1]]),
     array([0, 1, 2, 3, 4, 5]))

    >>> multi_label_binarizer([[1,2],[5]], list(range(1,6)))
    (array([[1, 1, 0, 0, 0],
            [0, 0, 0, 0, 1]]),
     array([1, 2, 3, 4, 5]))
    """
    if class_pos == None:
        mlb = sklearn.preprocessing.MultiLabelBinarizer()
        y = mlb.fit_transform(y)
        class_pos = mlb.classes_
    else:
        y_bin = []
        for row_dec in y:
            row_bin = np.zeros(len(class_pos), dtype=np.int32)
            for d in row_dec:
                row_bin[class_pos.index(d)] = 1
            y_bin.append(row_bin)
        y = np.array(y_bin, dtype=np.int32)
        class_pos = np.array(class_pos, dtype=np.int32)
    return (y, class_pos)

def shuffle_together(x, y):
    if (type(x) == np.ndarray) and (type(y) == np.ndarray):
        x = np.array(x)
        y = np.array(y)
        shuffle_index = np.random.permutation(np.arange(len(x)))
        x_shuffle = x[shuffle_index]
        y_shuffle = y[shuffle_index]
    elif (type(x) == list) and (type(y) == list):
        z = list(zip(x, y))
        random.shuffle(z)
        x_shuffle, y_shuffle = zip(*z)
    else:
        pass
    return (x_shuffle, y_shuffle)

def makeup_batchsize(x, y, batch_size):
    # Add data to make the number of sequences integral multiple of batch size.
    makeup_num = batch_size - len(x) % batch_size
    if (type(x) == np.ndarray) and (type(y) == np.ndarray):
        x = np.concatenate((x, np.array([[0] * x.shape[1]] * makeup_num)))
        y = np.concatenate((y, np.array([[0] * y.shape[1]] * makeup_num)))
    elif (type(x) == list) and (type(y) == list):
        x += [[0]] * makeup_num
        y += [[0]] * makeup_num
    else:
        pass
    return (x, y)

def batch_iter(x, y, batch_size, shuffle, last_batch='makeup', padding='post'):
    if shuffle == True:
        x, y = shuffle_together(x, y)
    # How to process the last batch, makeup or discard.
    if last_batch == 'makeup':
        x, y = makeup_batchsize(x, y, batch_size)
        batch_num = len(x) // batch_size + 1
    elif last_batch == 'discard':
        batch_num = len(x) // batch_size
        x = x[:batch_size * batch_num]
        y = y[:batch_size * batch_num]
    # Generate the iter.
    for i in range(batch_num):
        x_batch = x[i * batch_size:(i + 1) * batch_size]
        y_batch = y[i * batch_size:(i + 1) * batch_size]
        len_batch = [len(x) for x in x_batch]
        # Padding if needed.
        if padding != None:
            x_batch = pad_sequences(x_batch, padding=padding)
            y_batch = pad_sequences(y_batch, padding=padding)
            yield x_batch, y_batch, len_batch




