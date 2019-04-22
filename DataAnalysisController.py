# -*- coding: utf-8 -*-
"""
Created on Sat Dec  9 08:46:43 2017


The aim of this file is to serves as a point where all the classes will be called and the integration interface to another system
"""
import GetMonitoredData as gmd  # Import the class to get all the data from the repository
import SleepingActivitiesDataExtraction as _sleeping_ade # Import all the function in SleepingActivitiesDataExtraction
import MovementActivitiesDataExtraction as made # Import all the functions in MovementActivitiesDataExtraction
import SleepingActivity as sa # Import all the function in SleepingActivity.py
import ADLMovementPlaceActivity as adl_mvt_place # function that retun ADL
import ADLSummary as adl_activity_summary # This function is majorly to retun the activity summary
import MLPredictionsModels as ml # Class where ML training & Testing is being done
import StatisticalModels as stat_model
from pytz import timezone
from datetime import datetime, timedelta,date, time
import time
import pandas as pd
import scipy.stats as ss
from flask import Flask
import theano
import tensorflow
import keras
import json
import datetime
import math
import sys


def get_dataset(house_id,start_time,end_time,table_name,db_name,tz_from,tz_to,tz_api_key,local_tz):
    
    #activate this when testing for production release
    get_monitored_data = gmd.GetMonitoredData(house_id,start_time,end_time,table_name,db_name,tz_from,tz_to,tz_api_key,timezone(local_tz))
    
    #Class initialization values
    gui_id = get_monitored_data.gw_euid
    db_name = get_monitored_data.db_name
    table_name = get_monitored_data.table_name
    start_datetime = get_monitored_data.start_time
    end_datetime = get_monitored_data.stop_time
    from_tz = get_monitored_data.from_tz
    to_tz = get_monitored_data.to_tz
    api_key = get_monitored_data.tz_account_api_key
    local_tz = get_monitored_data.local_tz
    
    # building SQL Query
    db_name = str(db_name)
    SQL_Query = "select * from "+ db_name + "."+ str(table_name) + " where gw_euid=" + "'"+ str(gui_id) + "'"+ " and ts<=%s and ts>=%s allow filtering" 
    #Get the data out of the database
    data_df = get_monitored_data.connect_to_db(db_name,SQL_Query,end_datetime,start_datetime)
    
    return data_df 



# THis function is basically to save us from typing all the parameters needed to access the dataset in our repository
#All parameter can be changes in get_dataset and we will just call get_dataset_quickly to get the data out
#This return the raw dataset
def get_dataset_quickly(gw_uid,start_date,end_date,table_to_select,database_to_use,from_tz,to_tz,api_key,local_tz):
    
    data_df = get_dataset(gw_uid,start_date,end_date,table_to_select,database_to_use,from_tz,to_tz,api_key,"US/Pacific")
    return data_df #This return the raw dataset
    

#get the sleeping pattern
def get_sleep_timing():
    return _sleeping_ade.Q1_Q2(get_dataset_quickly())
 
#get the sleepdurations and timing after predictions
def get_sleep_computation():
    inbed_df_new = _sleeping_ade.get_in_bed_data(get_dataset_quickly())
    offbed_df_new = _sleeping_ade.get_off_bed_data(get_dataset_quickly())
    sleepDurationParameters = _sleeping_ade.Q3(inbed_df_new,offbed_df_new) 
    sleepAggregation = _sleeping_ade.get_sleep_duration_aggregation(sleepDurationParameters)
    SD = _sleeping_ade.clean_sleep_duration(sleepAggregation)
    ST = _sleeping_ade.sleep_time_extraction(sleepDurationParameters)
    
    # return value are scale_comp_predict_duration, mode_res_duration,scale_comp_predict_timing, mode_res_timing 
    return _sleeping_ade.sleep_scale_computation(ST,SD,"") 

# This extract the date that an activity will be extracted for
def get_startdate_to_extract_activity(start_date):
    split_date = start_date.split(" ")
    return split_date[0]
    

# This extract the date that an activity will be extracted for
def get_enddate_to_extract_activity(end_date):
    split_date = end_date.split(" ")[0]
    return  int(split_date.split("-")[2])
    
#This return the list of mvt activity of concern
def get_list_of_mvt_activity():
    mvt_sensor_id = [1,2,5,6,18,19,20]
    return mvt_sensor_id
    

