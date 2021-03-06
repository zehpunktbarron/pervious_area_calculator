# pervious_area_calculator
This script (Python 2.7) for ArcGIS 10.2.2 calculates pervious surfaces, based on a pedological definition of soil sealing. Therefore, the remaining areas should be considered either impervious or bodies of water.

For the calculation different data types are necessary. CIR imagery is needed for the calculation of the NDVI. Furthermore, vector data (e.g. cadastre or OSM data) is needed that provides information on buildings, traffic areas (streets, ways, railway tracks) and bodies of water as polygons. These layers should be merged and saved as a file that will be used in the script under the variable impervious_filter. Additionally, polygons representing agricultural areas are needed if the CIR imagery was taken during the leaf-off season. Depending on your study area, a shape portraying the administrative boundaries (e.g. of a city) is required.

After the calculation, you will receive a shapefile for every raster, as well as a merged version for the entire study area that delimits pervious surfaces.
