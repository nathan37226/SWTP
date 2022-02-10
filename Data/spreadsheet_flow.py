"""
Author:             Nathan Obert
Description:        This file contains functions used to join seperate .xlsx files containing
                    SWTP Influent Flow data. In 2021.xlsx, the first few rows are hidden from view.
                    If this is not fixed, exceptions occur when attempting to read from the file.
                    An easy fix is to convert it to .csv and back to .xlsx.
                    The Data was originally sourced from the Southwest Treatment Plant
                    found at https://www.springfieldmo.gov/405/Southwest-Treatment-Plant,
                    though the data used might not be publically avaliable.
"""
import pandas as pd
import numpy as np
from spreadsheet_utility import *

def removeNullsInfluentFlow(df):
    '''This function removes null values present in both
    forms: np.nan, and pd.NaT
    from the concatenated influent flow df.
    Note: did not use removeNulls due to wonky typing of data and null representation
    returns: pandas dataframe without nulls
    '''
    #null total influent flow values
    arr = np.array(df["SWTP Total Influent Flow"])
    badTotalsIndicies = []
    for i in range(len(arr)):
        if np.isnan(arr[i]):
            badTotalsIndicies.append(i)
    badTotalsIndicies = np.array(badTotalsIndicies)

    #null timestamps
    badTimes = np.argwhere(pd.isnull(np.array(df["DateTime"])))
    badTimes = np.array([x[0] for x in badTimes])
    
    #all null indicies
    badIndicies = np.sort(np.append(badTimes, badTotalsIndicies))

    #removing null indicies from df
    df.drop(axis=1, index=badIndicies, inplace=True)
    df.reset_index(drop=True, inplace=True)
    
    return df

def concatenateInfluentFlow(removeNulls = True):
    '''This function joins together each seperate year excel file from 
    the SWTP to make a running total for all five years.
    Ensure only the influent flow data is present in the directory -- NO LAB DATA!
    The files are assumed to be dated by year, meaning they are chronological
    already.
    If null values are desired, pass False.

    returns: pandas dataframe of influent flow data
    '''
    #getting filenames
    path = "SWTP Influent Data/influent data"
    names = getFileNames(path, ".xlsx")

    #getting numpy arrays
    df = pd.read_excel(path + "/" + names[0], engine="openpyxl", header=4)
    dateTimes = np.array(df["DateTime"])
    plant1Flow = np.array(df["SWTP Plant 1 Influent Flow"])
    plant1Gravity = np.array(df["SWTP Plant 1 Gravity Flow"])
    plant2Flow = np.array(df["SWTP Plant 2 Influent Flow"])
    peakFlow = np.array(df["SW_Peak_Flow"])
    for i in range(1, len(names)):
        temp_df = pd.read_excel(path + "/" + names[i], engine="openpyxl", header=3)

        #getting data into np arrays
        temp_dateTimes = np.array(temp_df["DateTime"])
        temp_plant1Flow = np.array(temp_df["SWTP Plant 1 Influent Flow"])
        temp_plant1Gravity = np.array(temp_df["SWTP Plant 1 Gravity Flow"])
        temp_plant2Flow = np.array(temp_df["SWTP Plant 2 Influent Flow"])
        temp_peakFlow = np.array(temp_df["SW_Peak_Flow"])

        #joining arrays to exisiting ones
        dateTimes = np.concatenate((dateTimes, temp_dateTimes))
        plant1Flow = np.concatenate((plant1Flow, temp_plant1Flow))
        plant1Gravity = np.concatenate((plant1Gravity, temp_plant1Gravity))
        plant2Flow = np.concatenate((plant2Flow, temp_plant2Flow))
        peakFlow = np.concatenate((peakFlow, temp_peakFlow))


    #creating total array with null value exception
    #null values are previously stored as "Null", not np.nan
    totals = np.empty_like(plant1Flow)
    for i in range(len(dateTimes)):
        try:
            totals[i] = plant1Flow[i] + plant1Gravity[i] + plant2Flow[i] + peakFlow[i]
            if isinstance(totals[i], str):
                raise TypeError
            elif plant1Flow[i] == 0 or plant2Flow[i] == 0:
                raise TypeError
        except TypeError:
            totals[i] = np.nan
    
    #creating new dataframe
    columnNames = ["DateTime", "SWTP Total Influent Flow", "SWTP Plant 1 Influent Flow", "SWTP Plant 1 Gravity Flow", 
    "SWTP Plant 2 Influent Flow", "SW_Peak_Flow"]
    dateTimes = np.array([pd.to_datetime(x) for x in dateTimes])    #converting datetimes for better display
    df = pd.DataFrame(np.array((dateTimes, totals, plant1Flow, plant1Gravity, plant2Flow, peakFlow)).T, columns=columnNames)    #.T for transpose so put as columns, not rows

    #removing missing datetimes from df
    if removeNulls:
        df = removeNullsInfluentFlow(df)
    
    #casting long double type to all numeric entries
    #the types are wonky up to this point
    for name in df.columns[1:]:
        df[name] = np.array(df[name]).astype(np.longdouble)

    return df

def removeLowFlows(df, tolerance=3.75):
    '''This function removes from a dataframe with all influent flow columns
    indicies with a suspicious low total.
    If plant 1 or plant 2 has a zero value, the row will be 
    removed from the dataframe.
    Further, if the total is less than the tolerance, will be removed.
    returns: pandas dataframe
    '''
    #data to work from
    p1Flow = np.array(df["SWTP Plant 1 Influent Flow"])
    p2Flow = np.array(df["SWTP Plant 2 Influent Flow"])
    totalFlow = np.array(df["SWTP Total Influent Flow"])

    #finding bad indicies
    p1Indicies = np.where(p1Flow == 0)
    p2Indicies = np.where(p2Flow == 0)
    totalIndicies = np.where(totalFlow < tolerance)     #should be much higher, so indiciative of bad value
    badIndicies = np.append(p2Indicies[0], totalIndicies[0])
    badIndicies = np.unique(np.append(p1Indicies[0], badIndicies))

    #dropping the indicies found
    df.drop(axis=1, index=badIndicies, inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df
