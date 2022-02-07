"""
Author:             Nathan Obert
Description:        This file contains functions used to join seperate .csv files with rainfall
                    gague data into a single file. In the .csv files, the timestamps are sometimes
                    missing or repeated. There is a function here that attempts to rectify that
                    with a basic algorithm; note that it's nowhere near perfect at fixing all
                    the issues. However, the vast majority of the data is valid after it
                    combs through and fixes some timestamps.
                    The data was originally sourced from Springfield's Rain Gague Network at
                    https://www.springfieldmo.gov/2153/Rain-Gauge-Network.
"""
import pandas as pd
import numpy as np
from copy import deepcopy
from spreadsheet_utility import *

def fixTimesRainfall(df):
    '''This function fixes issues with timestamps.
    The issue is that some hours will be of form: 10am, 12pm, 11am, etc, i.e. the hour is wrong.
    If the hour before and after are sequential, the middle value will be changed to match.
    To be used only by concatenateRainfallData.
    returns: pandas dataframe with DateTime column values changed
    '''
    #initial arrays to work from with formatted dates
    oldDateTimes = np.array(list(map(reformatDateTime, df["DateTime"])))
    newDateTimes = deepcopy(oldDateTimes)
    
    #comparing before and after hour to see if the middle matches
    #if no match, change
    for i in range(1, len(oldDateTimes) - 1):
        before = int(oldDateTimes[i - 1][10:13])
        after = int(oldDateTimes[i + 1][10:13])
        current = int(oldDateTimes[i][10:13])
        #if after is 00 or 01, make into 24 or 25 to be able to compare
        if after <= 1:
            after += 24
        #catching bad middle values
        if ( (current - 1 != before) or (current + 1 != after) ) and (after - before == 2):
            trueCurrent = (before + 1) % 24
            hour = str(trueCurrent) if len(str(trueCurrent)) == 2 else "0" + str(trueCurrent)
            newDateTimes[i] = oldDateTimes[i][:11] + hour + ":00:00"

    #replace with fixed datetimes
    df["DateTime"] = newDateTimes

    return df

def concatenateRainfallData(fixTimes = True):
    '''This function takes each seperate, untouched .csv file and joins them
    into a single master file named master.xlsx with a total column.
    This function assumes each .xls file has the same Date range.
    If the time fix is not desired, pass fixTimes as false.

    returns: pandas df of all rain data with total
    '''
    path = "Rainfall/new rainfall data"          #depends on where the current file is openned
    filenames = getFileNames(path, ".txt")

    #read first file into a dataframe
    df = pd.read_csv(path + "/" + filenames[0], header=1)
    df.drop(columns=df.columns[2:], inplace=True)       #removing all but first 2 columns

    #join others onto the existing dataframe
    for i in range(1, len(filenames)):
        temp_df = pd.read_csv(path + "/" + filenames[i], header=1)
        rainfallData = np.array(temp_df[temp_df.columns[1]])
        title = "Rainfall Amount (inches)." + str(i)
        df[title] = rainfallData
    
    #changing column names to reflect origin
    names = ["DateTime"]
    for i in range(len(filenames)):
        name = filenames[i][:filenames[i].find("_")] + " Rainfall (in)" #substring to first underscore in filename
        if name in names:
            name = filenames[i][:filenames[i].find("_", filenames[i].find("_")+1 )] + " Rainfall (in)" #to second underscore
            names.append(name)
        else:
            names.append(name) 
    df.columns = names

    # #casting types to columns
    # for col in df.columns[1:]:
    #     # df[col] = pd.to_numeric(df[col])
    #     print(col, type(df[col]))

    # adding total column
    totals = np.empty(shape=np.shape(df["DateTime"]))   #allocates memory needed all at once
    for i in range(len(df["DateTime"])):
        value = 0
        for col in df.columns[1:]:
            value += df[col][i]
        totals[i] = value           #overiding empty value in each index with total value
    df.insert(loc=1, column="Total Rainfall (in)", value=totals)    #puts new column in location 1, i.e. right after DateTime

    # #fixing issues with date order
    if fixTimes:
        df = fixTimesRainfall(df)

    #fixing type issues from .txt file reading
    for col in df.columns[1:]:
        df[col] = np.array(df[col]).astype(np.double)

    return df

def createAggregateFeatures(aggAll = False):
    '''This function will aggregate the total rainfall over periods
    of times, joining aggregate values as columns to the rainfall data.
    returns: pandas dataframe with full rainfall data and aggregate rainfall data
    '''
    numberOfDays = 7   #how many days the aggregates go back--df will get one column for each day
    df = concatenateRainfallData()

    if aggAll:
        columnList = df.columns[1:]
    else:
        columnList = [df.columns[1]]

    for col in columnList:
        #setting up to create aggregate values
        rainArr = np.array(df[col])
        hourIncrements = [24*x for x in range(3, numberOfDays + 1)]

        #aggregate creation
        for hours in hourIncrements:
            agg = hours*[np.nan]    #initial null values since cannot aggregate for these times
            for i in range(hours, len(rainArr)):
                value = np.sum(rainArr[i-hours:i])    #np sum is faster
                agg.append(value)
            
            #adding new column to dataframe
            agg = np.array(agg)
            header = col[:col.find(" ")] + " " + str(hours) + " Hour Rainfall Aggregate"
            df[header] = agg
    
    return df
