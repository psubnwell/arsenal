import os
import multiprocessing

from gensim.models import Word2Vec
from gensim.models import KeyedVectors
from gensim.models.word2vec import LineSentence
from sklearn.cluster import AffinityPropagation
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import json
from tqdm import tqdm

from arsenal.basic import basictool

STOPWORD = basictool.load_default_stopword('zh')
STOPFLAG = basictool.load_default_replace_pos('zh')

def linedoc2wordvec(linedoc_file, embedding_size, min_count, core_num=multiprocessing.cpu_count()):
    """Train on the linedoc file and get the word2vec model and vector.

    Args:
        linedoc_file: <str> The path of linedoc txt file. The documents in the
            file should be separated by space and one document per line.
        embedding_size: <int> The dimension of the embedding.
        core_num: <int> The number of CPU cores to work.

    Returns:
        A model file and a vector file under the same dir.
    """
    basedir = os.path.dirname(linedoc_file)
    # Train.
    model = Word2Vec(LineSentence(linedoc_file),
                     size=embedding_size,
                     min_count=min_count,
                     workers=core_num)
    # Save the model and vector.
    model.save(basedir + '/word_embedding.mdl')
    model.wv.save_word2vec_format(basedir + '/word_embedding.vec', binary=False)

def pretrained_vocab_embedding(pretrained_vec_file, word_index_dict):
    """Reorganize the embeddings according the indexes in the `word_index_dict`.

    Args:
        pretrained_vec_file: <str> The path to the word2vec file, which is saved
                             by the `gensim.model.wv.save_word2vec_format()`.
        word_index_dict: <dict> A dict whose items looks like
                         {'hello':0, 'world':1, ...}.
                         The words and indexes should be unique.

    Returns:
        A 2D numpy array with shape (word_num, embedding_dim).
    """
    pretrained_embeding = KeyedVectors.load_word2vec_format(pretrained_vec_file)
    embedding_dim = pretrained_embeding.syn0.shape[1]
    index_word_dict = {word_index_dict[k]:k for k in word_index_dict}
    word_num = len(word_index_dict)
    count = 0  # To count the number of words not in the pretrained embeddings.
    key = list(index_word_dict.keys())
    key.sort()
    vocab_embedding = np.random.randn(key[-1], embedding_dim)  # Initialize.
    for i in range(key[-1] + 1):
        try:
            word = index_word_dict[i]
        except KeyError:
            print('Index {} is not in your dict.'.format(i))
            print('For the compatibility we randomly initialize its embedding.')
        try:
            vocab_embedding[i]= pretrained_embeding[word]
        except (KeyError, UnboundLocalError):
            count += 1
    print('{}/{} ({}%) words are not in the pretrained embeddings.'.format(
        count, word_num, count / word_num * 100
    ))
    print('So the program just randomly initialize them.')
    return np.float32(vocab_embedding)

def get_centroid(name, vec, similarity_threshold):
    """[MemoryError]
    """
    sim_mat = cosine_similarity(vec)
    idx_tuple = np.where((sim_mat > similarity_threshold) & (sim_mat < 0.99))
    if (len(idx_tuple[0]) != 0):
        af = AffinityPropagation(affinity = 'precomputed').fit(cosine_similarity(vec))
        centroid_idx = af.cluster_centers_indices_
        cluster_num = len(centroid_idx)
        centroid_name = [name[centroid_idx[i]] for i in range(cluster_num)]
        centroid_vec = [vec[centroid_idx[i]] for i in range(cluster_num)]

        non_member_name = []
        for n in range(len(name)):
            similarity = [float for n in range(cluster_num)]
            for cn in range(len(centroid_name)):
                similarity[cn] = cosine_similarity([vec[n], centroid_vec[cn]])[0][1]
            if max(similarity) < similarity_threshold:
                non_member_name.append(name[n])
        non_member_vec = basictool.item_select(name, vec, non_member_name)

        centroid_name += get_centroid(non_member_name, non_member_vec, similarity_threshold)
        return centroid_name
    else:
        return []

def generate_synonmy_dict(word_embedding_vec_file, similarity_threshold,
                          stopword=STOPWORD, stopflag=STOPFLAG):
    """[MemoryError]
    """
    word_embedding = KeyedVectors.load_word2vec_format(word_embedding_vec_file)
    word = word_embedding.index2word
    word_embedding = word_embedding.syn0
    # Remove the stopwords and stopflags.
    idx_del = []
    for each_w in word:
        if (each_w.startswith('[') & each_w.endswith(']')) | (each_w in stopword):
            idx_del.append(word.index(each_w))
    word = np.delete(word, idx_del, axis = 0)
    word_embedding = np.delete(word_embedding, idx_del, axis = 0)

    centroid_word = get_centroid(word, word_embedding, similarity_threshold)
    centroid_word_embedding = basictool.item_select(word, word_embedding, centroid_word)
    cluster_num = len(centroid_word)
    synonym = [[] for n in range(cluster_num)]
    discard = []
    for i, we in enumerate(word_embedding):
        sim_mat = [cosine_similarity([we, cwe][0][1]) for cwe in centroid_word_embedding]
        if max(sim_mat) >= similarity_threshold:
            synonym[sim_mat.index(max(sim_mat))].append(word[i])
        else:
            discard.append(word[i])
    synonym_dict = dict([s for s in zip(centroid_word, synonym) if (len(s[1]) != 1)])

    print('--------------------------------------------------')
    print('Synonym dictionary preview:')
    print('Total %d centroid words. Similarity threshold = %.2f' % (len(centroid_word), similarity_threshold))
    print('CENTRIOD'.rjust(10,' ') + '[SYNONMY1, SYNONMY2, ...]')
    example_num = 0
    synonym_dict_show = synonym_dict.copy()
    for i in synonym_dict_show.keys():
        if len(synonym_dict_show[i]) > 8:
            synonym_dict_show[i] = synonym_dict_show[i][:7]
            synonym_dict_show[i].append('...')
        print(str(i).rjust(5,'　') + str(synonym_dict_show[i]))
        example_num += 1
        if example_num >= 10:
            break;
    print('...'.rjust(10,' ') + '[...]')
    print('--------------------------------------------------')

    return synonym_dict
