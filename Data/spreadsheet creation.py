"""
Author:             Nathan Obert
Description:        This file contains a function to join all data described in
                    spreadsheet_flow, spreadsheet_rainfall, and spreadsheet_atmo
                    into excel files for easier use and access.
                    The main function will combine all the data into files
                    as it's read. To use the main function, data must be stored
                    in the appropriate folders.

                    Folders: in the same directory as this and the other .py files,
                    have "SWTP Influent Data", "Rainfall", and "Atmosphere Conditions"
                    with appropriate folders and data within.
"""
from spreadsheet_utility import *
from spreadsheet_rainfall import *
from spreadsheet_flow import *
from spreadsheet_atmo import *
from spreadsheet_gwater import *
from spreadsheet_cgauge import *

@timer
def main():
    '''Implements a data pipline.
    '''
    ldf = concatenateInfluentFlow()
    ldf = removeLowFlows(ldf)
    saveFormattedExcel(ldf, "SWTP Influent Data/Combined Influent.xlsx")

    rdf = concatenateRainfallData()
    saveFormattedExcel(rdf, "Rainfall/Combined Rainfall.xlsx")

    rdf = createAggregateFeatures()
    # rdf = createAggregateFeatures(True)   #makes everything take long, adds individual aggregate values for each rainfall source
    saveFormattedExcel(rdf, "Rainfall/Combined Rainfall with Aggregate.xlsx")

    ldf = joinToDataframeImproved(leftDf=ldf, rightDf=rdf)
    saveFormattedExcel(ldf, "Joined Influent and Rainfall.xlsx")

    rdf = getHourlyConditions()
    saveFormattedExcel(rdf, "Atmosphere Conditions/Hourly Weather Data.xlsx")

    ldf = joinToDataframeImproved(leftDf=ldf, rightDf=rdf)
    saveFormattedExcel(ldf, "Joined Influent and Rainfall and Weather.xlsx")
    
    rdf = createGroundwater()
    saveFormattedExcel(rdf, "Groundwater/Combined Groundwater.xlsx")

    ldf = joinToDataframeImproved(leftDf=ldf, rightDf=rdf)
    saveFormattedExcel(ldf, "Joined Influent and Rainfall and Weather and Groundwater.xlsx")

    rdf = createCreekGauge()
    saveFormattedExcel(rdf, "Creek Gauge/Combined Creek Gauge.xlsx")

    ldf = joinToDataframeImproved(leftDf=ldf, rightDf=rdf)
    saveFormattedExcel(ldf, "Joined Influent and Rainfall and Weather and Groundwater and Creek Gauge.xlsx")



if __name__ == "__main__":
    main()