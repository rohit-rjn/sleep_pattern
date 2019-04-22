# -*- coding: utf-8 -*-
"""
Created on Fri Feb  9 04:39:16 2018
This file currently consist of two classes: 
GetSleepActivitySummary class: All activities concerning sleep are being carried out here
GetMovementActivitySummary class: All Activities concerning movement are being carried out here

"""
import numpy as np
import pandas as pd
#Statistical Packakes
from scipy import stats
import statsmodels as stats_model
import math
import json
#This class is to get the all the activities related to sleep
class GetSleepActivitySummary:
    
    def __init__(self,sleep_assumption_time_night,sleep_assumption_duration,sleep_assumption_time_morning):
        self.sleep_assumption_time_night = sleep_assumption_time_night #This is the sleep assumption start time. Hour is in 24 hours format  : e.g  20  means 8:00 PM
        self.sleep_assumption_duration = sleep_assumption_duration # This is the duration of sleep e.g 7
        self.sleep_assumption_time_morning = sleep_assumption_time_morning #This is the sleep assumption Stop time Next Day. Hour is in 24 hours format  : e.g  10:00AM
        
        
    
    #This return true if the hour component of a date value is more that the sleep_assumption_time
    #date_time = date value
    #assumption_time =  sleep_assumption_time
    def get_hour_component_of_date(self,date_time,assumption_time ):
        status = False
        #get the hour component
        date_and_time = str(date_time).split(" ")
        date_comp = date_and_time[1]
        hour_min_sec = str(date_comp).split(":")
        hours = int(hour_min_sec[0])
        if(hours >= assumption_time):
            status = True
        return status
    
    
    #This return true if the hour component of a date value is more that the sleep_assumption_time_next
    #date_time = date value
    #assumption_time =  sleep_assumption_time for the morning time
    def get_hour_component_of_date_morning(self,date_time,assumption_time_next ):
        try:
            #print ("Date & Assumption", date_time,assumption_time_next)
            status = False
            #get the hour component
            date_and_time = str(date_time).split(" ")
            date_comp = date_and_time[1]
            hour_min_sec = str(date_comp).split(":")
            hours = int(hour_min_sec[0])
            if(hours <= assumption_time_next):
                status = True
        except Exception as e:
            print(e)
        return status    
    
    
    
    
    #return a json representation of an activity
    def get_json_value(name,value):
        dic_activity = {} # This is to dictionary to store activity data
        return_result = ""
        dic_activity[name] = value
        return_result = json.dumps(dic_activity, ensure_ascii=False)

    #How much time the person sleeps at night( night time period will be a variable assumptions)
    def get_night_sleep_time(self,dataset):
        try:
            #print ("Current Day",len(dataset.index))
            list_of_time_inbed = [] # This stores the list of Time in bed for the night
            cnt = 0
            time_previous_inbed = ''
            night_sleep = []
            cnt_wake = 0 # Counter to track the number of time the person wakes up inbetween sleep
            time_differences = 0.0
            for row in dataset.itertuples():   
                
                status = self.get_hour_component_of_date(row.ts,self.sleep_assumption_time_night) #
                if(row.mvt == 1 and status == True ): # This shows that the person is inbed by the assumed time
                    cnt = cnt +1
                    time_previous_inbed = row.ts  
                    list_of_time_inbed.append(row.ts)
                elif(row.mvt == 2 and status == True):
                    cnt_wake += 1
                    if(time_previous_inbed != ""):
                        night_sleep.append(row.ts)                     
                        time_differences += (pd.to_datetime(row.ts) - pd.to_datetime(time_previous_inbed)).seconds /60.0  # The sleep duration
                        
                    else:
                        time_previous_inbed = row.ts 
                       
        except Exception as e:
            print (e)
        
        return time_differences,cnt_wake,list_of_time_inbed
        
        
        
    #How much time the person sleeps at Morning time ( Morning time period will be a variable assumptions)
    # The dataset here is the next day dataset
    def get_morning_sleep_time(self,dataset_nextday):
        try:
            list_of_time_offbed = [] # This stores the list of time the person is off bed for the morning
            cnt = 0
            time_previous_inbed = ''
            morning_sleep = []
            cnt_wake = 0 # Counter to track the number of time the person wakes up inbetween sleep
            time_differences = 0.0
            for row in dataset_nextday.itertuples():   
                
                status = self.get_hour_component_of_date_morning(row.ts,self.sleep_assumption_time_morning) #
                if(row.mvt == 1 and status == True ): # This shows that the person is inbed by the assumed time
                    cnt = cnt +1
                    time_previous_inbed = row.ts 
                    
                elif(row.mvt == 2 and status == True):
                    list_of_time_offbed.append(row.ts)
                    cnt_wake += 1
                    if(time_previous_inbed != ""):
                        morning_sleep.append(row.ts)                     
                        time_differences += (pd.to_datetime(row.ts) - pd.to_datetime(time_previous_inbed)).seconds /60.0  # The sleep duration
                        
                    else:
                        time_previous_inbed = row.ts 
                       
        except Exception as e:
            print ("Error with Function get_morning_sleep_time",e)
        
        return time_differences,cnt_wake, list_of_time_offbed       
        
        
    #This fuction collect the list of time in bed for the current day and the list of time off bed for the next day
    # It find the time difference between the very first time in bed on the current day and the next time off bed on the next day
    def get_sleeping_parameter(self,list_of_time_inbed,list_of_time_offbed):
        try:
            time_difference = 0.0
            x1 = ''
            yn = ''
            if(len(list_of_time_inbed) != 0 and len(list_of_time_offbed) != 0):
                x1 = str(list_of_time_inbed[0]) # First date in the list
                yn =  str(list_of_time_offbed[(len(list_of_time_offbed)-1)]) #Last date in the list
                time_difference =(pd.to_datetime(yn) - pd.to_datetime(x1)).seconds /60.0 
            else:
                time_difference = 0.0 # This retun 0.0 when the list are empty
        except Exception as e:
            print (e)
        return time_difference, x1, yn
        
        
    
    
    
            
