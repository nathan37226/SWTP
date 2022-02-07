import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from seaborn import heatmap
from scipy.stats import pearsonr

def joinRainfall(fixTimesOption = True):
    '''This function reads from master.xlsx sheet 'master' to get rainfall data and from
    SWTP Total Data - Copy.xlsx sheet Total to get influent flow data.
    It then joins the two together, rectifying some issues with the rainfall data's timestamps
    unless fixTimesOption is False.
    It saves the joined data into 'Joined Master.xlsx' once finished.'''


    #getting data into 2D arrays
    rainfallDf = pd.read_excel("master.xlsx", sheet_name="master", engine="openpyxl", header=2, nrows=44256)
    rainfallDf.sort_values(by=['Device Time'], kind='stable')   #stable so that daylight savings times aren't messed up
    # rainfallDf = rainfallDf.drop_duplicates(subset=['Device Time'])
    rainfallDf.columns = ["DateTime" if x == "Device Time" else x for x in rainfallDf.columns]  #changing header name
    rainfallArr = rainfallDf.to_numpy()

    flowDf = pd.read_excel("SWTP Total Data - Copy.xlsx", sheet_name="Total", engine="openpyxl")
    flowDf = flowDf.drop(columns=[flowDf.columns[-1]])
    flowArr = flowDf.to_numpy()


    #getting column headers for new dataframe being created
    columnNames = []
    for name in flowDf.columns:
        columnNames.append(name)
    for name in rainfallDf.columns:
        if name != "DateTime":
            columnNames.append(name)

    
    #setting up string comparison values for the left outer join, flowDf x rainfallDf
    combinedArr = []
    flowTimes = list(map(str, flowDf["DateTime"]))
    flowTimes = np.array([x[:16] for x in flowTimes])
    rainTimes = list(map(str, rainfallDf["DateTime"]))
    rainTimes = np.array([x[:16] for x in rainTimes])

    #fixing some wrong values in rain gague time--fixes a few hundred rows where times are wacky
    if fixTimesOption:
        for i in range(1, len(rainTimes) - 1):
            beforeStr = str(rainfallArr[i - 1][0])
            afterStr = str(rainfallArr[i + 1][0])
            currentStr = str(rainfallArr[i][0])
            before = int(beforeStr[10:13])
            after = int(afterStr[10:13])
            current = int(currentStr[10:13])
            #if after is 00 or 01, make into 24 or 25
            if after <= 1:
                after += 24
            #catching bad values
            if ( (current - 1 != before) or (current + 1 != after) ) and (after - before == 2):
                trueCurrent = (before + 1) % 24
                hour = str(trueCurrent) if len(str(trueCurrent)) == 2 else "0" + str(trueCurrent)
                rainTimes[i] = currentStr[:11] + hour + ":00"
        

    #left outer join onto influent flow data
    for i in range(len(flowTimes)):
        newEntry = [flowArr[i][0], flowArr[i][1]]
        locations = np.nonzero(rainTimes == flowTimes[i])

        if np.size(locations[0]) > 0:
            #found, so get values and append
            for value in rainfallArr[locations[0][0]][1:]:
                newEntry.append(value)
        else:
            #not found, so search for before
            for x in range(12):
                newEntry.append(np.nan)
        combinedArr.append(newEntry)

    combinedDf = pd.DataFrame(combinedArr, columns=columnNames)
    combinedDf.to_excel("Joined Master.xlsx", index=False)

def removeNulls(df, columnWithNull = 2):
    '''Utility function to remove null values--np.nan--from the dataframe.
    columnWithNull: any single column, integer index, that has a null value
    return: pandas dataframe'''
    arr = np.array(df[df.columns[columnWithNull]])
    nullLocations = np.argwhere(np.isnan(arr))
    nullLocations = [x[0] for x in nullLocations]
    df = df.drop(axis=0, index=nullLocations)
    df.reset_index(drop=True, inplace=True)
    return df

def removeLowFlows(df):
    '''Some flow rates on days are 0 or close to 0. The next highest is around 9.
    This function removes those days where something is probably wrong with the data.
    returns: pandas dataframe'''
    arr = np.array(df["SWTP Total Influent Flow"])
    locations = np.nonzero(arr < 4)
    return df.drop(axis=0, index=locations[0])

def getData():
    '''Gets data from the "filtered master.json" file.
    Faster than reading from an excel spreadsheet.
    Equivalent to:
    removeNulls(pd.read_excel("master.xlsx", sheet_name="Joined Master", engine="openpyxl"))'''
    return pd.read_json("filtered master.json")

def createAggregateFeatures():
    df = getData()
    totalRain = np.array(df["Total Rainfall (in)"])
    hourIncrements = [24*x for x in range(1, 11)]

    for hours in hourIncrements:
        agg = hours*[np.nan]
        for i in range(hours, len(totalRain)):
            value = np.sum(totalRain[i-hours:i])
            agg.append(value)
        agg = np.array(agg)
        header = str(hours) + " Hour Rainfall Aggregate"
        df[header] = agg

    # df.to_json("master with aggregate.json", double_precision=12)
    # df.to_excel("master with aggregate.xlsx", index=False)
    return df

    

def makeCovMatrixandHeatmap():
    # df = pd.read_excel("master.xlsx", sheet_name="master", engine="openpyxl", header=2, nrows=44351)
    df = getData()
    # df = createAggregateFeatures()
    df = df.drop(axis=1, columns="SWTP Total Influent Flow")
    covMatrix = df.cov()
    covMatrix.to_excel("Covariance Matrix Test.xlsx")

    ax = heatmap(covMatrix, cmap='mako', robust=True)
    ax.set_title("Rainfall Covariance Heatmap")
    plt.show()

def correlationPerRainFeature():
    # df = removeNulls(pd.read_excel("master.xlsx", sheet_name="Joined Master", engine="openpyxl"))

    df = removeNulls(createAggregateFeatures(), -1)
    yVals = np.array(df["SWTP Total Influent Flow"])    

    #finding pearson r correlation values with rainfall features and influent flow rates
    bestIndex = 0
    bestValue = 0
    for i in range(2, len(df.columns)):
        xVals = np.array(df[df.columns[i]])
        r, _ = pearsonr(xVals, yVals)
        if r > bestValue:
            bestIndex = i
            bestValue = r
        print(df.columns[i] + ": r = ", r)

    xVals = np.array(df[df.columns[bestIndex]])
    plt.scatter(xVals, yVals, s=.8)

    m, b = np.polyfit(xVals, yVals, 1)
    plt.plot(xVals, m * xVals + b, 'r')

    plt.xlabel(df.columns[bestIndex])
    plt.ylabel("SWTP Total Influent Flow")
    plt.show()


def main():
    makeCovMatrixandHeatmap()
    correlationPerRainFeature()
    

if __name__ == "__main__":
    main()