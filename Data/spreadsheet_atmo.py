"""
Author:             Nathan Obert
Description:        This file contains functions used to read and format hourly weather
                    data from the Weather Data.csv file.
                    The data was originally sourced from the National Oceanic and Atmosphereic Administration
                    found at https://www.ncdc.noaa.gov/cdo-web/datatools/lcd
                    via submitting a request for Springfield, Missouri.
"""
import pandas as pd
import numpy as np
from spreadsheet_utility import *

def valueFix(value):
    '''The values in Weather Data.csv are not uniform. Sometimes a value will be of form
    "279.68s" instead of "279.68". This handles such cases and converts the given
    string to a np.double.
    returns: np.double of the value
    '''
    try:
        value = np.double(value)
    except ValueError:
        value = str(value)
        if len(value) > 0:
            for i in range(len(value)):
                if value[i] not in "1234567890.":
                    value = np.double(value.replace(value[i], ""))
        else:
            value = np.nan
    return value

def getHourlyConditions():
    '''Obtains only the hourly conditions and Date from the
    file Atmosphere Conditions/Weather Data.csv.
    '''
    #reading wanted hourly columns
    desiredColumns = ["DATE", "REPORT_TYPE", "HourlyAltimeterSetting", "HourlyDewPointTemperature", 
    "HourlyDryBulbTemperature", "HourlyPressureChange", "HourlyPressureTendency",
    "HourlyRelativeHumidity", "HourlySeaLevelPressure", "HourlyStationPressure", "HourlyVisibility",
    "HourlyWetBulbTemperature", "HourlyWindSpeed"]
    df = pd.read_csv("Atmosphere Conditions/atmosphere conditions data/Weather Data.csv", usecols=desiredColumns)

    #filtering by report type
    arr = np.array(df["REPORT_TYPE"])
    badIndicies = np.where(arr != 'FM-15')
    df.drop(axis=0, index=badIndicies[0], inplace=True)
    df.reset_index(drop=True, inplace=True)

    #dropping unwanted report type column
    df.drop(columns=["REPORT_TYPE"], inplace=True)

    #fixing type issues -- some values are like "29.67s" instead of "29.67"
    for col in desiredColumns[2:]:
        arr = np.array(df[col])
        arr = np.array([valueFix(x) for x in arr])
        df[col] = arr

    #fixing datetime formatting
    df.rename({"DATE": "DateTime"}, axis=1, inplace=True)
    df["DateTime"] = np.array([x.replace("T", " ")[:14] + "00:00" for x in np.array(df["DateTime"])])

    return df
