import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from seaborn import heatmap
from scipy.stats import pearsonr, spearmanr
import dcor
from time import time

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

def normalize(arr):
    '''Converts an array with range [min, max] to [0, 1],
    preserving whatever inherent structure is present
    returns: normalized numpy array
    '''
    minimum = np.min(arr)
    maximum = np.max(arr)
    return np.array([(x-minimum)/(maximum-minimum) for x in arr])

def makeCovMatrixandHeatmap(df):
    df = df.drop(axis=1, columns="SWTP Total Influent Flow")
    covMatrix = df.cov()
    # covMatrix.to_excel("Covariance Matrix Test.xlsx")

    ax = heatmap(covMatrix, cmap='mako', robust=True, xticklabels=df.columns, yticklabels=df.columns)
    ax.set_title("Rainfall Covariance Heatmap")
    plt.show()
  
def compareCorrelation(df, correlationMeasurementMethod):
    flowArr = np.array(df["SWTP Total Influent Flow"])
    flowNullLocations = np.nonzero(np.isnan(flowArr))[0]

    l = []
    for col in df.columns[2:]:
        arr = np.array(df[col])

        # handle null values by not considering those locations
        arrNullLocations = np.nonzero(np.isnan(arr))[0]
        allNullLocations = np.unique(np.append(flowNullLocations, arrNullLocations))
        currentFlowArr = np.delete(flowArr, allNullLocations)
        arr = np.delete(arr, allNullLocations)

        # hand null values by converting to zero
        # arr = np.nan_to_num(arr)

        r = correlationMeasurementMethod(currentFlowArr, arr)  #if distance correlation
        if correlationMeasurementMethod != dcor.distance_correlation:
            r = r[0]    # returns r, p, only want r value
        l.append([col, r])
    l.sort(key=lambda a: a[0])
    l = l[::-1]
    return np.array(l)
    
@timer
def main():
    # non-rainfall data
    # df = pd.read_csv("Data/Joined Influent and All Rainfall and Weather and Groundwater and Creek Gauge.csv")
    # unwantedCols = [x for x in df.columns if (x.find("Rainfall") >= 0 or x.find("Flow") >= 0) ]
    # unwantedCols.remove("SWTP Total Influent Flow")
    # df.drop(columns=unwantedCols, inplace=True)
    
    # rainfall data
    df = pd.read_csv("All Rainfall.csv")
    
    # if want to normalize -- should not effect anything
    for col in df.columns[1:]:
        df[col] = normalize(df[col])

    # only 168 hour rainfall columns
    unwantedCols = [x for x in df.columns if x.find("168") < 0]
    unwantedCols.remove("SWTP Total Influent Flow")
    df.drop(columns=unwantedCols, inplace=True)
    makeCovMatrixandHeatmap(df)
    
    # methods of computing correlation
    # pearsonRVals = compareCorrelation(df, pearsonr)
    # spearmanRVals = compareCorrelation(df, spearmanr)
    # distanceCorrVals = compareCorrelation(df, dcor.distance_correlation)

    # correlationDf = pd.DataFrame(pearsonRVals, columns=["Feature", "Pearson R"])
    # correlationDf["Spearman R"] = spearmanRVals[:,1]
    # correlationDf["Distance Correlation"] = distanceCorrVals[:,1]

    # correlationDf.to_csv("___ Correlation Table.csv", index=False)

    # # printing sorted correlation values
    # for x in rVals:
    #     print(x)

    

    


if __name__ == "__main__":
    main()