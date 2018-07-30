#!/usr/bin/env python

# Script for mapping pervious surfaces using CIR imagery, cadastre and OSM data in Esri ArcGIS 10.2.2
# Python 2.7
# author: Sebastian Schmidt - July 2018

# inspired by:
# https://gis.stackexchange.com/questions/250896/calculate-ndvi-using-arcpy-spatial-analyst
# tools: https://pro.arcgis.com/de/pro-app/tool-reference/introduction-anatomy/anatomy-of-a-tool-reference-page.htm

# import modules arcpy and string
import arcpy, string, os

# import the environment settings and spatial analyst extension
from arcpy import env
from arcpy.sa import *

# check out the Spatial Analyst extension
arcpy.CheckOutExtension("spatial")

# set directory and workspace
out = "C:\impervious"
input_dir = "C:\impervious\CIR"
output_dir = "C:\impervious\Result"
env.workspace = r"C:\impervious\CIR"

# input data
impervious_filter = "C:\impervious\Vector\Filter.shp"
input_agriculture = "C:\impervious\Vector\Agriculture.shp"
administrative_clip = "C:\impervious\Vector\Mannheim.shp"

# calculate pervious surfaces for every raster
for tif in os.listdir(input_dir):
	if tif.endswith(".tif"):
		
		# calculate NDVI
		nir_band_raster = tif + "\Band_1"
		red_band_raster = tif + "\Band_3"
	
		ndvi_raster = Divide(
			Float(Raster(nir_band_raster) - Raster(red_band_raster)), Float(Raster(nir_band_raster) + Raster(red_band_raster)))
		
		print "calculating NDVI"
		
		# filter all the values >= 0
		filtered_raster=ExtractByAttributes(ndvi_raster, "VALUE >= 0") 
		
		# save raster as integer
		outInt = Int(filtered_raster)
		
		print "NDVI calculated of " + tif
		
		# smoothing raster with Majority Filter tool
		outMajFilt = MajorityFilter(outInt, "FOUR", "MAJORITY")
		
		# smoothing raster with Boundary Clean tool
		OutBndCln = BoundaryClean(outMajFilt, "NO_SORT", "TWO_WAY")

		# polygonize NDVI raster
		rtp = arcpy.RasterToPolygon_conversion(OutBndCln)

		print "conversion of " + tif + " completed"
		
		# merge NDVI with ALKIS agricultural areas
		vectordata = arcpy.Merge_management([rtp, input_agriculture])
		
		# union with vector layers
		Union_vector = arcpy.Union_analysis([vectordata, impervious_filter])
		
		print "union of " + tif + " completed"
		
		union = "union" + tif
		arcpy.MakeFeatureLayer_management(Union_vector, union)
		
		# select all the objects outside of the vector layers
		OutFilter = arcpy.SelectLayerByAttribute_management(union, "NEW_SELECTION", "Filter = ' '")
		
		# Clip with administrative outline
		vector_filter = arcpy.Clip_analysis(OutFilter, administrative_clip)
		
		# Clip with raster outline to clip agricultural areas
		outRas = Raster(tif)*0
		outline_vector = arcpy.RasterToPolygon_conversion(outRas)
		final_clip = arcpy.Clip_analysis(vector_filter, outline_vector)

		# add field and calculate area of polygons
		added_field = arcpy.AddField_management(final_clip, "area", "DOUBLE")
		final_clip_area = arcpy.CalculateField_management(added_field, "area", "!SHAPE.area!", "PYTHON")
		
		# select all polygons >= 1 squaremeter
		arcpy.MakeFeatureLayer_management(final_clip_area, "final" + tif)
		Out_Filter = arcpy.SelectLayerByAttribute_management("final" + tif, "NEW_SELECTION", "area >= 1")
		
		print "clip of " + tif + " completed"
		
		# dissolve result
		out_feature = output_dir+"\\"+'pervious_'+tif[:-3]+'shp'
		pervious = arcpy.Dissolve_management(Out_Filter, out_feature)

		print " " + tif + " completed"
		print "    "

print "All raster tiles calculated"
print "     "


# merge all the raster tiles for the entire city
arcpy.env.workspace = r"C:\impervious\Result"
shplist =  arcpy.ListFeatureClasses('*.shp')  
arcpy.Merge_management(shplist, os.path.join(out, 'Pervious.shp'))  

print " Finished "
