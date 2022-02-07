"""
Author:             Nathan Obert
Description:        This file contains four utility functions created to streamline the
                    process of cleaning input data for the SWTP Influent Flow project.
                    None of the functions are specific to a source of data.
"""
import glob
import pandas as pd
import numpy as np
from time import time

def getFileNames(path, filetype):
    '''This function gets the names of all files in the directory
    from this file's location.
    Note that each filename is just the filename with no path included.
    Returns: list of strings
    '''
    return [filename[len(path) + 1:] for filename in glob.glob(path + "/*" + filetype)]

def reformatDateTime(s):
    '''Changes a string datetime of form "m/d/yyyy hh:mm"
    to form "yyyy-mm-dd hh:mm:ss".
    Ex: "2/28/2017 0:00" becomes "2017-02-28 00:00:00"
    returns: formatted string
    '''
    #indicies to slice at
    firstSlash = s.find("/")
    secondSlash = s.rfind("/")
    space = s.find(" ")
    colon = s.find(":")

    #seperating out year, month, and day
    year = s[secondSlash + 1 : space]
    day = s[firstSlash + 1 : secondSlash]
    month = s[:firstSlash]
    hour = s[space + 1 : colon]

    #reformating day, month, and hour to be two digits
    day = day if len(day) == 2 else "0" + day
    month = month if len(month) == 2 else "0" + month
    hour = hour if len(hour) == 2 else "0" + hour

    return year + "-" + month + "-" + day + " " + hour + ":00:00"

def saveFormattedExcel(df, filename):
    '''This function saves a pandas dataframe df to as a .xlsx
    with a given filename. Further, it formats all the columns
    to be dynamically sized.
    Must have module xlsxwriter.
    The filename must include .xlsx.
    '''
    #getting writer object
    writer = pd.ExcelWriter(filename, engine="xlsxwriter") 

    #saving data to excel through writer object
    df.to_excel(writer, sheet_name='master', index=False)

    #dynamic column sizing for all columns
    for column in df:
        #length of either biggest object in a column or the column title, whichever is largest
        column_length = max( 12.5, len(column) ) + 1.5
        if column == "DateTime":
            column_length = 18      #overwriting value due to know largest value and datetime representation wonkiness -- it'd be v large o.w.
        #location of column
        col_idx = df.columns.get_loc(column)
        #setting the specific sheet's column widths
        worksheet = writer.sheets['master']
        worksheet.set_column(col_idx, col_idx, column_length)

    writer.save()

def removeNulls(df, columnIndexWithNull = 2):
    '''This function removes null values--np.nan--from the dataframe
    by dropping the indicies where they are found.
    columnWithNull: any single column, integer index, that has a null value
    return: pandas dataframe'''
    arr = np.array(df[df.columns[columnIndexWithNull]])
    nullLocations = np.argwhere(np.isnan(arr))
    nullLocations = [x[0] for x in nullLocations]
    df = df.drop(axis=0, index=nullLocations)
    df.reset_index(drop=True, inplace=True)
    return df

#previous left outer join
def joinToDataframe(leftPath, rightPath):
    '''Joins the data located in .xlsx from the right path to the combined influent 
    flow data located in the left path.
    Joins on the date and hour under columns DateTime through a left outer join 
    of influent data and rainfall data.
    path: address and path to .xlsx file, must have column DateTime 
    returns: pandas df with joined data
    '''
    #getting data to join together; going to get data from arrays to created the joined data
    flowDf = pd.read_excel(leftPath, engine="openpyxl")
    otherDf = pd.read_excel(rightPath, engine="openpyxl")
    flowArr = flowDf.to_numpy()
    otherArr = otherDf.to_numpy()
    combinedArr = []    #better to append data to list instead of np.array

    #getting column headers for new dataframe being created
    columnNames = []
    for name in flowDf.columns:
        columnNames.append(name)
    for name in otherDf.columns[1:]:
        columnNames.append(name)

    #setting up string comparison values for the left outer join
    flowTimes = list(map(str, flowDf["DateTime"]))
    flowTimes = np.array([x[:16] for x in flowTimes])
    otherTimes = list(map(str, otherDf["DateTime"]))
    otherTimes = np.array([x[:16] for x in otherTimes])

    #computing left outer join
    for i in range(len(flowTimes)):
        newEntry = [x for x in flowArr[i]]  #copying out values from the flow data
        locations = np.nonzero(otherTimes == flowTimes[i])   #letting np find location of matching rainfall datetime

        if np.size(locations[0]) > 0:
            #found, so get values and append
            for value in otherArr[locations[0][0]][1:]:
                newEntry.append(value)
        else:
            #not found, so appending null values for each column
            for i in otherDf.columns[1:]:
                newEntry.append(np.nan)
        combinedArr.append(newEntry)

    return  pd.DataFrame(np.array(combinedArr), columns=columnNames)

def joinToDataframeImproved(**kwargs):
    '''Keyword Arguments:
    leftPath: string location of a .xlsx file
    rightPath: string location of a .xlsx file

    leftDf = pandas dataframe
    rightDf = pandas dataframe

    Description:
    Joins the data located in right to the data located in the left.
    Both must have the column "DateTime".
    Performs a left outer join on both sets of data through
    the DateTime column
    returns: pandas dataframe with joined data
    '''
    keys = list(kwargs.keys())
    lDf = pd.DataFrame()
    rDf = pd.DataFrame()
    if "leftPath" in keys and "rightPath" in keys:
        #create dataframes through paths
        lDf = pd.read_excel(kwargs["leftPath"], engine="openpyxl")
        rDf = pd.read_excel(kwargs["rightPath"], engine="openpyxl")

    elif "leftDf" in keys and "rightDf" in keys:
        #reassign names through passed kwarg dataframes
        lDf = kwargs["leftDf"].copy()
        rDf = kwargs["rightDf"].copy()

    else:
        raise TypeError("Incorrect keyword arguments passed")


    #getting data to join together; going to get data from arrays to created the joined data
    lArr = lDf.to_numpy()
    rArr = rDf.to_numpy()
    combinedArr = []    #better to append data to list instead of np.array

    #getting column headers for new dataframe being created
    columnNames = []
    for name in lDf.columns:
        columnNames.append(name)
    for name in rDf.columns[1:]:
        columnNames.append(name)

    #setting up string comparison values for the left outer join
    flowTimes = list(map(str, lDf["DateTime"]))
    flowTimes = np.array([x[:16] for x in flowTimes])
    otherTimes = list(map(str, rDf["DateTime"]))
    otherTimes = np.array([x[:16] for x in otherTimes])

    #computing left outer join
    for i in range(len(flowTimes)):
        newEntry = [x for x in lArr[i]]  #copying out values from the flow data
        locations = np.nonzero(otherTimes == flowTimes[i])   #letting np find location of matching rainfall datetime

        if np.size(locations[0]) > 0:
            #found, so get values and append
            for value in rArr[locations[0][0]][1:]:
                newEntry.append(value)
        else:
            #not found, so appending null values for each column
            for i in rDf.columns[1:]:
                newEntry.append(np.nan)
        combinedArr.append(newEntry)

    return  pd.DataFrame(np.array(combinedArr), columns=columnNames)

def timer(funct):
    '''A decorator to place on functions to see how long they take
    '''
    def wrapper(*args, **kwargs):
        before = time()
        funct(*args, **kwargs)
        after = time() - before
        print("\n\n")
        if after < 60:
            print("Function took:", time() - before, "seconds")
        else:
            print("Function took:", (time() - before) / 60, "minutes")
    return wrapper
