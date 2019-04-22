# -*- coding: utf-8 -*-
"""
Created on Sun Jan 28 10:52:37 2018

@author: Rohit Ranjan
This is a framework basically returns the Activity of Daily Living for all the specified high level activities e.g movement or place
If movement is selected, it returns all the activities related to movement for each of the specified sensors ID
"""

import matplotlib.pyplot as plt
import pandas as pd
import datetime
from scipy import stats
#import urllib.request as urllib2
import json
import math
from datetime import timedelta,date, time
import time
from pytz import timezone
import os, os.path

try:
    import urllib.request as urllib2
except ImportError:
    import urllib2


#Convert date time to epoach time
def convert_date_time_to_epoach(date_para):
    date_format='%Y-%m-%d %H:%M:%S'
    epoach = time.mktime(time.strptime(date_para, date_format))
    return epoach 
    
    # This convert timezone from one to another and return the time zone difference
def get_dynamic_timezone_difference(time_zone_from, time_zone_to,key,date1):
    try:
        status = False
        #'http://api.timezonedb.com/v2/convert-time-zone?key=T5EIC058WQ3L&format=json&from=Africa/Accra&to=America/Vancouver&time=1511146800'
        time_offset = ""
        epoch_time  =   str( convert_date_time_to_epoach(date1))
        new_epoach_time = epoch_time.split(".")
        url = "http://api.timezonedb.com/v2/convert-time-zone?key=" + key + "&format=json&from=" + time_zone_from + "&to="+ time_zone_to +"&time="+ new_epoach_time[0]
        
        f = urllib2.urlopen(url)
        json_string = f.read()
        parsed_json = json.loads(json_string)
        status = parsed_json['status']
        if(status == "OK"):
            
            time_offset = (abs( parsed_json['offset'] ))/3600 # get the offset and make it positive
            
            status =True
        else:
            
            status = False
    except Exception as e:
        print ("Get Time Zone Fail"+ e)
    return time_offset,status

    #This method transform the time into a desire timezone
def time_rearrangement(data,time_zone_from, time_zone_to, key, local_tz,time_zone_offset):
    date_format='%Y-%m-%d %H:%M:%S'
    time_zone_offset_list = [] 
    date_list = []
    new_time_value = ""
     #The first loop is just to get one record and use it to get the timezone differences
    for sample in range(1):
        value =  pd.to_datetime(data.ts[sample])
        new_time_value =  value.strftime('%Y-%m-%d %H:%M:%S') #COnvert Timestamp to string
        time_zone_offset_list.append(time_zone_offset)
    for i in data.ts:
        i = pd.to_datetime(i)
        date_zone = local_tz.localize(i.to_pydatetime())
        date_zone = date_zone.replace(tzinfo=local_tz)
        new_date = i.to_pydatetime() - timedelta(hours=time_zone_offset) # Standard 8 hours lag time
        new_date_str = new_date.strftime(date_format)
        remove_zeros = new_date_str.split(".")
        date_list.append(remove_zeros[0])
    return date_list # This is the list of all the converted date



#extract a specific activity dataset
def get_specific_activity_data(data_df,activity_id, activity_type):
    
    if(len(data_df) != 0 and activity_id != 0 and activity_type != ''): #valdating
        activity_df = data_df.where(( data_df[activity_type] == int(activity_id))) # be in bedroom
        data_df.to_csv('activity_selected_by_date.csv') # Write the selected activity to csv
        activity_df.to_csv('activity_selected_by_activity_id.csv') # Write the selected activity to csv
        activity_df_new = activity_df.dropna()
    return activity_df_new


# Function to get the current date 
def get_todays_date():
    t = datetime.date.today()
    return t.strftime('%Y-%m-%d')


#function to retun the dataset of the current date
def get_dataset_based_on_date(todays_date,from_tz,to_tz,api_key,local_tz,time_zone_offset):
    todays_dataset = pd.DataFrame() #creates a new dataframe that's empty
    try:
        
        filename = 'user_mvts_dataset_for_analysis.csv'
        PATH = os.getcwd()+"/"+filename
        filepath = PATH 
        dataset = pd.read_csv(filepath, header = 0, sep = ',')
        split1 = dataset.ts.str.split("+").str.get(0) # split and remove the +0000 in the datetime string
        dataset.ts = split1
        dataset.ts  = pd.DataFrame(time_rearrangement (dataset,from_tz,to_tz,api_key,local_tz,time_zone_offset)) # correct timezone converter
        
        #process time to date time format
        dataset.ts = pd.to_datetime(dataset.ts)# convert from string to datetime
        dataset.index = dataset.ts # turn ts  column into index
        todays_dataset = dataset[todays_date]
        
    except Exception as e:
        print ("There is error with get_dataset_based_on_date function with message ", e)
    return todays_dataset



