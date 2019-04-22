# -*- coding: utf-8 -*-
"""
Created on Sat Dec  9 09:05:14 2017

@author: Rohit

The aim of this class is to fetch the data from the database and convert each of the timezone to the location timezone
"""

from cassandra.cluster import Cluster
from datetime import datetime, timedelta,date, time
import time
from pytz import timezone
import urllib2

import pandas as pd
import os
import os.path


from flask import json


#Convert date time to epoach
def convert_date_time_to_epoach(date_para):
    date_format='%Y-%m-%d %H:%M:%S'
    epoach = time.mktime(time.strptime(date_para, date_format))
    return epoach # this return the epoach time
    
    # This convert timezone from one to another and return the time zone difference
def get_dynamic_timezone_difference(time_zone_from, time_zone_to,key,date1):
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
       
    return time_offset

    #This method transform the time into a desire timezone
def time_rearrangement(data,time_zone_from, time_zone_to, key, local_tz):
    date_format='%Y-%m-%d %H:%M:%S'
    time_zone_offset_list = [] 
    date_list = []
     #The first loop is just to get one record and use it to get the timezone differences
    for sample in range(1):
        print ("sample data",data.ts[sample], type(data.ts[sample]))
        value = (data.ts[sample].to_pydatetime())
        new_time_value = value.strftime('%Y-%m-%d %H:%M:%S') #COnvert Timestamp to string
        time_zone_offset = get_dynamic_timezone_difference(time_zone_from,time_zone_to,key,new_time_value)
        time_zone_offset_list.append(time_zone_offset)
    for i in data.ts:
        #Change the Datetime to PST
        date_zone = local_tz.localize(i.to_pydatetime())       
        date_zone = date_zone.replace(tzinfo=local_tz)  
        new_date = i.to_pydatetime() - timedelta(hours=time_zone_offset) # Standard 8 hours lag time
        new_date_str = new_date.strftime(date_format)
        remove_zeros = new_date_str.split(".")
        date_list.append(remove_zeros[0])
            
    return date_list

#method to buid a factory for panda
def pandas_factory(colnames, rows):
    return pd.DataFrame(rows, columns=colnames)


#This class is to get the data of the monitored person from any keyspace
class GetMonitoredData:
    
    
    def __init__(self, gw_euid,start_time,stop_time, table_name,db_name, from_tz, to_tz, tz_account_api_key,local_tz):
        self.gw_euid = gw_euid # house id
        self.start_time = start_time # Start time to select query
        self.stop_time = stop_time # Stop time to select query
        self.table_name = table_name # table to be selected from
        self.db_name = db_name # Database name to be selected from
        self.from_tz = from_tz # This is the initial dataset timezone
        self.to_tz = to_tz # This is the new dataset timezone
        self.tz_account_api_key = tz_account_api_key # This is the timezonedb api key for the account
        self.local_tz = local_tz # This is to use the local time zone of the house
        
    #sript to verify if csv file exist else, create it
    def verify_file_path(self):
        #generated_dataset/user_mvts_dataset_for_analysis.csv
        try:
            status = False
            filename = 'user_mvts_dataset_for_analysis.csv'
            PATH = os.getcwd()+"/"+filename
            if(os.path.exists('./'+filename) and os.access(PATH, os.R_OK) and os.access(PATH, os.W_OK)):
                status = True
            else:
                open(filename,"w+")
                if os.path.isfile(PATH) and os.access(PATH, os.R_OK):
                    status = True
        except Exception as e:
            print ("Error Processing Data File")
        return status, PATH
        
        
    
    def connect_to_db(self,keyspace_name,sql,EndTS,StartTS):
        try:
            status = False
            data_df = pd.DataFrame() #creates a new dataframe that's empty
            cluster = Cluster()
            session = cluster.connect()
            session.set_keyspace(keyspace_name)
            session.row_factory = pandas_factory #pd.DataFrame(rows, columns=colnames)
            session.default_fetch_size = 1000000000 #needed for large queries, otherwise driver will do pagination. Default is 50000.
            
            rows = session.execute(sql,[EndTS,StartTS])
            data_df = rows._current_rows
            data_df = data_df.sort_values(data_df.columns[2])
            path_status,file_path = self.verify_file_path()
            if(path_status == True):
                data_df.to_csv(file_path)
            else:
                print ("KEY FILE PATH NOT FOUND; PROGRAM MAY NOW WORK EFFECTIVELY")
            
            status  = True
        except Exception as e:
            print ("Error Connecting to Database",e)
                
        return data_df , status, len(data_df.index)

    
    


