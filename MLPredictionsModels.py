# -*- coding: utf-8 -*-
"""
Created on Fri Feb  2 01:41:19 2018

This file contains the implementation of the sequence prediction model with LTSM
It predict the next activities based on the sequence of activities

"""

# -*- coding: utf-8 -*-


import theano
# tensorflow
import tensorflow
# keras

from numpy import array
from numpy import argmax
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder
import numpy as np
import pandas as pd
import math
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
import json

import numpy
import matplotlib.pyplot as plt
from pandas import read_csv
import math
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from numpy import array

from numpy import argmax
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder
import numpy as np
import matplotlib.pyplot as plt
from sklearn.neighbors import LocalOutlierFactor
from lsanomaly import LSAnomaly


  

################# Prediction section for a single Activity #####################
def get_dataset_each_activity_sequence(data_df,activity_type):
    new_data = []
    for row in data_df.itertuples():
    
        previous_data = ""
        if(activity_type == 'sleep_duration'):
            new_data.append((row.sleep_duration))
        elif(activity_type == 'living_room'):
            new_data.append((row.daily_living_room_mvt))
        elif(activity_type == 'kitchen'):
            new_data.append((row.daily_kitchen_mvt))
    return new_data
    
# convert an array of values into a dataset matrix
def create_dataset_each_activity(dataset, look_back=1):
    dataX, dataY = [], []
    for i in range(len(dataset)-look_back-1):
        a = dataset[i:(i+look_back)]
        dataX.append(a)
        dataY.append(dataset[i + look_back])
    return numpy.array(dataX), numpy.array(dataY)
        
    
#Model Learning with LSTM
# This model predict the future activity based on the previous activities
def each_adl_activity_prediction(data_df,activity_type):
    try:
        dic_result = {}
        new_data = get_dataset_each_activity_sequence(data_df,activity_type) 
        if(activity_type == 'sleep_duration'):
            dataset = data_df.sleep_duration.values
        elif(activity_type == 'living_room'):
            dataset = data_df.daily_living_room_mvt.values
        elif(activity_type == 'kitchen'):
            dataset = data_df.daily_kitchen_mvt.values
            
        dataset = dataset.astype('float32')
        dataset =dataset.reshape(-1,1)
        # normalize the dataset
        scaler = MinMaxScaler(feature_range=(0, 1))
        dataset = scaler.fit_transform(dataset)
        # split into train and test sets
        train_size = int(len(dataset) * 0.80)
        test_size = len(dataset) - train_size
        #print (train_size,test_size)
        train = dataset[0:train_size] 
        test = dataset[test_size:len(dataset)-1]
            
        # reshape into X=t and Y=t+1
        look_back = 1
        trainX, trainY = create_dataset_each_activity(train, look_back)
        testX, testY = create_dataset_each_activity(test, look_back)
        # reshape input to be [samples, time steps, features]
        trainX = numpy.reshape(trainX, (trainX.shape[0], 1, trainX.shape[1]))
        testX = numpy.reshape(testX, (testX.shape[0], 1, testX.shape[1]))
            
        
        
        # define example of categorical data
        values = array(new_data)
        # integer encode
        label_encoder = LabelEncoder()
        integer_encoded = label_encoder.fit_transform(values)
        
        # binary encode
        onehot_encoder = OneHotEncoder(sparse=False)
        integer_encoded = integer_encoded.reshape(len(integer_encoded), 1)
        onehot_encoded = onehot_encoder.fit_transform(integer_encoded)
        
        # invert first example
        inverted = label_encoder.inverse_transform([argmax(onehot_encoded[0, :])])
        
        
        model = Sequential()
        model.add(LSTM(4, input_shape=(1, look_back)))
        model.add(Dense(1))
        model.compile(loss='mse', optimizer='adam', metrics=["accuracy"])
        model.fit(trainX, trainY, epochs=10, batch_size=2, verbose=2)
        # make predictions
        trainPredict = model.predict(trainX)
        testPredict = model.predict(testX)
         
        #print ("Training", trainPredict)
        #print ("Testing ",testPredict)
            
        #print ("************************RESEULT********************")
        #print (type(trainPredict))
        #print(label_encoder.inverse_transform(argmax(trainPredict[0,:])))
        #print(label_encoder.inverse_transform(argmax(testPredict[0,:])))
        
        predicted_sensor_id =  label_encoder.inverse_transform(argmax(testPredict[0,:]))
        dic_result["predicted_"+activity_type] = predicted_sensor_id
        json.dumps(dic_result, ensure_ascii=False)
    except Exception as e:
        print (e)
    return dic_result
    

 



