import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.dates as mdates
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline

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
    df = pd.read_csv("Interpolation/Joined Influent and Rainfall and Weather and Groundwater and Creek Gauge.csv", parse_dates=["DateTime"])

    # getting wanted values out of dataframe
    arr = np.array(df["SWTP Total Influent Flow"])
    arr = np.array([np.nan if x < 3.7 else x for x in arr]) # removing suspicious low flow values
    # arr = np.array(df["Ozark Aquifer Depth to Water Level (ft)"])

    # adding null patches and original data to figure
    fig, ax = plt.subplots()
    fig, ax = visualizeMissingValues(df["DateTime"], arr, fig, ax)

    # finding all null values present and how many in a row
    index = 0
    pairs = []                  # formatted like [(start index, num values)]
    while index < len(arr):
        if np.isnan(arr[index]):
            width = 1
            while np.isnan(arr[index + width]):
                width += 1
            pairs.append((index, width))
            index += width
        else:
            index += 1

    # for pair in pairs:
    #     print("Null values starting at index: {i}. {w} total nulls".format(i=pair[0], w=pair[1]))

    # interpolation
    dates = np.array(df["DateTime"])    # so that interpolated values can be plotted
    for pair in pairs:
        if pair[1] < 7:
            # interpolation for short gaps -- cubic splines

            # getting number of points before and after the null values
            lenBackwards = 0
            while lenBackwards < 15 and not np.isnan(arr[pair[0] - lenBackwards - 1]):
                lenBackwards += 1
            lenForwards = 0
            while lenForwards < 15 and not np.isnan(arr[pair[0] + pair[1] + lenForwards]):
                lenForwards += 1
            # print("For null {index}, start index = {sindex} and end index = {eindex}. {w} total nulls".format(index = pair[0], 
            #     sindex = pair[0] - lenBackwards, eindex = pair[0] + lenForwards, w = pair[1]))
            
            # setting ranges of values to get x and y points for interpolation
            nullRange = list(range(pair[0], pair[0] + pair[1], 1))
            totalRange = list(range(pair[0] - lenBackwards, pair[0] + lenForwards + 1, 1))
            x = [x for x in totalRange if x not in nullRange]
            y = [arr[i] for i in x]

            # building spline and interpolating
            cspline = CubicSpline(x, y)
            interpolationRange = list(range(pair[0] - 1, pair[0] + pair[1] + 1, 1))

            # plotting interpolated values
            newDates = [dates[i] for i in interpolationRange]
            ax.plot(newDates, cspline(interpolationRange), "g--")

        else:
            # interpolation for long gaps ???
            continue

    plt.show(block=True)

if __name__ == "__main__":
    main()