#This return the list of place activity of concern
def get_list_of_mvt_activity():
    place_sensor_id = [4,5,29,46]
    return mvt_sensor_id

#Get the next day date
def get_next_day_date():
    nextday_date =  datetime.date.today() + datetime.timedelta(days=1)
    formatted_result =  datetime.datetime.strftime(nextday_date,'%Y-%m-%d') 
    return formatted_result

#Get the next day from current date
#The current date parameter is a string
def get_next_day_date_based_on_current_date(current_date):
    split_date = current_date.split("-")
    
    new_date = split_date[0] + "-"+split_date[1]+ "-"+ str(int(split_date[2])+1)
    return new_date


#Get the Daily activity for movement and place
#current_date = adl_mvt_place.get_todays_date() # is working
#current_date = '2017-06-025' 
#activity_id = 1 # This is the sensor ID
#activity_type = 'mvt' # Activity Type can either be 'mvt' or 'place'
#This will get specific activity
def get_adl(current_date,activity_id,activity_type,from_tz,to_tz,api_key,local_tz):
    print("Data Extraction and Conversion to local Timezone")
    dataset =  adl_mvt_place.get_dataset_based_on_date(current_date,from_tz,to_tz,api_key,local_tz,time_zone_offset)
    print ("Daily Computation Based on Activity ID")
    daily_activity = adl_mvt_place.get_daily_in_total_minute(dataset,current_date, activity_id,activity_type) # This activity only receive movement sensor id
    print (daily_activity)
    



#This function will get the entire daily activity dataset
def get_adl_dataset(todays_date,from_tz,to_tz,api_key,local_tz):
    return adl_mvt_place.get_dataset_based_on_date(todays_date,from_tz,to_tz,api_key,local_tz,time_zone_offset)
    



#Testing ADL Computation
dic_activity = {}
gw_uid = "000D6F000C362FB5"
start_date ="2017-06-01 00:00:00.000+0000"
end_date = "2017-06-30 23:59:59.000+0000"
table_to_select = "user_mvts"
database_to_use = "recare_adl"
from_tz = "Africa/Accra"
to_tz = "America/Vancouver"
#api_key = "T5EIC058WQ3L"
api_key = "A4IZ8B4JOKAJ"
local_tz = timezone("US/Pacific")

time_zone_offset = 8



#assumptions
sleep_assumption_time_night = 20  #This is the assumed hour when the night time starts (Start Sleeping for the current day)
sleep_assumption_time_morning = 10  #This is the assumed hour when the morning time stop (Stop sleeping for the next day)
sleep_assumption_duration = 7  #This is not being used now but is the assumed sleeping duration
#daily activity parameter
current_date = '2017-06-25' 
nextday_date = '2017-06-26'
activity_id = 5 # This is the sensor ID
activity_type = 'mvt' # Activity Type can either be 'mvt' or 'place'

#fetch data from the database
fetch_data , status,dataset_size = get_dataset_quickly(gw_uid,start_date,end_date,table_to_select,database_to_use,from_tz,to_tz,api_key,local_tz)    # just to test




if(status == True):
    print("Connection to DB Successful with return dataset size of "+ str(dataset_size))
    
else:
    print ("Unsuccessful Connection Please Check your Connection Parameters")# We can write a script to send mail to the admin on this failure
    sys.exit()


print ("&&&&&&&&&&&&&&&&&&&& PROCESSING ADL ,TRAINING AND FITING LSTM &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")


#Testing the daily activity summary
adl_dataset = get_adl_dataset(current_date,from_tz,to_tz,api_key,local_tz) #dataset of today

adl_dataset_nextday = get_adl_dataset(nextday_date,from_tz,to_tz,api_key,local_tz) #dataset of nextday

print ("Next day:", get_next_day_date())


print ("*************************** *SLEEPING ACTIVITY SUMMARY ****************************************************")
print (adl_activity_summary.daily_sleeping_summary(adl_dataset,adl_dataset_nextday,sleep_assumption_time_night,sleep_assumption_duration,sleep_assumption_time_morning))
print("")






print ("*************************** *MOVEMENT ACTIVITY SUMMARY ****************************************************")
mvt_hourly = adl_activity_summary.hourly_daily_movement_activity(adl_dataset)
print(mvt_hourly)



