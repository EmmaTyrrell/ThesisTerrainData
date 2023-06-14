#testing on creating a point later from xy data

print("ready")

#import directories
import arcpy
from arcpy import env
from arcpy.sa import *
import os
from collections import defaultdict
print("arcpy imported")

# estabslish parameters
arcpy.env.workspace = "C:\\Users\\Emma Tyrrell\\Documents\\PSU_SDS\\THESIS_230226"
temporalDataFilesWorkspace = (arcpy.env.workspace + "\\Data\\WeatherStations\\SpatialDataFiles")
terrainDataFilesWorkspace = (arcpy.env.workspace + "\\Data\\TerrainData")
arcpy.env.overwriteOutput = True
demFiles = (arcpy.env.workspace + "\\Data\\DEM")
projectBoundary = (arcpy.env.workspace + "\\Data\\StaticDataGDB.gdb\\ProjectBoundary")
GCSsr = arcpy.SpatialReference(4326)
PCSsr = arcpy.SpatialReference(6432)
print("parameters established")

#add slope
walk = arcpy.da.Walk(demFiles, topdown=True, datatype="RasterDataset")
try:
    #walk for slope
    for dirpath, dirnames, filenames in walk:
        for filename in filenames:
            print(filename + " for slope")

            shapefile_slope = f"slope_{filename[:-13]}_.tif"

            #run slope tool
            try:

                #conduct slope
                outSlope = Slope(os.path.join(dirpath,filename), "DEGREE", 1, "PLANAR", "", "GPU_THEN_CPU")
                print("Slope executed")

                #save slope
                outSlope.save(terrainDataFilesWorkspace + "\\" + shapefile_slope)
                print("Slope saved")

            except Exception as ex:
                print(ex)

except Exception as ex:
    print(ex)

#add aspect
walk = arcpy.da.Walk(demFiles, topdown=True, datatype="RasterDataset")
try:
    #walk for slope
    for dirpath, dirnames, filenames in walk:
        for filename in filenames:
            print((filename + " for aspect"))

            shapefile_aspect = f"aspect_{filename[:-13]}_.tif"

            try:

                #conduct aspect
                outAspect = Aspect(os.path.join(dirpath,filename), "PLANAR", "", "", "GPU_THEN_CPU")
                print("asepct exeuted")

                #save aspect
                outAspect.save(terrainDataFilesWorkspace + "\\" + shapefile_aspect)
                print("aspect saved")

            except Exception as ex:
                print(ex)

except Exception as ex:
    print(ex)

#print contour lines
print('create contour lines...')

walk = arcpy.da.Walk(demFiles, topdown=True, datatype="RasterDataset")
for dirpath, dirnames, filenames in walk:
    print('dirpath = {}, dirnames = {}, filenames = {}'.format(dirpath, dirnames, filenames))
    for filename in filenames:
        print(filename)

        # run 100 contours
        shapefile_contours100 = f"contour_{filename[:-13]}_100.shp"
        try:
            out100Contours = (terrainDataFilesWorkspace + "\\" + shapefile_contours100)
            mergedContours100 = (terrainDataFilesWorkspace + "\\mergedContours100.shp")
            Contour(os.path.join(dirpath, filename), out100Contours, 100, 0)

            print("contour 100 saved")

        except Exception as ex:
            print(ex)

#merge all 100 contour lines with the same tailb
shapes = defaultdict(list)
mergeOutput = terrainDataFilesWorkspace
for root, folder, files in os.walk(terrainDataFilesWorkspace):
    for file in files:
            if file.endswith("100.shp"):
                fullname = os.path.join(root, file)
                group = file.split("_1")[0]
                shapes[group].append(fullname)
for g, shapelist in shapes.items():
    arcpy.management.Merge(inputs=shapelist, output=os.path.join(mergeOutput, g))

gContours = (g + ".shp")
print (gContours)

mergedContours = (terrainDataFilesWorkspace + "\\merged100Contours.shp")
mergedContoursClipped = (terrainDataFilesWorkspace + "\\merged100ContoursClipped.shp")
arcpy.management.MakeFeatureLayer(gContours, mergedContours)
print ("feature layer working")

#export features
arcpy.conversion.ExportFeatures(gContours, mergedContours)
print("check file conversion")

#clip features
arcpy.analysis.Clip(mergedContours, projectBoundary, mergedContoursClipped)
print("file cliped")
