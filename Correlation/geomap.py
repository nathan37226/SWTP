import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
import shapely.geometry as geo
    

#reading in springfield area as latitude and longitude
map = gpd.read_file("Correlation/Springfield Geodata/Street_Centerline.shp") 
map = map.to_crs(epsg=4326)

#getting rainfall lat and lon
df = pd.read_excel("Correlation/rainfall addresses and correlation.xlsx", engine="openpyxl")
points = [geo.Point(xy) for xy in zip(df["Longitude"], df["Latitude"])]
df["geometry"] = points

#setting up geo dataframe
geoDf = gpd.GeoDataFrame(df, crs="EPSG:4326", geometry=df["geometry"])

#plotting springfield area
fig, ax = plt.subplots()
map.plot(ax=ax, alpha=0.5, color="grey")

#plotting rainfall sources ontop of springfield
geoDf.plot(ax=ax, column="Distance Correlation", cmap="coolwarm", legend=True, 
    legend_kwds={'shrink': 0.3, 'label': "Distance Correlation"}, markersize=450)

#adding labels to points
for x, y, label in zip(df["Longitude"], df["Latitude"], df["Label"]):
    ax.annotate(label, xy=(x, y), xytext=(3.75, 8.5), textcoords="offset points", size=10, weight="light")

#adding SWTP to map
lon = -93.361996
lat = 37.155313
offset = .005
leftPoint, rightPoint = geo.Point(lon - offset, lat), geo.Point(lon + offset, lat)
topPoint, bottomPoint = geo.Point(lon, lat + offset), geo.Point(lon, lat - offset)
polyPoints = [leftPoint, topPoint, rightPoint, bottomPoint]
polygon = geo.Polygon([[p.x, p.y] for p in polyPoints])
p = gpd.GeoSeries(polygon)
p.plot(ax=ax, color="tab:orange")
ax.annotate("SWTP", xy=(lon, lat), xytext=(1.5, 5.75), textcoords="offset points", size=10, weight="light")

ax.set_xlabel("Longitude", size=15)
ax.set_ylabel("Latitude", size=15)
plt.title("Aggregate Rain Gauge Distance Correlation to Total Influent Flow Rates", size=18)
plt.show()