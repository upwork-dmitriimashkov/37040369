import pydeck as pdk
import geopandas as gpd

# Function to get data from AWS Glue
def get_data_from_glue():
    """
    This function retrieves data from an AWS Glue catalog. It specifically loads a table named 'aggregation.mmr'
    and filters rows where 'AGGR_CATEGORY' equals 'GEOID'. It selects the 'FIPS_GEOID' and 'count' fields.
    The resulting DataFrame is returned with columns renamed to 'GEOID' and 'population'.
    """
    from pyiceberg.catalog import load_catalog

    # Load the catalog named 'docs' of type 'glue'
    catalog = load_catalog("docs", **{"type": "glue"})

    # Load the table 'aggregation.mmr' from the catalog
    table = catalog.load_table("aggregation.mmr")

    # Scan the table with a filter and selected fields, convert the result to a pandas DataFrame
    mmr = table.scan(
        row_filter="AGGR_CATEGORY = 'GEOID'",
        selected_fields=("FIPS_GEOID", "count"),
    ).to_pandas()

    # Rename the columns of the DataFrame
    mmr.columns = ["GEOID", "population"]

    return mmr

# Call the function to get data from AWS Glue
df = get_data_from_glue()

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
