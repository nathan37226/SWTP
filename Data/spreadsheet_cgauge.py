import pandas as pd
from spreadsheet_utility import *

def createCreekGauge(qualCodes = False):
    '''This function creates a joined dataframe file of filtered, hourly data from the
    original source files in the creek gauge data subdirectory.
    returns: pandas dataframe of all creek gauge data
    '''
    #getting filenames
    path = "Creek Gauge/creek gauge data"
    filenames = getFileNames(path, ".xlsx")

    #formatting data for further joining
    for file in filenames:
        #reading file into a 2D array
        df = pd.read_excel(path + "/" + file, engine="openpyxl", header=29)

        #taking only whole hour values--sometimes by 5 mins, sometimes by 15 mins
        arr = np.array([list(x.split("\t")) for x in df[df.columns[0]]])
        reducedArr = []
        for row in arr:
            mins = row[2][14:]
            if mins == "00":
                reducedArr.append(row)
        
        #dropping unwanted columns
        columnNames = ["Agency", "ID Num?", "DateTime", "Timezone", file[:file.find(" ")] + " Gauge Height (ft)", file[:file.find(" ")] + " Qualification Code"]
        df = pd.DataFrame(reducedArr, columns=columnNames)
        df.drop(columns=["Agency", "ID Num?", "Timezone"], inplace=True)

        saveFormattedExcel(df, "Creek Gauge/Formatted " + file)
    

    ldf = pd.read_excel("Creek Gauge/Formatted " + filenames[0], engine="openpyxl")
    
    #other columns are added through the left outer join because of 
    #miscrepencies with the dates, e.g. they don't have the same values for the datetime columns
    #missing values are present
    for i in range(1, len(filenames)):
        rdf = pd.read_excel("Creek Gauge/Formatted " + filenames[i], engine="openpyxl")
        ldf = joinToDataframeImproved(leftDf = ldf, rightDf = rdf)

    #casting double types where needed
    for col in ldf.columns:
        if col.find("Height") > 0:
            ldf[col] = np.array(ldf[col]).astype(np.double)

    #removing qualCodes if desired
    if not qualCodes:
        colList = []
        for col in ldf.columns:
            if col.find("Code") > 0:
                colList.append(col)

        ldf.drop(columns=colList, inplace=True)

    return ldf
            