################################## TESTING  ADL Using By Getting Several Daily Activity #########################
current_date = '2017-06'
activity_id = 5 # This is the sensor ID
activity_type = 'mvt' # Activity Type can either be 'mvt' or 'place'
adl_statistical_status = False # This is set to true if the new day adl fall within confidence interval
confidence_interval = 0.99
max_tolerance = 60 # This is in munite to show the maximum minute that can be tolorated before rejection



#******************************** TESTING SLEEPING PREDICTION BY COLLECTING SEVERAL DAILY ACTIVITY *******************************************
# Data Cleaning section
#This function returns the dataframe object of extracted daily activity
# activity_type is integer: 1 is sleep scale; 2 is living scale; 3 is kitchen scale
def get_dataframe_of_daily_activity(daily_activity_date,daily_activity_list,activity_type):
    # convert the arrays to panda dataframe object
    if(activity_type == 1): # sleeping scale
        df_sleep_duration = pd.DataFrame({'sleep_duration':daily_activity_list})
        df_sleep_date =  pd.DataFrame({'date':daily_activity_date})
        df_new = pd.concat([df_sleep_date,df_sleep_duration], axis=1)
    elif(activity_type == 2): # living room scale conversion
        df_living_duration = pd.DataFrame({'daily_living_room_mvt':daily_activity_list})
        df_living_date =  pd.DataFrame({'date':daily_activity_date})
        df_new = pd.concat([df_living_date,df_living_duration], axis=1)
    elif(activity_type == 3): # Kitchen room scale conversion
        df_kitchen_duration = pd.DataFrame({'daily_kitchen_mvt':daily_activity_list})
        df_kitchen_date =  pd.DataFrame({'date':daily_activity_date})
        df_new = pd.concat([df_kitchen_date,df_kitchen_duration], axis=1)
    
    return df_new
    

# Computation base on sleeping ADL    
def sleep_scale(current_date,from_tz,to_tz,api_key,local_tz):
    
    temp_daily_sleep_duration_list = [] # Temporarily stores the daily sleep duration 
    daily_sleep_duration_list = [] # This store the daily sleep duration
    daily_date = [] # This stores the daily date
    for i in range(1,28):
        current_date_new = current_date + "-"+str(i) # Get the current date
        next_date = get_next_day_date_based_on_current_date(current_date_new) # get the next day from the current date
        
        adl_dataset = get_adl_dataset(current_date_new,from_tz,to_tz,api_key,local_tz) #dataset for current date
        adl_dataset_nextday = get_adl_dataset(next_date,from_tz,to_tz,api_key,local_tz) #dataset of nextday
        result = adl_activity_summary.only_daily_sleeping_activity (adl_dataset,adl_dataset_nextday,sleep_assumption_time_night,sleep_assumption_duration,sleep_assumption_time_morning)
        
        daily_result = json.loads(result) # Load the json returned records
        appended_result_sleep_duration =  str(math.ceil(daily_result["sleeping-duration-at-night"]))
        
        daily_sleep_duration_list.append(appended_result_sleep_duration) 
        daily_date.append(current_date_new)
        
        print (result)
    #temp_daily_sleep_duration_list = daily_sleep_duration_list     
    
    
    # ML Prediction Section
    new_df = get_dataframe_of_daily_activity(daily_date,daily_sleep_duration_list,1) # Cleaned Dataframe object for the sleep activity
    print("------- ADL DATAFRAME ------ ")
    print (new_df)
    print ("-----Training  LSTM for Sensor ID Prediction")
    print (ml.sensor_id_activity_prediction(fetch_data,activity_type))
    
    print ("-----Training LSTM for ADL Prediction")
    print (ml.each_adl_activity_prediction(new_df,"sleep_duration")) # This is for sleep duration prediction
    
    
    
    #  Anomally Detection
    adl_data_future = daily_sleep_duration_list[len(daily_sleep_duration_list)-1] # get the last item in the list . THis was not used to train
    
    daily_sleep_duration_list.pop(len(daily_sleep_duration_list)-1) #pop out last element
    adl_data_train = daily_sleep_duration_list
    print(adl_data_train)
    #adl_data_future = daily_sleep_duration_list[len(daily_sleep_duration_list)-1] # get the last item in the list . THis was not used to train
    
    predicted_result, predicted_prob_result = ml.is_anomaly(adl_data_train,adl_data_future) 
    
    print("Anomaly Predicted Result is->", predicted_result)   # the output is 0.0 if the new Data is normal otherwise it returns "anomally"      
    print ("Anomaly Predicted Probability Result ->", predicted_prob_result[0][0])
    
    
    #Statistical Evaluations
    adl_mean,adl_lowerbound,adl_upperbound = stat_model.adl_mean_confidence_interval_via_api(adl_data_train, confidence_interval)
    print ("Mean Value ->",adl_mean,"Lower Bound ->",adl_lowerbound,"Upper Bound ->",adl_upperbound)

    return adl_mean,adl_lowerbound,adl_upperbound ,adl_data_future


