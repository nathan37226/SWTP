import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
import shapely.geometry as geo

#reading in springfield area as latitude and longitude
map = gpd.read_file("Correlation/Springfield Geodata/Street_Centerline.shp") 

map = map.to_crs(epsg=4326)

#gettiing rainfall lat and lon
df = pd.read_excel("Correlation/rainfall addresses.xlsx", engine="openpyxl")
points = [geo.Point(xy) for xy in zip(df["Longitude"], df["Latitude"])]
df["geometry"] = points

#setting up geo dataframe
geoDf = gpd.GeoDataFrame(df, crs="EPSG:4326", geometry=df["geometry"])

#plotting springfield area
fig, ax = plt.subplots()
map.plot(ax=ax, alpha=0.5, color="grey")

#plotting rainfall sources ontop of springfield

#LATER TURN INTO HEATMAP -- use column="correlation" and cmap="rainbow" or something
geoDf.plot(ax=ax, markersize=20, color="red")

plt.show()