################# Prediction section for all activities based on sensor's ID #####################
    #This function receive the dataset for training purpose
def get_dataset(data_df,activity_type):
    new_data = []
    for row in data_df.itertuples():
        previous_data = ""
        if(row.mvt != "" and activity_type == 'mvt'):
            new_data.append(int(row.mvt))
        elif(row.place != "" and activity_type == 'place'):
            new_data.append(int(row.place))
    return new_data
    
    
    
# convert an array of values into a dataset matrix
def create_dataset(dataset, look_back=1):
    dataX, dataY = [], []
    for i in range(len(dataset)-look_back-1):
        a = dataset[i:(i+look_back)]
        dataX.append(a)
        dataY.append(dataset[i + look_back])
    return numpy.array(dataX), numpy.array(dataY)
    
    
#Model Learning with LSTM
# This model predict the future activity based on the previous activities
def sensor_id_activity_prediction(data_df,activity_type):
    dic_result = {}
    new_data = get_dataset(data_df,activity_type) 
    #data_df.columns.values.tolist()
    dataset = data_df.place.values
    dataset = dataset.astype('float32')
    dataset =dataset.reshape(-1,1)
    # normalize the dataset
    scaler = MinMaxScaler(feature_range=(0, 1))
    dataset = scaler.fit_transform(dataset)
    # split into train and test sets
    train_size = int(len(dataset) * 0.67)
    test_size = len(dataset) - train_size
    
    train = dataset[0:train_size] 
    test = dataset[test_size:len(dataset)]
        
    # reshape into X=t and Y=t+1
    look_back = 1
    trainX, trainY = create_dataset(train, look_back)
    testX, testY = create_dataset(test, look_back)
    # reshape input to be [samples, time steps, features]
    trainX = numpy.reshape(trainX, (trainX.shape[0], 1, trainX.shape[1]))
    testX = numpy.reshape(testX, (testX.shape[0], 1, testX.shape[1]))
   
    
    values = array(new_data)
    
    # integer encode
    label_encoder = LabelEncoder()
    integer_encoded = label_encoder.fit_transform(values)
    
    # binary encode
    onehot_encoder = OneHotEncoder(sparse=False)
    integer_encoded = integer_encoded.reshape(len(integer_encoded), 1)
    onehot_encoded = onehot_encoder.fit_transform(integer_encoded)
    
    # invert first example
    inverted = label_encoder.inverse_transform([argmax(onehot_encoded[0, :])])
    
      
    model = Sequential()
    model.add(LSTM(4, input_shape=(1, look_back))) #, activation="sigmoid"
    model.add(Dense(1))
    model.compile(loss='mse', optimizer='adam', metrics=["accuracy"])
    model.fit(trainX, trainY, epochs=10, batch_size=2, verbose=2)
    # make predictions
    trainPredict = model.predict(trainX)
    testPredict = model.predict(testX)
         
    #print ("Training", trainPredict)
    #print ("Testing ",testPredict)
        
    #print ("************************RESEULT********************")
    #print (type(trainPredict))
    #print(label_encoder.inverse_transform(argmax(trainPredict[0,:])))
    #print(label_encoder.inverse_transform(argmax(testPredict[0,:])))
        
    predicted_sensor_id =  label_encoder.inverse_transform(argmax(testPredict[0,:]))
    dic_result["predicted_"+activity_type+"_sensor_id"] = predicted_sensor_id
    json.dumps(dic_result, ensure_ascii=False)
    return dic_result


    
#anomaly detection in the  pattern
# Receive a set of training dataset as adl_dataset
# Receive a set of testing anomaly dataset
# Return 0.0 if anomally is not detected and "anomaly" if an anomaly is detected
def is_anomaly(adl_dataset,adl_data_test):
    # At train time lsanomaly calculates parameters rho and sigma
    lsanomaly = LSAnomaly(sigma=3, rho=0.1)

    res = np.reshape((adl_dataset),(-1, 1))
    
    lsanomaly.fit(res)
        
    res_test = np.reshape((adl_data_test),(-1, 1))
    predit_res = lsanomaly.predict(res_test)
    return predit_res ,lsanomaly.predict_proba(res_test) # predicted result and probability of the result
    
    
    #adl_data_train = [9,6,5,4,6,5,4,6,5,4,3,20,50]
    #adl_data_test = [10]
    #is_anomaly(adl_data_train,adl_data_test)          
    
