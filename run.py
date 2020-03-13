#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 19 14:15:08 2019
@author: fzed
"""
####### packages
       ###########################
from flask import request,Flask,render_template,jsonify
from flask_bootstrap import Bootstrap
# DL packages
import numpy as np
import keras.backend as keras_backend 
from keras.models import model_from_json
import pickle
from preprocessingData import tokenize,preprocessing_data

app=Flask(__name__)

Bootstrap(app)



num=0
inp_ques=False   
stor=''
inputs_test, queries_test, _,_, _,_,story_maxlen,query_maxlen,word_idx,test_stories=preprocessing_data()
    
@app.route('/')
def index():
    return render_template('home.html')

 

####### for the first page
       ###########################
@app.route('/show_story',methods=['POST'])
def show_story():
    """ this function takes the number from the input,and return the 
    corresponding story, and then starts the chat  """
    
    if request.method =='POST':
        num=request.form['num']
        story_list=test_stories[int(num)][0]
        stor=' '.join(word for word in story_list)
        with open('data', 'wb') as f:
            pickle.dump([stor,num], f, 2)
        
        return render_template('chat.html', story = stor,number = num)
        #return jsonify({'story':stor,'number':num})
   

## for testing ajax stuff 


@app.route('/predict_',methods=['POST'])
def predict():  
    """this function takes the question the user asks, and predict the answer"""
    if request.method=='POST':
        # open data file , where the story and it's number are 
        with open('data', 'rb') as file:
            stor, num = pickle.load(file)
        
        question=request.form['ques']#get the question the user entered
        
        ques_token=tokenize(question) # tokenize the question
        ques_token=[i.lower() for i in ques_token]# 
        try:
            word_tokens = [word_idx[w] for w in ques_token] # vectorise the question
            print(word_tokens)
                
            input_stories=np.zeros((1001,68)) # array to store data
            input_stories[:1000]=inputs_test 
            input_stories[1000]=inputs_test[int(num)]# add the new story
            queries= np.zeros((1001,4))# array to store questions
            queries[:1000]=queries_test# 
            queries[1000]=word_tokens# add the new question
                # loading the model 
            json_file = open('model1.json', 'r')
            # print(json_file)
            loaded_model_json = json_file.read()
            # print(loaded_model_json)
            # json_file.close()

            loaded_model = model_from_json(loaded_model_json)
                # load weights into new model
            loaded_model.load_weights("model1.h5")
                # predict the answer 
            pred=loaded_model.predict(([input_stories, queries]))
            val_max = np.argmax(pred[1000])
            keras_backend.clear_session() # destruction du graph courant
            
            for key, val in word_idx.items():
                if val == val_max:
                    predicted_word = key
            predicted_word=predicted_word.title()
            print(predicted_word)
            return jsonify({'story':stor,'pred':predicted_word, 'question':question,'number':num,'name':ques_token[2].title(),'word':word_tokens})

        except KeyError:
          return jsonify({'error': 'Please enter a question based on the story ','story':stor,'question':question,'number':num,'name':ques_token[2].title()})
  
        
####### Home page
       ###########################
@app.route('/return_1',methods=['POST'])
def return_index():
    if request.method=='POST':
        return render_template('home.html')


####### 404 error page
       ###########################
@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('NotFound.html'), 404   
        
if __name__=='__main__':
    app.run(debug=True)