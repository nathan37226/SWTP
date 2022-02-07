"""
Author:             Nathan Obert
Description:        This file contains functions related to gathering and combining
                    the groundwater data sources into a single pandas dataframe.
"""
import pandas as pd
import numpy as np
from spreadsheet_utility import *

def reformatGroundwaterDf(filename, df):
    '''This function manipulates the data in the original dataframe
    of groundwater data to become hourly with fewer columns.
    filename is an argument that helps name the depth column
    returns: edited pandas dataframe
    '''
    #slicing out column to split up values in as a list
    arr = list(df[df.columns[0]]) 

    #taking only even hour values, putting into reducedArr
    #also splits up into multiple columns
    #cannot just do every other row because the datetime data is not perfect--has missing values
    reducedArr = []
    for i in range(len(arr)):
        temp_list = list(arr[i].split("\t"))
        datetime = str(temp_list[2])
        if datetime[14:] == "00":
            reducedArr.append(temp_list)

    # #transforming arr into a 2D array by splitting the values
    # reducedArr = [list(x.split("\t")) for x in reducedArr]

    #creating dataframe
    columnNames = ["Agency", "ID Num?", "DateTime", "Timezone", filename[19:-5] + " Depth to Water Level (ft)", filename[19:-5] + " Qualification Code"]
    df = pd.DataFrame(reducedArr, columns=columnNames)

    #casting double to water level -- originally number stored as text
    df[df.columns[4]] = np.array(df[df.columns[4]]).astype(np.double)
    
    #dropping unwanted columns
    df.drop(columns=["Agency", "ID Num?", "Timezone"], inplace=True)

    return df

def createGroundwater(qualCodes = False):
    '''This function creates a joined dataframe file of filtered, hourly data from the
    original source files in the groundwater data subdirectory.
    returns: pandas dataframe of all groundwater data
    '''
    #getting filenames
    path = "Groundwater/groundwater data"
    filenames = getFileNames(path, ".xlsx")

    #formatting data for further joining
    for file in filenames:
        #reading initial file
        df = pd.read_excel(path + "/" + file, engine="openpyxl", header=29)
        
        #getting wanted data
        df = reformatGroundwaterDf(file, df)

        #saving as excel
        saveFormattedExcel(df, "Groundwater/Formatted " + file)

    ldf = pd.read_excel("Groundwater/Formatted " + filenames[0], engine="openpyxl")
    
    #other columns are added through the left outer join because of 
    #miscrepencies with the dates, e.g. they don't have the same values for the datetime columns
    #missing values are present
    for i in range(1, len(filenames)):
        rdf = pd.read_excel("Groundwater/Formatted " + filenames[i], engine="openpyxl")
        ldf = joinToDataframeImproved(leftDf = ldf, rightDf = rdf)
    
    #casting double types where needed
    for col in ldf.columns:
        if col.find("Depth") > 0:
            ldf[col] = np.array(ldf[col]).astype(np.double)

    #creating an average column
    # averageArr = np.zeros_like(np.array(df[df.columns[0]]))
    # for i in range(len(df[df.columns[0]])):
    #     total = 0
    #     n = 0
    #     for col in df.columns:
    #         if col.find("Depth") > 0:
    #             total += df[col][i]
    #             n += 1
    #     averageArr[i] = total/n
    # df["Average Depth to Water Level (in)"] = averageArr

    #removing qualCodes if desired
    if not qualCodes:
        colList = []
        for col in ldf.columns:
            if col.find("Code") > 0:
                colList.append(col)

        ldf.drop(columns=colList, inplace=True)

    return ldf