#This class is to get the all the activities related to Movement      
class GetMovementActivitySummary:
    
    def __init__(self,label=None):
        self.label = label
        
    #get the hour of a particular day
    def get_hour_component_of_date(self,date_time):
        
        #get the hour component
        date_and_time = str(date_time).split(" ")
        date_comp = date_and_time[1]
        hour_min_sec = str(date_comp).split(":")
        hours = int(hour_min_sec[0])
        return hours
        

    
    
    #Hourly Movevement in Living Room
    #THis return the total number of movement made in the living room every hour and the total number of movement for this activity in a day
    def hourly_living_movement_activity_summary(self,dataset):
        hour = 0
        hour_mvt_counter = 0# This store the number of movement within an hour
        mvt_counter_list = [] #This stores list of movement for the entire dataset but this is temporary, used for computation
        
        final_mvt_counter_list = [] #This is the final list where the counter for each hourly movement is being stored
        cnt = 0
        for row in dataset.itertuples(): 
            
            if(row.place == 46): # This shows Livingroom activity
                hour = int(self.get_hour_component_of_date(row.ts))
                mvt_counter_list.append(hour)                
                
        for i in range(len(mvt_counter_list)):
            if(cnt > 0):
                if(int(mvt_counter_list[i]) == int(mvt_counter_list[i-1])):
                    hour_mvt_counter = hour_mvt_counter+1
                else:
                    #This append the sensor id AND THE NUMBER OF MOVEMENT BASED ON THAT SENSOR ID (sensor id-number of movement)
                    final_mvt_counter_list.append(str(mvt_counter_list[i-1]) + "-"+str(hour_mvt_counter+1))
                    hour_mvt_counter = 0
                    
            else:
                cnt = cnt+1
             
        return final_mvt_counter_list, len(mvt_counter_list)
        
        
        
        
    #Hourly Movevement in The Kitchen
    #THis return the total number of movement made in the Kitchen every hour and the total number of movement for this activity in a day
    def hourly_kitchen_movement_activity_summary(self,dataset):
        hour = 0
        hour_mvt_counter = 0# This store the number of movement within an hour
        mvt_counter_list = [] #This stores list of movement for the entire dataset but this is temporary, used for computation
        
        final_mvt_counter_list = [] #This is the final list where the counter for each hourly movement is being stored
        cnt = 0
        for row in dataset.itertuples(): 
            
            if(row.place == 29): # This shows Livingroom activity
                hour = int(self.get_hour_component_of_date(row.ts))
                mvt_counter_list.append(hour)                
                
        for i in range(len(mvt_counter_list)):
            if(cnt > 0):
                if(int(mvt_counter_list[i]) == int(mvt_counter_list[i-1])):
                    hour_mvt_counter = hour_mvt_counter+1
                else:
                    #This append the sensor id AND THE NUMBER OF MOVEMENT BASED ON THAT SENSOR ID (sensor id-number of movement)
                    final_mvt_counter_list.append(str(mvt_counter_list[i-1]) + "-"+str(hour_mvt_counter+1))
                    hour_mvt_counter = 0
                    
            else:
                cnt = cnt+1
        return final_mvt_counter_list, len(mvt_counter_list)
        
        
        
    #Hourly Movevement in The Bedroom
    #THis return the total number of movement made in the Bedroom every hour and the total number of movement for this activity in a day
    def hourly_bedroom_movement_activity_summary(self,dataset):
        #print(dataset)
        hour = 0
        hour_mvt_counter = 0# This store the number of movement within an hour
        mvt_counter_list = [] #This stores list of movement for the entire dataset but this is temporary, used for computation
        
        final_mvt_counter_list = [] #This is the final list where the counter for each hourly movement is being stored
        cnt = 0
        for row in dataset.itertuples(): 
            
            if(row.place == 5): # This shows Livingroom activity
                hour = int(self.get_hour_component_of_date(row.ts))
                mvt_counter_list.append(hour)                
                
        for i in range(len(mvt_counter_list)):
            if(cnt > 0):
                if(int(mvt_counter_list[i]) == int(mvt_counter_list[i-1])):
                    hour_mvt_counter = hour_mvt_counter+1
                else:
                    #This append the sensor id AND THE NUMBER OF MOVEMENT BASED ON THAT SENSOR ID (sensor id-number of movement)
                    final_mvt_counter_list.append(str(mvt_counter_list[i-1]) + "-"+str(hour_mvt_counter+1))
                    hour_mvt_counter = 0
                    
            else:
                cnt = cnt+1
             
        return final_mvt_counter_list, len(mvt_counter_list)
    
   
    #THis return the total number of the person goes out on the out with place and movement
    # Also, Duration Outside of Home
    def outside_movement_place_activity_summary(self,dataset):
        mvt_counter_list = [] #This stores list of movement for the entire dataset  for outside activity
        place_counter_list = [] #This stores list of place for the entire dataset  for outside activity
       
        
        time_differences_outside_place = 0.0
        time_differences_outside_place_tmp  =''
        
        time_differences_outside_mvt = 0.0
        time_differences_outside_mvt_tmp = ''
        for row in dataset.itertuples(): 
            
            if(row.place == 37 ): # This shows Outside activity based on place
                place_counter_list.append(row.place)
                if(time_differences_outside_place_tmp != ""):
                    time_differences_outside_place += (pd.to_datetime(row.ts) - pd.to_datetime(time_differences_outside_place_tmp)).seconds /60.0  # The duration outside
                time_differences_outside_place_tmp = row.ts
            elif(row.mvt == 19): # This shows Outside activity based on movement
                mvt_counter_list.append(row.mvt)
                if(time_differences_outside_mvt_tmp != ""):
                    time_differences_outside_mvt += (pd.to_datetime(row.ts) - pd.to_datetime(time_differences_outside_mvt_tmp)).seconds /60.0  # The duration outside
                time_differences_outside_mvt_tmp = row.ts
        return len(place_counter_list), len(mvt_counter_list), time_differences_outside_place
    


