import pydeck as pdk
import geopandas as gpd
import pandas as pd

# Load data from a JSON file into a pandas DataFrame
# The parameters are set to ensure that the data is loaded as strings without any conversion
df = pd.read_json("sample.json", orient="index", convert_dates=False,
                  keep_default_dates=False, convert_axes=False, dtype=int, precise_float=False, date_unit=None, )
# Reset the index of the DataFrame
df.reset_index(inplace=True)
# Rename the columns of the DataFrame
df.columns = ["GEOID", "population"]

# Load a GeoJSON file into a GeoDataFrame
gdf = gpd.read_file('mi1.json', geometry='geometry')
# Merge the DataFrame and GeoDataFrame on the 'GEOID' column
gdf = gdf.merge(df, on='GEOID')
# Create a new column 'color' in the GeoDataFrame, which is the ratio of the 'population' column to its maximum value
gdf["color"] = gdf['population'] / gdf['population'].max()

# Create a new GeoDataFrame for the centroids of the geometries in the original GeoDataFrame
# Also, copy the 'population' column from the original GeoDataFrame
centroids = gpd.GeoDataFrame(geometry=gdf.centroid, crs=gdf.crs)
centroids["population"] = gdf['population']

# Define the initial view state for the pydeck visualization
# The latitude and longitude are set to the mean of the y and x coordinates of the centroids, respectively
view_state = pdk.ViewState(latitude=centroids.centroid.y.mean(), longitude=centroids.centroid.x.mean(), zoom=6,
                           max_zoom=12)

# Define a GeoJsonLayer for the geometries in the original GeoDataFrame
polygon = pdk.Layer("GeoJsonLayer", gdf, stroked=True, filled=True, opacity=0.7, get_line_color=[255, 0, 0],
                    get_fill_color="[255, 140, 0, 250 * color]",
                    line_width_min_pixels=2)

# Create a Deck with the defined layers and initial view state
r = pdk.Deck(layers=[polygon], initial_view_state=view_state)
# Export the Deck to an HTML file
r.to_html("geojson_layer.html")
