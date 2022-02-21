import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.dates as mdates
from datetime import datetime

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
        rectColor: the color of the rectangles
    '''
    # setting up rectangle parameters
    opacityCoeff = 0.5
    rectColor = "red"

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
                allRects.append(mpatches.Rectangle(coords, width, rectHeight, color=rectColor, alpha=opacityCoeff))
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
            allRects.append(mpatches.Rectangle(coords, width, rectHeight, color=rectColor, alpha=opacityCoeff))

        else:
            index += 1

    return allRects


def main():
    # df = pd.read_csv("Interpolation/Joined Influent and Rainfall and Weather and Groundwater and Creek Gauge.csv")
    df = pd.read_csv("Interpolation/Imputed Data.csv", parse_dates=["DateTime"])
    flows = np.array(df["SWTP Total Influent Flow"])
    # dates = np.array([datetime.strptime(s, "%Y-%m-%d %H:%M:%S") for s in df["DateTime"]])
    dates = np.array(df["DateTime"])

    fig, ax = plt.subplots()
    ax.plot(dates, flows)

    rects = makeNullRects(dates, flows)
    for rect in rects:
        ax.add_patch(rect)

    formatter = mdates.ConciseDateFormatter(ax.xaxis.get_major_locator(), formats=["%Y", "%Y-%b", "%b-%d", "%d %H:%M", "%d %H:%M", "%H:%M"])
    locator = mdates.AutoDateLocator()
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_major_locator(locator)

    fig.autofmt_xdate()

    plt.show()
    

if __name__ == "__main__":
    main()