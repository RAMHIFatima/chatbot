# -*- coding: utf-8 -*-
"""
Created on Thu Mar 28 16:51:16 2019

@author: ramhi
"""


# DL packages
import re
from keras.preprocessing.sequence import pad_sequences

import numpy as np
import tarfile
from keras.utils.data_utils import get_file
from functools import reduce


####### some usefull functions
       ###########################
def vectorize_stories(data, word_idx, story_maxlen, query_maxlen):
    """vectorize stories and queries + padding  """
    X_stories = []
    X_queries = []
    answers = []
    for story, query, answer in data:
        word_vect = [word_idx[w] for w in story]
        wordq_vect = [word_idx[w] for w in query]
        y = np.zeros(len(word_idx) + 1)
        y[word_idx[answer]] = 1
        X_stories.append(word_vect)
        X_queries.append(wordq_vect)
        answers.append(y)
    return (pad_sequences(X_stories, maxlen=story_maxlen),
            pad_sequences(X_queries, maxlen=query_maxlen), np.array(answers))
    
    
    
def get_stories(f, only_supporting=False, max_length=None):
    """"""
    data = parse_stories(f.readlines(), only_supporting=only_supporting)
    flatten = lambda data: reduce(lambda x, y: x + y, data)
    data = [(flatten(story), q, answer) for story, q, answer in data if not max_length or len(flatten(story)) < max_length]
    return data


####### analysing storing
       #########################
def parse_stories(lines, only_supporting=False):
    data = []
    story = []
    for line in lines:
        line = line.decode('utf-8').strip()
        nid, line = line.split(' ', 1)
        nid = int(nid)
        if nid == 1:
            story = []
        if '\t' in line:
            q, a, supporting = line.split('\t')
            q = tokenize(q)
            q=[i.lower() for i in q]
            substory = None
            if only_supporting:
                # Only select the related substory
                supporting = map(int, supporting.split())
                substory = [story[i - 1] for i in supporting]
            else:
                # Provide all the substories
                substory = [x for x in story if x]
            data.append((substory, q, a))
            story.append('')
        else:
            sent = tokenize(line)
            story.append(sent)
    return data


####### get vocabulary from the dataset
       #########################
def get_vocab(data):
    vocab = set()
    for story, q, answer in data:
        vocab |= set(story + q + [answer])
    vocab = sorted(vocab)
    print()
    return vocab


####### transform data into tokens
       #########################
def tokenize(sent):

    return [x.strip() for x in re.split('(\W+)?', sent) if x.strip()]

    

####### Download Data
       #########################
def download_data():
    try :
        path = get_file('babi-tasks-v1-2.tar.gz', origin='https://s3.amazonaws.com/text-datasets/babi_tasks_1-20_v1-2.tar.gz')
    except:
        print('Error downloading dataset, please download it manually:\n'
              '$ wget http://www.thespermwhale.com/jaseweston/babi/tasks_1-20_v1-2.tar.gz\n'
              '$ mv tasks_1-20_v1-2.tar.gz ~/.keras/datasets/babi-tasks-v1-2.tar.gz')
        raise
    tar = tarfile.open(path)
    
    challenges = {
        # QA1 with 10,000 samples
        'single_supporting_fact_10k': 'tasks_1-20_v1-2/en-10k/qa1_single-supporting-fact_{}.txt',
        # QA2 with 10,000 samples
        'two_supporting_facts_10k': 'tasks_1-20_v1-2/en-10k/qa2_two-supporting-facts_{}.txt',
        
    }
    challenge_type = 'single_supporting_fact_10k'
    challenge = challenges[challenge_type]
    return challenge,tar


####### get Stories from Data
       ###########################
def preprocessing_data():
    
    challenge,tar=download_data()
    train_stories = get_stories(tar.extractfile(challenge.format('train')))
    test_stories = get_stories(tar.extractfile(challenge.format('test')))
    d=train_stories + test_stories
    vocab=get_vocab(d)
    vocab_size = len(vocab) + 1
    
    story_maxlen = max(map(len, (x for x, _, _ in train_stories + test_stories)))
    query_maxlen = max(map(len, (x for _, x, _ in train_stories + test_stories)))
    word_idx = dict((c, i + 1) for i, c in enumerate(vocab))
    inputs_train, queries_train, answers_train = vectorize_stories(train_stories,
                                                                   word_idx,
                                                                   story_maxlen,
                                                                   query_maxlen)
    inputs_test, queries_test, answers_test = vectorize_stories(test_stories,
                                                                word_idx,
                                                                story_maxlen,query_maxlen)
    return  inputs_test, queries_test, answers_test,inputs_train, queries_train,vocab_size,story_maxlen,query_maxlen,word_idx,test_stories



    
       