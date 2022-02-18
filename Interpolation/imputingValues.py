import numpy as np
import pandas as pd
from scipy.interpolate import CubicSpline
from scipy.interpolate import interp1d
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

@timer
def main():
    # reading in initial data
    df = pd.read_csv("Interpolation/data.csv")

    for col in df.columns[1:]:
        # getting array from a column
        arr = np.array(df[col])
        if col == "SWTP Total Influent Flow":
            arr = np.array([np.nan if x < 3.7 else x for x in arr]) # removing suspicious low flow values

        # finding all null values present and how many in a row
        index = 0
        while index < len(arr):
            # finding null gap
            if np.isnan(arr[index]):
                # getting width of null gap
                width = 1
                while index + width < len(arr) and np.isnan(arr[index + width]):
                    width += 1

                if width < 7 and index + width + 1 < len(arr):
                    # interpolate data!
                    # remember: all values before this index are filled
                    # want next 10 values if not null, else however many there are available until first null, guarenteed at least 1
                    if width == 1:
                        # linear interpolate
                        x = [index-1] + [index+1]
                        y = [arr[i] for i in x]
                        linInterplator = interp1d(x, y)

                        # adding imputed value into array
                        arr[index] = linInterplator(index)
                    
                    elif width == 2:
                        # linear interpolate
                        x = [index-1] + [index+2]
                        y = [arr[i] for i in x]
                        linInterplator = interp1d(x, y)
        
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

                        #replacing null values in array with interpolated values
                        for i in nullRange:
                            arr[i] = cspline(i)

                # move index forward past gap, continue searching
                index += width

            # no null gap, so continue searching
            else:
                index += 1
        
        # replacing column with new array
        df[col] = arr
    
    df.to_csv("Interpolation/Imputed Data.csv", index=False)


if __name__ == "__main__":
    main()