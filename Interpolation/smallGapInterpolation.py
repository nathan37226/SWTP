import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.dates as mdates
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline
from scipy.interpolate import interp1d

import sys
import sklearn.neighbors._base
sys.modules['sklearn.neighbors.base'] = sklearn.neighbors._base
from missingpy import MissForest

def makeNullRects(dates, y):
    '''This function returns a list of matplotlib.patches.Rectangles where
    np.nan values are present in the y array. If values are consecutive,
    the rectangles will widen as needed.
    Note that this function is made for a figure with an x-axis of dates
    Input:
        dates: x axis date time values
        y: y axis range values as np.array, contains np.nan values

    Returns:
        list of matplotlib.patches.Rectangles located where
        y has np.nan values.

    Rectangle Parameters in function:
        opacityCoeff: how solid rectangles appear
        longRectColor: the color of the rectangles with >=7 width
        shortRectColor: the color of the rectanges with <7 width
    '''
    # setting up rectangle parameters
    opacityCoeff = 0.5
    longRectColor = "red"
    shortRectColor = "magenta"

    # prep work for creating rectangles for nan values
    index = 0
    yMax = np.nanmax(y)
    yMin = np.nanmin(y)
    rectHeight = yMax - yMin
    yRectCoor = yMin
    allRects = []   # this is what will be returned

    # creating rectangle patches
    while index < len(y):

        # if nan exists, then need to create a rectangle patch
        if np.isnan(y[index]):
            xRectCoorIndex = index - 1

            # condition for if first y value is nan
            if index == 0:
                xRectCoorIndex += 1
            
            # condition for if last y value is nan, assumes y is not len 2
            elif index + 1 == len(y):
                xRectCoor = mdates.date2num(dates[xRectCoorIndex])
                coords = (xRectCoor, yRectCoor)
                width = mdates.date2num(dates[xRectCoorIndex + 1]) - mdates.date2num(dates[xRectCoorIndex])
                allRects.append(mpatches.Rectangle(coords, width, rectHeight, color=shortRectColor, alpha=opacityCoeff))
                break
                
            # all other cases
            xRectCoor = mdates.date2num(dates[xRectCoorIndex])

            # checking finding how long the rectangle needs to be--how many consecutive null values
            index += 1
            while np.isnan(y[index]):
                index += 1
            rightEdgeIndex = mdates.date2num(dates[index])

            # making rectangle
            coords = (xRectCoor, yRectCoor)
            width = rightEdgeIndex - xRectCoor
            color = shortRectColor
            if index - xRectCoorIndex > 7:
                color = longRectColor
            allRects.append(mpatches.Rectangle(coords, width, rectHeight, color=color, alpha=opacityCoeff))

        else:
            index += 1

    return allRects

def visualizeMissingValues(dates, arr, fig, ax):
    '''This function plots an array of values with datetime x axis values onto
    a given axis, showing patches of null values if present.
    '''
    ax.plot(dates, arr)

    rects = makeNullRects(dates, arr)
    for rect in rects:
        ax.add_patch(rect)

    formatter = mdates.ConciseDateFormatter(ax.xaxis.get_major_locator(), formats=["%Y", "%Y-%b", "%b-%d", "%d %H:%M", "%d %H:%M", "%H:%M"])
    locator = mdates.AutoDateLocator()
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_major_locator(locator)

    fig.autofmt_xdate()
    return fig, ax


def main():
    # reading in initial data
    # df = pd.read_csv("Interpolation/Joined Influent and Rainfall and Weather and Groundwater and Creek Gauge.csv", parse_dates=["DateTime"])
    df = pd.read_csv("Interpolation/Imputed Data.csv", parse_dates=["DateTime"])

    # getting wanted values out of dataframe
    # arr = np.array(df["SWTP Total Influent Flow"])
    # arr = np.array([np.nan if x < 3.7 else x for x in arr]) # removing suspicious low flow values
    # arr = np.array(df["Ozark Aquifer Depth to Water Level (ft)"])
    # arr = np.array(df["James Gauge Height (ft)"])
    arr = np.array(df["Wilsons Gauge Height (ft)"])

    # adding null patches and original data to figure
    fig, ax = plt.subplots()
    fig, ax = visualizeMissingValues(df["DateTime"], arr, fig, ax)

    # finding all null values present and how many in a row
    index = 0
    # pairs = []                  # formatted like [(start index, num values)]
    dates = np.array(df["DateTime"])    # so that interpolated values can be plotted
    while index < len(arr):
        # finding null gap
        if np.isnan(arr[index]):
            # getting width of null gap
            width = 1
            while index + width < len(arr) and np.isnan(arr[index + width]):
                width += 1
            # print("Index = {i}, width = {w}".format(i = index, w = width))

            if width < 7 and index + width + 1 < len(arr):
                # interpolate data!
                # remember: all values before this index are filled
                # want next 10 values if not null, else however many there are available until first null, guarenteed at least 1
                if width == 1:
                    # linear interpolate
                    x = [index-1] + [index+1]
                    y = [arr[i] for i in x]
                    linInterplator = interp1d(x, y)
                    
                    # plotting value
                    interpolationRange = [index-1] + [index] + [index+1]
                    newDates = [dates[i] for i in interpolationRange]
                    ax.plot(newDates, linInterplator(interpolationRange), "g--")

                    # adding imputed value into array
                    arr[index] = linInterplator(index)
                
                elif width == 2:
                    # linear interpolate
                    x = [index-1] + [index+2]
                    y = [arr[i] for i in x]
                    linInterplator = interp1d(x, y)
                    
                    # plotting value
                    interpolationRange = [index-1] + [index] + [index+1] + [index+2]
                    newDates = [dates[i] for i in interpolationRange]
                    ax.plot(newDates, linInterplator(interpolationRange), "g--")

                    # adding imputed values into array
                    arr[index] = linInterplator(index)
                    arr[index+1] = linInterplator(index+1)

                else:
                    # cubic spline interpolation -- sometimes prone to unbelieveable imputed data, but generally close enough to seem right
                    # "Wilsons Gauge Height (ft)" is a bad impution example in one spot to the far right where it dips below the previous minimum
                    lenForwards = 0
                    while lenForwards < 10 and not np.isnan(arr[index + width + lenForwards + 1]):
                        lenForwards += 1

                    lenBackwards = 0
                    while lenBackwards < 10 and not np.isnan(arr[index - lenBackwards - 1]):
                        lenBackwards += 1
                    
                    # getting x and y values for cubic spline and building spline
                    nullRange = list(range(index, index + width, 1))
                    totalRange = list(range(index - lenBackwards, index + width + lenForwards + 1, 1))
                    x = [x for x in totalRange if x not in nullRange]
                    y = [arr[i] for i in x]
                    cspline = CubicSpline(x, y)

                    # plotting interpolated values
                    interpolationRange = list(range(index - 1, index + width + 1, 1))
                    newDates = [dates[i] for i in interpolationRange]
                    ax.plot(newDates, cspline(interpolationRange), "g--")

                    #replacing null values in array with interpolated values
                    for i in interpolationRange:
                        arr[i] = cspline(i)

            # move index forward past gap, continue searching
            index += width

        # no null gap, so continue searching
        else:
            index += 1

    # for pair in pairs:
    #     print("Null values starting at index: {i}. {w} total nulls".format(i=pair[0], w=pair[1]))

    plt.show(block=True)

if __name__ == "__main__":
    main()