#  hourly_daily_movement_activity
# This is to measure ambulating - living room movement, kitchen movement
def ambulating_scale(current_date,from_tz,to_tz,api_key,local_tz):
    
    daily_living_ambulating_duration_list = [] # Temporarily stores the daily living room ambulating duration 
    daily_kitchen_ambulating_duration_list = [] # Temporarily stores the daily kitchen room ambulating duration 
    
    daily_date = [] # This stores the daily living room date
    for i in range(1,10):
        current_date_new = current_date + "-"+str(i) # Get the current date
        #next_date = get_next_day_date_based_on_current_date(current_date_new) # get the next day from the current date
        
        adl_dataset = get_adl_dataset(current_date_new,from_tz,to_tz,api_key,local_tz) #dataset for current date
        #adl_dataset_nextday = get_adl_dataset(next_date,from_tz,to_tz,api_key,local_tz) #dataset of nextday
        result = adl_activity_summary.hourly_daily_movement_activity(adl_dataset)
        
        daily_result = json.loads(result) # Load the json returned records
        appended_result_living_ambulating_duration =  str(math.ceil(daily_result["living-room-movement-counter"]))
        appended_result_kitchen_ambulating_duration = str(math.ceil(daily_result["kitchen-movement-counter"]))
        
        daily_living_ambulating_duration_list.append(appended_result_living_ambulating_duration) 
        daily_kitchen_ambulating_duration_list.append(appended_result_kitchen_ambulating_duration) 
        
        daily_date.append(current_date_new)
        
        print ("Daily Living Room",appended_result_living_ambulating_duration)
        print ("Daily Kitchen",appended_result_kitchen_ambulating_duration)
    new_living_df = get_dataframe_of_daily_activity(daily_date,daily_living_ambulating_duration_list,2) # Cleaned Dataframe object for the living room activity
        
    new_kitchen_df = get_dataframe_of_daily_activity(daily_date,daily_kitchen_ambulating_duration_list,3) # Cleaned Dataframe object for the kitchen activity
    
    
    print ("-----Training LSTM for ADL Prediction for living room movement")
    print (ml.each_adl_activity_prediction(new_living_df,"living_room")) # This is for living room daily prediction
    
    print ("-----Training LSTM for ADL Prediction for Kitchen movement")
    print (ml.each_adl_activity_prediction(new_kitchen_df,"kitchen")) # This is for kitchen daily prediction
   
    
    return new_living_df, new_kitchen_df
    


#----------- DECISION SUPPORT LAYER ------------------------------
adl_mean,adl_lowerbound,adl_upperbound ,adl_data_future = sleep_scale(current_date,from_tz,to_tz,api_key,local_tz) # sleep scale
print("Future activity is :",adl_data_future)
if (adl_lowerbound <= float(adl_data_future) <= adl_upperbound):
    print("Future Daily Activity ->", adl_data_future)
    adl_statistical_status = True
else:
    #subtract the future value from the lower or the upper bound to see the difference if it within the threshold
    if(float(adl_data_future) < adl_lowerbound):
        tolerance_error = adl_lowerbound - float(adl_data_future)
        if(tolerance_error > max_tolerance):
            adl_statistical_status = False
        else:
            adl_statistical_status = True
    elif(float(adl_data_future) > adl_upperbound):
        tolerance_error = adl_upperbound - float(adl_data_future)
        if(tolerance_error >= max_tolerance):
            adl_statistical_status = False
        else:
            adl_statistical_status = True

print ("Acceptance Status of New ADL",adl_statistical_status)


print("----------Movement ADL Computation -----------")
new_living,new_kitchen = ambulating_scale(current_date,from_tz,to_tz,api_key,local_tz) # Living Room

print (new_living)
print (new_kitchen)