#Class Activities for Sleeping
def daily_sleeping_summary(dataset,dataset_next,sleep_assumption_time_night,sleep_assumption_duration,sleep_assumption_time_morning):
    sleep_class = GetSleepActivitySummary(sleep_assumption_time_night,sleep_assumption_duration,sleep_assumption_time_morning)#Initiate the Sleep Activity Summary Class
    dic_activity = {} # This is to dictionary to store activity data
    return_result = ""
    #How much time the person sleeps at night( night time period will be a variable assumptions)
    night_sleep_duration,wakeup_between_sleep_night,list_of_time_inbed = sleep_class.get_night_sleep_time(dataset) #Night time spleep result
    morning_sleep_duration,wakeup_between_sleep_morning,list_of_time_offbed = sleep_class.get_morning_sleep_time(dataset_next) # Morning time sleep result
    
    print (list_of_time_inbed+list_of_time_offbed)
    print ("")
    transition_time,x1,yn = sleep_class.get_sleeping_parameter(list_of_time_inbed,list_of_time_offbed)   
    print ("Transition List",transition_time,x1,yn)
    print("")
    
    
    dic_activity["sleeping-duration-at-night"] = transition_time # Question 1
    
    #What time he/she went to bed.
    dic_activity["time-went-to-bed"] = x1 # Question 2
    
    # What time he/she wakes up
    dic_activity["wake-up-time"] = yn #Question 3
    
    #How many time he woke up in-between sleep
    dic_activity["wakeup-inbetween-sleep-counter"] = wakeup_between_sleep_night + wakeup_between_sleep_morning #Question 4
    
    return_result = json.dumps(dic_activity, ensure_ascii=False)
    return return_result



