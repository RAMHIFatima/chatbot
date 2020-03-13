# -*- coding: utf-8 -*-
"""
Created on Thu Mar 28 16:51:16 2019

@author: ramhi
"""

# DL packages

from keras.models import Model, Sequential
from keras.layers import Input, LSTM, Dense, Embedding, Dropout, Activation
from keras.layers import add, dot, concatenate, Permute

    ####### Training model
           ###########################
           # placeholders
def model(vocab_size,query_maxlen,story_maxlen):
    input_sequence = Input((story_maxlen,))
    question = Input((query_maxlen,))
    
    # encoders
    # embed the input sequence into a sequence of vectors
    input_encoder_m = Sequential()
    input_encoder_m.add(Embedding(input_dim=vocab_size,
                                  output_dim=64))
    input_encoder_m.add(Dropout(0.3))
    # output: (samples, story_maxlen, embedding_dim)
    
    # embed the input into a sequence of vectors of size query_maxlen
    input_encoder_c = Sequential()
    input_encoder_c.add(Embedding(input_dim=vocab_size,
                                  output_dim=query_maxlen))
    input_encoder_c.add(Dropout(0.3))
    # output: (samples, story_maxlen, query_maxlen)
    
    # embed the question into a sequence of vectors
    question_encoder = Sequential()
    question_encoder.add(Embedding(input_dim=vocab_size,
                                   output_dim=64,
                                   input_length=query_maxlen))
    question_encoder.add(Dropout(0.3))
    # output: (samples, query_maxlen, embedding_dim)
    
    # encode input sequence and questions (which are indices)
    # to sequences of dense vectors
    input_encoded_m = input_encoder_m(input_sequence)
    input_encoded_c = input_encoder_c(input_sequence)
    question_encoded = question_encoder(question)
    
    # compute a 'match' between the first input vector sequence
    # and the question vector sequence
    # shape: `(samples, story_maxlen, query_maxlen)`
    match = dot([input_encoded_m, question_encoded], axes=(2, 2))
    match = Activation('softmax')(match)
    
    
    # add the match matrix with the second input vector sequence
    response = add([match, input_encoded_c])  # (samples, story_maxlen, query_maxlen)
    response = Permute((2, 1))(response)  # (samples, query_maxlen, story_maxlen)
    
    
    # concatenate the match matrix with the question vector sequence
    answer = concatenate([response, question_encoded])
    
    
    # the original paper uses a matrix multiplication for this reduction step.
    # we choose to use a RNN instead.
    answer = LSTM(32)(answer) # (samples, 32)
    # one regularization layer -- more would probably be needed.
    answer = Dropout(0.3)(answer)
    answer = Dense(vocab_size)(answer)  # (samples, vocab_size)
    # we output a probability distribution over the vocabulary
    answer = Activation('softmax')(answer)
    
    # build the final model
    model = Model([input_sequence, question], answer)
    
    return model 
    
        
    
       