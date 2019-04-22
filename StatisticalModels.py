# -*- coding: utf-8 -*-
"""
Created on Fri Mar  9 22:11:37 2018

@author: Rohit
This Module Comprises of statistical computations ADL results
"""


import numpy as np
import scipy as sp
import scipy.stats
from scipy import stats

#Calculating confidence interval using mathematical proof
def adl_mean_confidence_interval_via_compute(dataset, confidence_percent_value):
    new_dataset = list(map(float, dataset))
    a = 1.0*np.array(new_dataset)
    n = len(a)
    mean_value, std_value = np.mean(a), scipy.stats.sem(a)
    h = std_value * sp.stats.t._ppf((1+confidence_percent_value)/2., n-1)
    return mean_value, mean_value-h, mean_value+h  #mean, lower limit, upper limit
    
    
#Computing Confidence interval using function in scipy api
def adl_mean_confidence_interval_via_api(dataset,confidence_percent_value):
    new_dataset = list(map(float, dataset))
    mean, var, std = stats.bayes_mvs(new_dataset,alpha=confidence_percent_value)
    lower,upper = mean.minmax
    return mean.statistic, lower,upper #mean, lower limit, upper limit
    