#Class Activities for Movement
def hourly_daily_movement_activity(dataset):
    movement_class = GetMovementActivitySummary()
    dic_activity = {} # This is to dictionary to store activity data
    return_result = ""
    
    # Number of hourly Movement in the Living room and the Total Number of movement made in Living Room
    living_room_hourly_movement,living_room_movement_counter = movement_class.hourly_living_movement_activity_summary(dataset)   
    dic_activity["living-room-hourly-movement"] = living_room_hourly_movement
    dic_activity["living-room-movement-counter"] = living_room_movement_counter

    # Number of hourly Movement in the Kithen and the Total Number of movement made in Kitchen
    kitchen_hourly_movement,kitchen_movement_counter = movement_class.hourly_kitchen_movement_activity_summary(dataset)  
    dic_activity["kitchen-hourly-movement"] = kitchen_hourly_movement
    dic_activity["kitchen-movement-counter"] = kitchen_movement_counter
    
    # Number of hourly Movement in the Bedroom and the Total Number of movement made in Bedroom    
    bedroom_hourly_movement,bedroom_movement_counter = movement_class.hourly_bedroom_movement_activity_summary(dataset)  
    dic_activity["bedroom-hourly-movement"] = bedroom_hourly_movement
    dic_activity["bedroom-movement-counter"] = bedroom_movement_counter
    
    
    # Number of time he goes out of the house in terms of place and movement sensors and the duration outside
    outside_place_movement,outside_mvt_movement ,duration_outside_home= movement_class.outside_movement_place_activity_summary(dataset)  
    dic_activity["outside-place-movement-counter"] = outside_place_movement
    dic_activity["outside-mvt-movement-counter"] = outside_mvt_movement
    dic_activity["duration-outside-home"] = duration_outside_home
    return_result = json.dumps(dic_activity, ensure_ascii=False)
    return return_result
    
    
    
# This is to get only the daily sleeping duration to be called for Machine Learning Predictions
def only_daily_sleeping_activity(dataset,dataset_next,sleep_assumption_time_night,sleep_assumption_duration,sleep_assumption_time_morning):
    
    sleep_class = GetSleepActivitySummary(sleep_assumption_time_night,sleep_assumption_duration,sleep_assumption_time_morning)#Initiate the Sleep Activity Summary Class
    dic_activity = {} # This is to dictionary to store activity data
    return_result = ""
    
    #How much time the person sleeps at night( night time period will be a variable assumptions)
    # ----------- Call the fuction for the comment above ------------
    night_sleep_duration,wakeup_between_sleep_night,list_of_time_inbed = sleep_class.get_night_sleep_time(dataset) #Night time spleep result
    morning_sleep_duration,wakeup_between_sleep_morning,list_of_time_offbed = sleep_class.get_morning_sleep_time(dataset_next) # Morning time sleep result
    
    transition_time,x1,yn = sleep_class.get_sleeping_parameter(list_of_time_inbed,list_of_time_offbed)   
    
    dic_activity["sleeping-duration-at-night"] = transition_time # Question 1
    return_result = json.dumps(dic_activity, ensure_ascii=False)
    return return_result


#This is to get only the movement daily movement a
def only_daily_Movement_activity():
    sleep_class = GetSleepActivitySummary(sleep_assumption_time_night,sleep_assumption_duration,sleep_assumption_time_morning)#Initiate the Sleep Activity Summary Class
    dic_activity = {} # This is to dictionary to store activity data
    return_result = ""
    
    #How much time the person sleeps at night( night time period will be a variable assumptions)
    # ----------- Call the fuction for the comment above ------------
    night_sleep_duration,wakeup_between_sleep_night,list_of_time_inbed = sleep_class.get_night_sleep_time(dataset) #Night time spleep result
    morning_sleep_duration,wakeup_between_sleep_morning,list_of_time_offbed = sleep_class.get_morning_sleep_time(dataset_next) # Morning time sleep result
    
    transition_time,x1,yn = sleep_class.get_sleeping_parameter(list_of_time_inbed,list_of_time_offbed)   
    
    dic_activity["sleeping-duration-at-night"] = transition_time # Question 1
    return_result = json.dumps(dic_activity, ensure_ascii=False)
    return return_result