#this function is to classify activities
#This function return the json object of an activity based on it id
def get_activity_classification_mvt(activity_id, result, activity_counter):
    try:
        dic_activity = {} # This is to dictionary to store activity data
        return_result = ""
        if(activity_id == 1): # This shows inbed activity
            dic_activity["daily_in_bed_activity_in_minute"] = result
            dic_activity["daily_in_bed_activity_counter"] = activity_counter #How many times does it goes to bed daily
            return_result = json.dumps(dic_activity, ensure_ascii=False)
        elif(activity_id == 2): # This shows off bed activities
            dic_activity["daily_off_bed_activity_in_minute"] = result
            return_result = json.dumps(dic_activity, ensure_ascii=False)
        elif(activity_id == 4): # This shows off bed activities
            dic_activity["daily_washroom_activity_in_minute"] = result
            dic_activity["daily_washroom_activity_counter"] = activity_counter #How many times does it goes to wash room daily
            return_result = json.dumps(dic_activity, ensure_ascii=False)
        elif(activity_id == 5): # This shows off open door activities
            dic_activity["daily_open_activity_in_minute"] = result
            dic_activity["daily_open_activity_counter"] = activity_counter 
            return_result = json.dumps(dic_activity, ensure_ascii=False)
        elif(activity_id == 6): # This shows off Close activities
            dic_activity["daily_close_activity_in_minute"] = result
            dic_activity["daily_close_activity_counter"] = activity_counter #
            return_result = json.dumps(dic_activity, ensure_ascii=False)
        elif(activity_id == 18): 
            dic_activity["daily_change_activity_in_minute"] = result
            dic_activity["daily_change_activity_counter"] = activity_counter 
            return_result = json.dumps(dic_activity, ensure_ascii=False)
        elif(activity_id == 19): 
            dic_activity["daily_leave_home_activity_in_minute"] = result
            dic_activity["daily_leave_home_activity_counter"] = activity_counter 
            return_result = json.dumps(dic_activity, ensure_ascii=False)
        elif(activity_id == 20): 
            dic_activity["daily_back_home_activity_in_minute"] = result
            dic_activity["daily_back_home_activity_counter"] = activity_counter 
            return_result = json.dumps(dic_activity, ensure_ascii=False)
        elif(activity_id == 21): 
            dic_activity["daily_take_shower_activity_in_minute"] = result
            dic_activity["daily_take_shower_activity_counter"] = activity_counter 
            return_result = json.dumps(dic_activity, ensure_ascii=False)
        elif(activity_id == 22): 
            dic_activity["daily_take_shower_end_activity_in_minute"] = result
            dic_activity["daily_take_shower_end_activity_counter"] = activity_counter 
            return_result = json.dumps(dic_activity, ensure_ascii=False)
    except  Exception as e:
        print (e)
    return return_result




def get_activity_classification_place(activity_id, result, activity_counter):
    try:
        dic_activity = {} # This is to dictionary to store activity data
        return_result = ""
        if(activity_id == 4): # This shows inbed activity
            dic_activity["daily_in_bathroom_activity_in_minute"] = result
            dic_activity["daily_in_bathroom_activity_counter"] = activity_counter #How many times does it goes to the bedroom daily
            return_result = json.dumps(dic_activity, ensure_ascii=False)
        elif(activity_id == 5): # This shows off bed activities
            dic_activity["daily_in_bedroom_activity_in_minute"] = result
            dic_activity["daily_in_bedroom_activity_counter"] = activity_counter
            return_result = json.dumps(dic_activity, ensure_ascii=False)
    except Exception as e:
        print (e)
    return return_result





#This function return daily number of minute of an activity based on the fuction paramenter
def get_daily_in_total_minute(dataset,current_date, activity_id, activity_type):
    try:
        return_result = ""
        if(dataset.shape[0] != 0): # test is the dataset is empty
            
            #Get specific activity dataset
            activity_dataset = get_specific_activity_data(dataset, activity_id,activity_type)
            dataset_time_diff = activity_dataset.index.to_series().diff() # get the time differences from the timestamp
            result = abs((dataset_time_diff.dt.total_seconds().sum())/60.0) # Total time in Minute
            
            #activity classification
            if(activity_type == 'mvt'):
                return_result = get_activity_classification_mvt(activity_id, result, len(activity_dataset.index)) # This return the json object based on the activity id
            elif(activity_type == 'place'):
                return_result = get_activity_classification_place(activity_id, result, len(activity_dataset.index)) # This return the json object based on the activity id
                
    except Exception as e:
        print (e)       
    return return_result
        


