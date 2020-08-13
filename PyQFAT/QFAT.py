__author__ = 'sgao7'
import site
from sys import executable
from os import path
interpreter = executable
sitepkg = path.dirname(interpreter) + "\\site-packages"
print(sitepkg)
site.addsitedir(sitepkg)
import xml.etree.ElementTree
import numpy, mmap, os, sys, shutil, traceback, csv, gc, operator,math,time,shutil, pandas
import arcpy
from Tkinter import *
import tkFileDialog
from arcpy import env, mapping, Raster
from arcpy.sa import *
from functools import partial
from itertools import islice

import MESH2DEM, MESH2TIME
top = Tk()
top.title('Quantitative Flood Analysis Tool')
top.geometry("1400x800")
file_path = ""
folder=""
approott = os.path.dirname(os.path.abspath(sys.argv[0]))


def main():

  def QSAT():
    arcpy.AddMessage("-------------------------------------------")
    arcpy.AddMessage("     Quantitative Flood Analysis Tool      ")
    arcpy.AddMessage("                   SHU GAO                 ")
    arcpy.AddMessage("                   LSU CCR                 ")
    arcpy.AddMessage("-------------------------------------------")

    #Output Folder/Workspace
    inWorkspace =Entry.get(entry)

    #Input .14 File
    File14 = Entry.get(entry1)
    #Input Water Surface Elevation.63 File
    File63 = Entry.get(entry2)
    #Input Inundation time .63 File
    File63_time = Entry.get(entry3)


    #Input HUC_12 Polygon File
    inFeature = Entry.get(entry4)
    #Output Feature Name
    outFeature = Entry.get(entry5)
    #Cell Size (Option)
    Cell_size = Entry.get(entry6)

    xmin=Entry.get(entry7)
    ymin=Entry.get(entry8)
    xmax=Entry.get(entry9)
    ymax=Entry.get(entry10)
    UTMZone=Entry.get(entry11)
    perct = Entry.get(entry13)
    lower = Entry.get(entry12)
    File14_1 = inWorkspace+"\\"+"14copy"+".grd" #for calculating inun depth
    File63_1 = inWorkspace+"\\"+"63copy"+".63"

    File14_2 = inWorkspace+"\\"+"14copy_2"+".grd" #for calculating inun time
    File63_time_1 = inWorkspace+"\\"+"Time63copy"+".63"
    File63_2 = inWorkspace+"\\"+"63copy_2"+".63"


    CtrlTxt_Depth = inWorkspace +"\\"+"ctrl_depth"+".txt"
    CtrlTxt_WSE = inWorkspace +"\\"+"ctrl_WSE"+".txt"
    CtrlTxt_Time = inWorkspace +"\\"+"ctrl_Time"+".txt"
    RasDepth = "maxele_Output_inundation"
    RasWSE = "Output_WSE"
    RasTime = "Inun_Time"
    WSECtrl = inWorkspace+"/"+RasWSE
    DepthCtrl=inWorkspace+"/"+RasDepth
    TimeCtrl = inWorkspace+"/"+RasTime+"_"+lower+"_"+perct
    DepthRaster=inWorkspace+"\\"+RasDepth+".flt"
    WSERaster=inWorkspace+"\\"+RasWSE+".flt"
    TimeRaster = inWorkspace+"\\"+RasTime+"_"+lower+"_"+perct+".flt"

    Name14= File14.rsplit('/', 1)[-1]
    Name63= File63.rsplit('/', 1)[-1]

    Name14_1= File14_1.rsplit('\\', 1)[-1]
    Name63_1= File63_1.rsplit('\\', 1)[-1]

    Name14_2= File14_2.rsplit('\\', 1)[-1]
    Name63_Time = File63_time.rsplit('/', 1)[-1]
    Name63_2= File63_2.rsplit('\\', 1)[-1]

    File_Mesh = open(File14, "r+b")# Open .14/.grd file
    map = mmap.mmap(File_Mesh.fileno(), 0)
    map.readline()




    if(var2.get()==0 and var3.get()==0): #only calcuate WSE
        print var1.get()
        print var2.get()
        print var3.get()

        with open(CtrlTxt_WSE, 'w') as file:
              file.write("%s,%s\n" % (File14,File63))  # file name
              file.write("0\n")  # compute WSE
              file.write("%s\n" % WSECtrl)  # output raster name
              file.write("%s\n" % Cell_size)  # output raster resolution
              file.write("1\n")  # 1:geographic
              file.write("1\n")  # multiplication factor
              file.write("%s\n" %xmin)  # Longxmin
              file.write("%s\n" %ymin)  # Latymin
              file.write("%s\n" %xmax)  # Longxmax
              file.write("%s\n" %ymax)  # Latymax
              file.write("%s\n" %UTMZone)  # UTMZone
              file.write("2\n")  # 2:NAD83
              file.write("0\n")  # Raster Output Type
        MESH2DEM.grd2dem_call(CtrlTxt_WSE)
        arcpy.AddMessage("\nWSE RASTER DONE!")




        ignore="DATA"
        arcpy.env.workspace = inWorkspace
        arcpy.CheckOutExtension("spatial")# Check out a spatial analysis licence
        refInput = arcpy.Describe(WSERaster).spatialReference
        arcpy.env.overwriteOutput = True


        outPriFeature = inWorkspace + "\\" +"HUC_Prj" + ".shp"
        arcpy.Project_management(inFeature, outPriFeature, refInput)

        # Zonal Statistics as Table for Inun Time------------------------------------------------
        outWSE = ZonalStatisticsAsTable(outPriFeature, "OBJECTID", WSERaster, "meanSWETable" , ignore, "MEAN")
        arcpy.AddMessage("\nMEAN WATER SURFACE ELEVATION DONE!")



        # Join Fields-----------------------------  -------------------------------------------------
        arcpy.JoinField_management(outPriFeature, "OBJECTID", outWSE, "OBJECTID", "MEAN")


        # Writing shapefile
        #  List of fields to add
        fields = ["MeanWSE_m"]
        addfield = partial(
            arcpy.AddField_management,
            outPriFeature,
            field_type="FLOAT",
            field_precision="10",
            field_scale="5")
        for field in fields:
            addfield(field)


        arcpy.CalculateField_management(outPriFeature, "MeanWSE_m",'!MEAN!', "PYTHON_9.3")

        Keepfields = ["OBJECTID","MeanWSE_m"]
        fms = arcpy.FieldMappings()
        fields = arcpy.ListFields(outPriFeature)
        for field in fields:
            if field.name in Keepfields:
                fm = arcpy.FieldMap()
                fm.addInputField(outPriFeature, field.name)
                fms.addFieldMap(fm)
            else:
                pass
        arcpy.FeatureClassToFeatureClass_conversion(outPriFeature,inWorkspace,outFeature,field_mapping=fms)

        # Delete the fields in the raw feature data
        arcpy.DeleteField_management(outPriFeature,["MEAN","MeanWSE_m"])
        arcpy.AddMessage("\nPROGRAM FINISHED!")
    else:
        if (var1.get()==0 and var3.get()==0):#only inundation depth

            shutil.copyfile(File14, File14_1)
            shutil.copyfile(File63,File63_1)


            with open(CtrlTxt_Depth, 'w') as file:
              file.write("%s,%s\n" % (File14_1,File63_1))  # file name
              file.write("1\n")  # compute inundation depth
              file.write("%s\n" % DepthCtrl)  # output raster name
              file.write("%s\n" % Cell_size)  # output raster resolution
              file.write("1\n")  # 1:geographic
              file.write("1\n")  # multiplication factor
              file.write("%s\n" %xmin)  # Longxmin
              file.write("%s\n" %ymin)  # Latymin
              file.write("%s\n" %xmax)  # Longxmax
              file.write("%s\n" %ymax)  # Latymax
              file.write("%s\n" %UTMZone)  # UTMZone
              file.write("2\n")  # 2:NAD83
              file.write("0\n")  # Raster Output Type


            MESH2DEM.grd2dem_call(CtrlTxt_Depth)
            arcpy.AddMessage("\nINUNDATION WATER DEPTH RASTER DONE!")


            ignore="DATA"
            arcpy.env.workspace = inWorkspace
            arcpy.CheckOutExtension("spatial")# Check out a spatial analysis licence
            refInput = arcpy.Describe(DepthRaster).spatialReference
            arcpy.env.overwriteOutput = True


            outPriFeature = inWorkspace + "\\" +"HUC_Prj" + ".shp"
            arcpy.Project_management(inFeature, outPriFeature, refInput)
            # Zonal Statistics as Table for Water Depth------------------------------------------------


            # Zonal Statistics as Table for Land Elevation------------------------------------------------
            outDep = ZonalStatisticsAsTable(outPriFeature, "OBJECTID", DepthRaster, "meanDepthTable" , ignore, "MEAN")
            arcpy.AddMessage("\nMEAN INUNDATED DEPTH DONE!")



            #  Zonal Statistics as Table for Calculating Volume------------------------------------------------
            outVol = ZonalStatisticsAsTable(outPriFeature, "OBJECTID", DepthRaster, "totalVolmTable", ignore, "SUM")
            #  End of Zonal Statistics as Table---------------------------------------------------------
            arcpy.AddMessage("\nTOTAL VOLUME DONE!")

            # Join Fields-----------------------------  -------------------------------------------------
            arcpy.JoinField_management(outPriFeature,"OBJECTID", outDep ,"OBJECTID", "MEAN")
            arcpy.JoinField_management(outPriFeature, "OBJECTID", outDep, "OBJECTID", "AREA")
            arcpy.JoinField_management(outPriFeature, "OBJECTID", outVol, "OBJECTID", "SUM")


            # Writing shapefile
            #  List of fields to add
            fields = ["MeanDep_m","AREA_Km2", "Volume_Km3","Percent"]
            addfield = partial(
                arcpy.AddField_management,
                outPriFeature,
                field_type="FLOAT",
                field_precision="10",
                field_scale="5")
            for field in fields:
                addfield(field)

            arcpy.CalculateField_management(outPriFeature, "AREA_Km2",'!AREA!/1000000', "PYTHON_9.3")
            arcpy.CalculateField_management(outPriFeature, "MeanDep_m",'!MEAN!', "PYTHON_9.3")
            arcpy.CalculateField_management(outPriFeature, "Volume_Km3",'!SUM!', "PYTHON_9.3")
            arcpy.CalculateField_management(outPriFeature, "Percent",'((!AREA!/1000000)/!AreaSqKm!)*100', "PYTHON_9.3")


            #description = arcpy.Describe(outExtractDepth)
            #CellSize = description.children[0].meanCellHeight
            cursor = arcpy.UpdateCursor(outPriFeature)
            row = cursor.next()
            gridsize = float(Cell_size)
            while row:
                field1="Volume_Km3"
                row.setValue(field1, row.getValue(field1)*gridsize*gridsize/1000000000)
                cursor.updateRow(row)
                row = cursor.next()

            # End of adding fields

            # Feature to feature: Extracting "MeanWSE_m", "AREA_Km2", "MeanDep_m", "Volume" to new feature files
            # Setup field mappings
            Keepfields = ["OBJECTID",  "MeanDep_m", "AREA_Km2","Volume_Km3", "Percent" ]
            fms = arcpy.FieldMappings()
            fields = arcpy.ListFields(outPriFeature)
            for field in fields:
                if field.name in Keepfields:
                    fm = arcpy.FieldMap()
                    fm.addInputField(outPriFeature, field.name)
                    fms.addFieldMap(fm)
                else:
                    pass
            arcpy.FeatureClassToFeatureClass_conversion(outPriFeature,inWorkspace,outFeature,field_mapping=fms)

            # Delete the fields in the raw feature data
            arcpy.DeleteField_management(outPriFeature,["MEAN","AREA","SUM","PERCENTAGE",   "MeanDep_m","AREA_Km2", "Volume_Km3","Percent"])
            arcpy.AddMessage("\nPROGRAM FINISHED!")
        else:
            if(var1.get()==0 and var2.get()==0):#only calcuate inundation time
                File_Mesh = open(File14, "r+b")# Open .14/.grd file
                map = mmap.mmap(File_Mesh.fileno(), 0)
                map.readline()

                File_CSV = inWorkspace + "\\" + "MeshPts" + ".csv"# Name the CSV file
                f = open(File_CSV, 'wb') # Open the CSV file

                fTime = open(File63_time, "r+b")# Open .63 file
                fT = islice(fTime,3,None) # Skip the first three rows

                fDepth = open(File63, "r+b")# Open .63 file
                fD = islice(fDepth,3,None) # Skip the first three rows

                Num_Node = int(map.readline().split()[1])
                f.write("PT_ID,LONG,LAT,LandElev,Time\n") # Set five columns in the CSV file

                nLine = []
                #Write CSV File
                for i in fT:
                    tmp = i.split()
                    nLine = map.readline().split()
                    f.write(nLine[0] + "," + nLine[1] + "," + nLine[2] + ","+ nLine[3] + "," +tmp[1] + "\n")


                File_CSV2 = inWorkspace + "\\" + "MeshPts2" + ".csv"# Name the CSV file
                f2 = open(File_CSV2, 'wb') # Open the CSV file
                f2.write("ID,WSE\n")
                for j in fD:
                        WSE = j.split()
                        f2.write(WSE[0]+","+WSE[1] + "\n")


                map.close()
                File_Mesh.close()
                f.close()

                File_CSV_New = inWorkspace + "\\" + "MeshPtsNew" + ".csv"# Name the CSV file
                # Read the CSV file created above
                fNew =pandas.read_csv(File_CSV)

                fNew2 = pandas.read_csv(File_CSV2)

                Merge = pandas.merge( fNew, fNew2,left_on='PT_ID', right_on='ID')#merge according to Node1
                Merge=Merge.drop('ID', axis=1)


                Merge.columns= ['PT_ID','LONG','LAT','LandElev','Time','WSE']
                # Get the Inundation Water depth and create a new csv including water depth
                #LandElev = fNew['LandElev']*(-1)
                #Time =fNew['Time']
                #fNew['Time'] = Time
                #f.write(fNew['PT_ID']+"," + fNEW['LONG'] + "," + fNEW['LAT'] + ","+ fNew['LandElev'] + "," +fNEW2['Time'] +","+fNEW2["WSE"]+"\n")

                Merge = Merge[(Merge['LandElev']<0)&(Merge['WSE']> -99999)&(Merge['Time']>0)] #delete WSE=-99999, Time=0,LandElev>0
                perct=float(perct)
                lower=float(lower)
                maxvalue = numpy.percentile(Merge['Time'],perct)
                minvalue = numpy.percentile(Merge['Time'],lower)
                arcpy.AddMessage("\nMin inundation time is %s hours after removing the time lower than %s percent "%(minvalue, lower))
                arcpy.AddMessage("\nMax inundation time is %s hours after removing the time over %s percent "%(maxvalue, perct))

                with open(CtrlTxt_Time, 'w') as file:
                    file.write("%s,%s;%s\n" % (File14,File63,File63_time))  # file name
                    file.write("0\n")  # compute inundation depth
                    file.write("%s\n" % TimeCtrl)  # output raster name
                    file.write("%s\n" % Cell_size)  # output raster resolution
                    file.write("1\n")  # 1:geographic
                    file.write("1\n")  # multiplication factor
                    file.write("%s\n" %maxvalue)  # maxvalue
                    file.write("%s\n" %minvalue)  # maxvalue
                    file.write("%s\n" %xmin)  # Longxmin
                    file.write("%s\n" %ymin)  # Latymin
                    file.write("%s\n" %xmax)  # Longxmax
                    file.write("%s\n" %ymax)  # Latymax
                    file.write("%s\n" %UTMZone)  # UTMZone
                    file.write("2\n")  # 2:NAD83
                    file.write("0\n")  # Raster Output Type

                MESH2TIME.grd2dem_call(CtrlTxt_Time)
                arcpy.AddMessage("\nINUNDATION TIME RASTER DONE!")


                ignore="DATA"
                arcpy.env.workspace = inWorkspace
                arcpy.CheckOutExtension("spatial")# Check out a spatial analysis licence
                refInput = arcpy.Describe(TimeRaster).spatialReference
                arcpy.env.overwriteOutput = True


                outPriFeature = inWorkspace + "\\" +"HUC_Prj" + ".shp"
                arcpy.Project_management(inFeature, outPriFeature, refInput)

                # Zonal Statistics as Table for Inun Time------------------------------------------------
                outTime = ZonalStatisticsAsTable(outPriFeature, "OBJECTID", TimeRaster, "meanTimeTable" , ignore, "MEAN")
                arcpy.AddMessage("\nMEAN INUNDATION TIME DONE!!")



                # Join Fields-----------------------------  -------------------------------------------------
                arcpy.JoinField_management(outPriFeature, "OBJECTID", outTime, "OBJECTID", "MEAN")


                # Writing shapefile
                #  List of fields to add
                fields = ["InunTime_h"]
                addfield = partial(
                    arcpy.AddField_management,
                    outPriFeature,
                    field_type="FLOAT",
                    field_precision="10",
                    field_scale="5")
                for field in fields:
                    addfield(field)


                arcpy.CalculateField_management(outPriFeature, "InunTime_h",'!MEAN!', "PYTHON_9.3")

                Keepfields = ["OBJECTID","InunTime_h" ]
                fms = arcpy.FieldMappings()
                fields = arcpy.ListFields(outPriFeature)
                for field in fields:
                    if field.name in Keepfields:
                        fm = arcpy.FieldMap()
                        fm.addInputField(outPriFeature, field.name)
                        fms.addFieldMap(fm)
                    else:
                        pass
                arcpy.FeatureClassToFeatureClass_conversion(outPriFeature,inWorkspace,outFeature,field_mapping=fms)

                # Delete the fields in the raw feature data
                arcpy.DeleteField_management(outPriFeature,["MEAN","InunTime_h"])
                arcpy.AddMessage("\nPROGRAM FINISHED!")
            else:
                if(var1.get()==1and var2.get()==1and var3.get()==0):#calcuate WSE &Inundation depth
                    shutil.copyfile(File14, File14_1)
                    shutil.copyfile(File63,File63_1)
                    shutil.copyfile(File14,File14_2)
                    with open(CtrlTxt_WSE, 'w') as file:
                      file.write("%s,%s\n" % (File14,File63))  # file name
                      file.write("0\n")  # compute WSE
                      file.write("%s\n" % WSECtrl)  # output raster name
                      file.write("%s\n" % Cell_size)  # output raster resolution
                      file.write("1\n")  # 1:geographic
                      file.write("1\n")  # multiplication factor
                      file.write("%s\n" %xmin)  # Longxmin
                      file.write("%s\n" %ymin)  # Latymin
                      file.write("%s\n" %xmax)  # Longxmax
                      file.write("%s\n" %ymax)  # Latymax
                      file.write("%s\n" %UTMZone)  # UTMZone
                      file.write("2\n")  # 2:NAD83
                      file.write("0\n")  # Raster Output Type


                    with open(CtrlTxt_Depth, 'w') as file:
                      file.write("%s,%s\n" % (File14_1,File63_1))  # file name
                      file.write("1\n")  # compute inundation depth
                      file.write("%s\n" % DepthCtrl)  # output raster name
                      file.write("%s\n" % Cell_size)  # output raster resolution
                      file.write("1\n")  # 1:geographic
                      file.write("1\n")  # multiplication factor
                      file.write("%s\n" %xmin)  # Longxmin
                      file.write("%s\n" %ymin)  # Latymin
                      file.write("%s\n" %xmax)  # Longxmax
                      file.write("%s\n" %ymax)  # Latymax
                      file.write("%s\n" %UTMZone)  # UTMZone
                      file.write("2\n")  # 2:NAD83
                      file.write("0\n")  # Raster Output Type



                    MESH2DEM.grd2dem_call(CtrlTxt_WSE)
                    arcpy.AddMessage("\nWSE RASTER DONE!")
                    MESH2DEM.grd2dem_call(CtrlTxt_Depth)
                    arcpy.AddMessage("\nINUNDATION WATER DEPTH RASTER DONE!")


                    ignore="DATA"
                    arcpy.env.workspace = inWorkspace
                    arcpy.CheckOutExtension("spatial")# Check out a spatial analysis licence
                    refInput = arcpy.Describe(DepthRaster).spatialReference
                    arcpy.env.overwriteOutput = True


                    outPriFeature = inWorkspace + "\\" +"HUC_Prj" + ".shp"
                    arcpy.Project_management(inFeature, outPriFeature, refInput)
                    # Zonal Statistics as Table for Water Depth------------------------------------------------
                    outWSE = ZonalStatisticsAsTable(outPriFeature, "OBJECTID", WSERaster, "meanSWETable" , ignore, "MEAN")
                    arcpy.AddMessage("\nMEAN WATER SURFACE ELEVATION DONE!")


                    # Zonal Statistics as Table for Land Elevation------------------------------------------------
                    outDep = ZonalStatisticsAsTable(outPriFeature, "OBJECTID", DepthRaster, "meanDepthTable" , ignore, "MEAN")
                    arcpy.AddMessage("\nMEAN INUNDATED DEPTH DONE!")



                    #  Zonal Statistics as Table for Calculating Volume------------------------------------------------
                    outVol = ZonalStatisticsAsTable(outPriFeature, "OBJECTID", DepthRaster, "totalVolmTable", ignore, "SUM")
                    #  End of Zonal Statistics as Table---------------------------------------------------------
                    arcpy.AddMessage("\nTOTAL VOLUME DONE!")

                    # Join Fields-----------------------------  -------------------------------------------------
                    arcpy.JoinField_management(outPriFeature,"OBJECTID", outDep ,"OBJECTID", "MEAN")
                    arcpy.JoinField_management(outPriFeature, "OBJECTID", outWSE, "OBJECTID", "MEAN")
                    arcpy.JoinField_management(outPriFeature, "OBJECTID", outDep, "OBJECTID", "AREA")
                    arcpy.JoinField_management(outPriFeature, "OBJECTID", outVol, "OBJECTID", "SUM")


                    # Writing shapefile
                    #  List of fields to add
                    fields = ["MeanWSE_m","MeanDep_m","AREA_Km2", "Volume_Km3","Percent"]
                    addfield = partial(
                        arcpy.AddField_management,
                        outPriFeature,
                        field_type="FLOAT",
                        field_precision="10",
                        field_scale="5")
                    for field in fields:
                        addfield(field)

                    arcpy.CalculateField_management(outPriFeature, "MeanWSE_m",'!MEAN_1!', "PYTHON_9.3")
                    arcpy.CalculateField_management(outPriFeature, "AREA_Km2",'!AREA!/1000000', "PYTHON_9.3")
                    arcpy.CalculateField_management(outPriFeature, "MeanDep_m",'!MEAN!', "PYTHON_9.3")
                    arcpy.CalculateField_management(outPriFeature, "Volume_Km3",'!SUM!', "PYTHON_9.3")
                    arcpy.CalculateField_management(outPriFeature, "Percent",'((!AREA!/1000000)/!AreaSqKm!)*100', "PYTHON_9.3")


                    #description = arcpy.Describe(outExtractDepth)
                    #CellSize = description.children[0].meanCellHeight
                    cursor = arcpy.UpdateCursor(outPriFeature)
                    row = cursor.next()
                    gridsize = float(Cell_size)
                    while row:
                        field1="Volume_Km3"
                        row.setValue(field1, row.getValue(field1)*gridsize*gridsize/1000000000)
                        cursor.updateRow(row)
                        row = cursor.next()

                    # End of adding fields

                    # Feature to feature: Extracting "MeanWSE_m", "AREA_Km2", "MeanDep_m", "Volume" to new feature files
                    # Setup field mappings
                    Keepfields = ["OBJECTID",  "MeanWSE_m","MeanDep_m", "AREA_Km2","Volume_Km3", "Percent" ]
                    fms = arcpy.FieldMappings()
                    fields = arcpy.ListFields(outPriFeature)
                    for field in fields:
                        if field.name in Keepfields:
                            fm = arcpy.FieldMap()
                            fm.addInputField(outPriFeature, field.name)
                            fms.addFieldMap(fm)
                        else:
                            pass
                    arcpy.FeatureClassToFeatureClass_conversion(outPriFeature,inWorkspace,outFeature,field_mapping=fms)

                    # Delete the fields in the raw feature data
                    arcpy.DeleteField_management(outPriFeature,["MEAN", "MEAN_1","AREA","SUM","PERCENTAGE",   "MeanWSE_m", "MeanDep_m","AREA_Km2", "Volume_Km3","Percent"])
                    arcpy.AddMessage("\nPROGRAM FINISHED!")

                else:
                    if(var1.get()==1and var3.get()==1and var2.get()==0):#calcuate WSE &Inundation time
                        File_Mesh = open(File14, "r+b")# Open .14/.grd file
                        map = mmap.mmap(File_Mesh.fileno(), 0)
                        map.readline()

                        File_CSV = inWorkspace + "\\" + "MeshPts" + ".csv"# Name the CSV file
                        f = open(File_CSV, 'wb') # Open the CSV file

                        fTime = open(File63_time, "r+b")# Open .63 file
                        fT = islice(fTime,3,None) # Skip the first three rows

                        fDepth = open(File63, "r+b")# Open .63 file
                        fD = islice(fDepth,3,None) # Skip the first three rows

                        Num_Node = int(map.readline().split()[1])
                        f.write("PT_ID,LONG,LAT,LandElev,Time\n") # Set five columns in the CSV file

                        nLine = []
                        #Write CSV File
                        for i in fT:
                            tmp = i.split()
                            nLine = map.readline().split()
                            f.write(nLine[0] + "," + nLine[1] + "," + nLine[2] + ","+ nLine[3] + "," +tmp[1] + "\n")


                        File_CSV2 = inWorkspace + "\\" + "MeshPts2" + ".csv"# Name the CSV file
                        f2 = open(File_CSV2, 'wb') # Open the CSV file
                        f2.write("ID,WSE\n")
                        for j in fD:
                                WSE = j.split()
                                f2.write(WSE[0]+","+WSE[1] + "\n")


                        map.close()
                        File_Mesh.close()
                        f.close()

                        File_CSV_New = inWorkspace + "\\" + "MeshPtsNew" + ".csv"# Name the CSV file
                        # Read the CSV file created above
                        fNew =pandas.read_csv(File_CSV)

                        fNew2 = pandas.read_csv(File_CSV2)

                        Merge = pandas.merge( fNew, fNew2,left_on='PT_ID', right_on='ID')#merge according to Node1
                        Merge=Merge.drop('ID', axis=1)


                        Merge.columns= ['PT_ID','LONG','LAT','LandElev','Time','WSE']
                        # Get the Inundation Water depth and create a new csv including water depth
                        #LandElev = fNew['LandElev']*(-1)
                        #Time =fNew['Time']
                        #fNew['Time'] = Time
                        #f.write(fNew['PT_ID']+"," + fNEW['LONG'] + "," + fNEW['LAT'] + ","+ fNew['LandElev'] + "," +fNEW2['Time'] +","+fNEW2["WSE"]+"\n")

                        Merge = Merge[(Merge['LandElev']<0)&(Merge['WSE']> -99999)&(Merge['Time']>0)] #delete WSE=-99999, Time=0,LandElev>0
                        perct=float(perct)
                        lower=float(lower)
                        maxvalue = numpy.percentile(Merge['Time'],perct)
                        minvalue = numpy.percentile(Merge['Time'],lower)

                        arcpy.AddMessage("\nMin inundation time is %s hours after removing the time lower than %s percent "%(minvalue, lower))
                        arcpy.AddMessage("\nMax inundation time is %s hours after removing the time over %s percent "%(maxvalue, perct))

                        shutil.copyfile(File63,File63_2)
                        shutil.copyfile(File14, File14_1)


                        with open(CtrlTxt_WSE, 'w') as file:
                            file.write("%s,%s\n" % (File14_1,File63_2))  # file name
                            file.write("0\n")  # compute WSE
                            file.write("%s\n" % WSECtrl)  # output raster name
                            file.write("%s\n" % Cell_size)  # output raster resolution
                            file.write("1\n")  # 1:geographic
                            file.write("1\n")  # multiplication factor
                            file.write("%s\n" %xmin)  # Longxmin
                            file.write("%s\n" %ymin)  # Latymin
                            file.write("%s\n" %xmax)  # Longxmax
                            file.write("%s\n" %ymax)  # Latymax
                            file.write("%s\n" %UTMZone)  # UTMZone
                            file.write("2\n")  # 2:NAD83
                            file.write("0\n")  # Raster Output Type
                        with open(CtrlTxt_Time, 'w') as file:
                            file.write("%s,%s;%s\n" % (File14,File63,File63_time))  # file name
                            file.write("0\n")  # compute inundation depth
                            file.write("%s\n" % TimeCtrl)  # output raster name
                            file.write("%s\n" % Cell_size)  # output raster resolution
                            file.write("1\n")  # 1:geographic
                            file.write("1\n")  # multiplication factor
                            file.write("%s\n" %maxvalue)  # maxvalue
                            file.write("%s\n" %minvalue)  # maxvalue
                            file.write("%s\n" %xmin)  # Longxmin
                            file.write("%s\n" %ymin)  # Latymin
                            file.write("%s\n" %xmax)  # Longxmax
                            file.write("%s\n" %ymax)  # Latymax
                            file.write("%s\n" %UTMZone)  # UTMZone
                            file.write("2\n")  # 2:NAD83
                            file.write("0\n")  # Raster Output Type

                        MESH2DEM.grd2dem_call(CtrlTxt_WSE)
                        arcpy.AddMessage("\nWSE RASTER DONE!")
                        MESH2TIME.grd2dem_call(CtrlTxt_Time)
                        arcpy.AddMessage("\nINUNDATION TIME RASTER DONE!")
                        ignore="DATA"
                        arcpy.env.workspace = inWorkspace
                        arcpy.CheckOutExtension("spatial")# Check out a spatial analysis licence
                        refInput = arcpy.Describe(WSERaster).spatialReference
                        arcpy.env.overwriteOutput = True


                        outPriFeature = inWorkspace + "\\" +"HUC_Prj" + ".shp"
                        arcpy.Project_management(inFeature, outPriFeature, refInput)
                        # Zonal Statistics as Table for Water Depth------------------------------------------------
                        outWSE = ZonalStatisticsAsTable(outPriFeature, "OBJECTID", WSERaster, "meanSWETable" , ignore, "MEAN")
                        arcpy.AddMessage("\nMEAN WATER SURFACE ELEVATION DONE!")

                        # Zonal Statistics as Table for Inun Time------------------------------------------------
                        outTime = ZonalStatisticsAsTable(outPriFeature, "OBJECTID", TimeRaster, "meanTimeTable" , ignore, "MEAN")
                        arcpy.AddMessage("\nMEAN INUNDATION TIME DONE!")


                        arcpy.JoinField_management(outPriFeature, "OBJECTID", outWSE, "OBJECTID", "MEAN")
                        arcpy.JoinField_management(outPriFeature, "OBJECTID", outTime, "OBJECTID", "MEAN")


                        # Writing shapefile
                        #  List of fields to add
                        fields = ["MeanWSE_m","InunTime_h"]
                        addfield = partial(
                            arcpy.AddField_management,
                            outPriFeature,
                            field_type="FLOAT",
                            field_precision="10",
                            field_scale="5")
                        for field in fields:
                            addfield(field)

                        arcpy.CalculateField_management(outPriFeature, "MeanWSE_m",'!MEAN!', "PYTHON_9.3")
                        arcpy.CalculateField_management(outPriFeature, "InunTime_h",'!MEAN_1!', "PYTHON_9.3")



                        #  Feature to feature: Extracting "MeanWSE_m", "AREA_Km2", "MeanDep_m", "Volume" to new feature files
                        # Setup field mappings
                        Keepfields = ["OBJECTID",  "MeanWSE_m","InunTime_h" ]
                        fms = arcpy.FieldMappings()
                        fields = arcpy.ListFields(outPriFeature)
                        for field in fields:
                            if field.name in Keepfields:
                                fm = arcpy.FieldMap()
                                fm.addInputField(outPriFeature, field.name)
                                fms.addFieldMap(fm)
                            else:
                                pass
                        arcpy.FeatureClassToFeatureClass_conversion(outPriFeature,inWorkspace,outFeature,field_mapping=fms)

                        # Delete the fields in the raw feature data
                        arcpy.DeleteField_management(outPriFeature,["MEAN", "MEAN_1", "MeanWSE_m",  "InunTime_h"])
                        arcpy.AddMessage("\nPROGRAM FINISHED!")
                       # arcpy.AddMessage("\n After eliminating the time more than %s %, the max time is %s" %perct %maxvalue )
                    else:
                        if(var2.get()==1and var3.get()==1and var1.get()==0):#calcuate Inundation depth & time

                            File_Mesh = open(File14, "r+b")# Open .14/.grd file
                            map = mmap.mmap(File_Mesh.fileno(), 0)
                            map.readline()

                            File_CSV = inWorkspace + "\\" + "MeshPts" + ".csv"# Name the CSV file
                            f = open(File_CSV, 'wb') # Open the CSV file

                            fTime = open(File63_time, "r+b")# Open .63 file
                            fT = islice(fTime,3,None) # Skip the first three rows

                            fDepth = open(File63, "r+b")# Open .63 file
                            fD = islice(fDepth,3,None) # Skip the first three rows

                            Num_Node = int(map.readline().split()[1])
                            f.write("PT_ID,LONG,LAT,LandElev,Time\n") # Set five columns in the CSV file

                            nLine = []
                            #Write CSV File
                            for i in fT:
                                tmp = i.split()
                                nLine = map.readline().split()
                                f.write(nLine[0] + "," + nLine[1] + "," + nLine[2] + ","+ nLine[3] + "," +tmp[1] + "\n")


                            File_CSV2 = inWorkspace + "\\" + "MeshPts2" + ".csv"# Name the CSV file
                            f2 = open(File_CSV2, 'wb') # Open the CSV file
                            f2.write("ID,WSE\n")
                            for j in fD:
                                    WSE = j.split()
                                    f2.write(WSE[0]+","+WSE[1] + "\n")


                            map.close()
                            File_Mesh.close()
                            f.close()

                            File_CSV_New = inWorkspace + "\\" + "MeshPtsNew" + ".csv"# Name the CSV file
                            # Read the CSV file created above
                            fNew =pandas.read_csv(File_CSV)

                            fNew2 = pandas.read_csv(File_CSV2)

                            Merge = pandas.merge( fNew, fNew2,left_on='PT_ID', right_on='ID')#merge according to Node1
                            Merge=Merge.drop('ID', axis=1)


                            Merge.columns= ['PT_ID','LONG','LAT','LandElev','Time','WSE']
                            # Get the Inundation Water depth and create a new csv including water depth
                            #LandElev = fNew['LandElev']*(-1)
                            #Time =fNew['Time']
                            #fNew['Time'] = Time
                            #f.write(fNew['PT_ID']+"," + fNEW['LONG'] + "," + fNEW['LAT'] + ","+ fNew['LandElev'] + "," +fNEW2['Time'] +","+fNEW2["WSE"]+"\n")

                            Merge = Merge[(Merge['LandElev']<0)&(Merge['WSE']> -99999)&(Merge['Time']>0)] #delete WSE=-99999, Time=0,LandElev>0
                            perct=float(perct)
                            lower=float(lower)
                            maxvalue = numpy.percentile(Merge['Time'],perct)
                            minvalue = numpy.percentile(Merge['Time'],lower)
                            arcpy.AddMessage("\nMin inundation time is %s hours after removing the time lower than %s percent "%(minvalue, lower))
                            arcpy.AddMessage("\nMax inundation time is %s hours after removing the time over %s percent "%(maxvalue, perct))
                            shutil.copyfile(File14, File14_1)
                            shutil.copyfile(File63,File63_1)
                            shutil.copyfile(File14,File14_2)



                            with open(CtrlTxt_Depth, 'w') as file:
                              file.write("%s,%s\n" % (File14_1,File63_1))  # file name
                              file.write("1\n")  # compute inundation depth
                              file.write("%s\n" % DepthCtrl)  # output raster name
                              file.write("%s\n" % Cell_size)  # output raster resolution
                              file.write("1\n")  # 1:geographic
                              file.write("1\n")  # multiplication factor
                              file.write("%s\n" %xmin)  # Longxmin
                              file.write("%s\n" %ymin)  # Latymin
                              file.write("%s\n" %xmax)  # Longxmax
                              file.write("%s\n" %ymax)  # Latymax
                              file.write("%s\n" %UTMZone)  # UTMZone
                              file.write("2\n")  # 2:NAD83
                              file.write("0\n")  # Raster Output Type

                            with open(CtrlTxt_Time, 'w') as file:
                                file.write("%s,%s;%s\n" % (File14,File63,File63_time))  # file name
                                file.write("0\n")  # compute inundation depth
                                file.write("%s\n" % TimeCtrl)  # output raster name
                                file.write("%s\n" % Cell_size)  # output raster resolution
                                file.write("1\n")  # 1:geographic
                                file.write("1\n")  # multiplication factor
                                file.write("%s\n" %maxvalue)  # maxvalue
                                file.write("%s\n" %minvalue)  # maxvalue
                                file.write("%s\n" %xmin)  # Longxmin
                                file.write("%s\n" %ymin)  # Latymin
                                file.write("%s\n" %xmax)  # Longxmax
                                file.write("%s\n" %ymax)  # Latymax
                                file.write("%s\n" %UTMZone)  # UTMZone
                                file.write("2\n")  # 2:NAD83
                                file.write("0\n")  # Raster Output Type

                            MESH2TIME.grd2dem_call(CtrlTxt_Time)
                            arcpy.AddMessage("\nINUNDATION TIME RASTER DONE!")
                            MESH2DEM.grd2dem_call(CtrlTxt_Depth)
                            arcpy.AddMessage("\nINUNDATION WATER DEPTH RASTER DONE!")


                            ignore="DATA"
                            arcpy.env.workspace = inWorkspace
                            arcpy.CheckOutExtension("spatial")# Check out a spatial analysis licence
                            refInput = arcpy.Describe(DepthRaster).spatialReference
                            arcpy.env.overwriteOutput = True


                            outPriFeature = inWorkspace + "\\" +"HUC_Prj" + ".shp"
                            arcpy.Project_management(inFeature, outPriFeature, refInput)


                            # Zonal Statistics as Table for Land Elevation------------------------------------------------
                            outDep = ZonalStatisticsAsTable(outPriFeature, "OBJECTID", DepthRaster, "meanDepthTable" , ignore, "MEAN")
                            arcpy.AddMessage("\nMEAN INUNDATED DEPTH DONE!")

                            # Zonal Statistics as Table for Inun Time------------------------------------------------
                            outTime = ZonalStatisticsAsTable(outPriFeature, "OBJECTID", TimeRaster, "meanTimeTable" , ignore, "MEAN")
                            arcpy.AddMessage("\nMEAN INUNDATION TIME DONE!")

                            #  Zonal Statistics as Table for Calculating Volume------------------------------------------------
                            outVol = ZonalStatisticsAsTable(outPriFeature, "OBJECTID", DepthRaster, "totalVolmTable", ignore, "SUM")
                            #  End of Zonal Statistics as Table---------------------------------------------------------
                            arcpy.AddMessage("\nTOTAL VOLUME DONE!")

                            # Join Fields-----------------------------  -------------------------------------------------
                            arcpy.JoinField_management(outPriFeature,"OBJECTID", outDep ,"OBJECTID", "MEAN")
                            arcpy.JoinField_management(outPriFeature, "OBJECTID", outTime, "OBJECTID", "MEAN")
                            arcpy.JoinField_management(outPriFeature, "OBJECTID", outDep, "OBJECTID", "AREA")
                            arcpy.JoinField_management(outPriFeature, "OBJECTID", outVol, "OBJECTID", "SUM")


                            # Writing shapefile
                            #  List of fields to add
                            fields = ["MeanDep_m","AREA_Km2", "Volume_Km3","Percent", "InunTime_h"]
                            addfield = partial(
                                arcpy.AddField_management,
                                outPriFeature,
                                field_type="FLOAT",
                                field_precision="10",
                                field_scale="5")
                            for field in fields:
                                addfield(field)


                            arcpy.CalculateField_management(outPriFeature, "AREA_Km2",'!AREA!/1000000', "PYTHON_9.3")
                            arcpy.CalculateField_management(outPriFeature, "MeanDep_m",'!MEAN!', "PYTHON_9.3")
                            arcpy.CalculateField_management(outPriFeature, "Volume_Km3",'!SUM!', "PYTHON_9.3")
                            arcpy.CalculateField_management(outPriFeature, "Percent",'((!AREA!/1000000)/!AreaSqKm!)*100', "PYTHON_9.3")
                            arcpy.CalculateField_management(outPriFeature, "InunTime_h",'!MEAN_1!', "PYTHON_9.3")

                            #description = arcpy.Describe(outExtractDepth)
                            #CellSize = description.children[0].meanCellHeight
                            cursor = arcpy.UpdateCursor(outPriFeature)
                            row = cursor.next()
                            gridsize = float(Cell_size)
                            while row:
                                field1="Volume_Km3"
                                row.setValue(field1, row.getValue(field1)*gridsize*gridsize/1000000000)
                                cursor.updateRow(row)
                                row = cursor.next()

                            # End of adding fields

                            #  Feature to feature: Extracting "MeanWSE_m", "AREA_Km2", "MeanDep_m", "Volume" to new feature files
                            # Setup field mappings
                            Keepfields = ["OBJECTID",  "MeanDep_m", "AREA_Km2","Volume_Km3", "Percent","InunTime_h" ]
                            fms = arcpy.FieldMappings()
                            fields = arcpy.ListFields(outPriFeature)
                            for field in fields:
                               if field.name in Keepfields:
                                    fm = arcpy.FieldMap()
                                    fm.addInputField(outPriFeature, field.name)
                                    fms.addFieldMap(fm)
                               else:
                                    pass
                            arcpy.FeatureClassToFeatureClass_conversion(outPriFeature,inWorkspace,outFeature,field_mapping=fms)

                            # Delete the fields in the raw feature data
                            arcpy.DeleteField_management(outPriFeature,["MEAN", "MEAN_1","AREA","SUM","PERCENTAGE", "MeanDep_m","AREA_Km2", "Volume_Km3","Percent", "InunTime_h"])
                            arcpy.AddMessage("\nPROGRAM FINISHED!")
                            # arcpy.AddMessage("\n After eliminating the time more than %s %, the max time is %s" %perct %maxvalue )
                        else:
                             if(var1.get()==1 and var2.get()==1and var3.get()==1):
                                 File_Mesh = open(File14, "r+b")# Open .14/.grd file
                                 map = mmap.mmap(File_Mesh.fileno(), 0)
                                 map.readline()

                                 File_CSV = inWorkspace + "\\" + "MeshPts" + ".csv"# Name the CSV file
                                 f = open(File_CSV, 'wb') # Open the CSV file

                                 fTime = open(File63_time, "r+b")# Open .63 file
                                 fT = islice(fTime,3,None) # Skip the first three rows

                                 fDepth = open(File63, "r+b")# Open .63 file
                                 fD = islice(fDepth,3,None) # Skip the first three rows

                                 Num_Node = int(map.readline().split()[1])
                                 f.write("PT_ID,LONG,LAT,LandElev,Time\n") # Set five columns in the CSV file

                                 nLine = []
                                 #Write CSV File
                                 for i in fT:
                                     tmp = i.split()
                                     nLine = map.readline().split()
                                     f.write(nLine[0] + "," + nLine[1] + "," + nLine[2] + ","+ nLine[3] + "," +tmp[1] + "\n")


                                 File_CSV2 = inWorkspace + "\\" + "MeshPts2" + ".csv"# Name the CSV file
                                 f2 = open(File_CSV2, 'wb') # Open the CSV file
                                 f2.write("ID,WSE\n")
                                 for j in fD:
                                         WSE = j.split()
                                         f2.write(WSE[0]+","+WSE[1] + "\n")


                                 map.close()
                                 File_Mesh.close()
                                 f.close()

                                 File_CSV_New = inWorkspace + "\\" + "MeshPtsNew" + ".csv"# Name the CSV file
                                 # Read the CSV file created above
                                 fNew =pandas.read_csv(File_CSV)

                                 fNew2 = pandas.read_csv(File_CSV2)

                                 Merge = pandas.merge( fNew, fNew2,left_on='PT_ID', right_on='ID')#merge according to Node1
                                 Merge=Merge.drop('ID', axis=1)


                                 Merge.columns= ['PT_ID','LONG','LAT','LandElev','Time','WSE']
                                 # Get the Inundation Water depth and create a new csv including water depth
                                 #LandElev = fNew['LandElev']*(-1)
                                 #Time =fNew['Time']
                                 #fNew['Time'] = Time
                                 #f.write(fNew['PT_ID']+"," + fNEW['LONG'] + "," + fNEW['LAT'] + ","+ fNew['LandElev'] + "," +fNEW2['Time'] +","+fNEW2["WSE"]+"\n")

                                 Merge = Merge[(Merge['LandElev']<0)&(Merge['WSE']> -99999)&(Merge['Time']>0)] #delete WSE=-99999, Time=0,LandElev>0
                                 perct=float(perct)
                                 lower=float(lower)
                                 maxvalue = numpy.percentile(Merge['Time'],perct)
                                 minvalue = numpy.percentile(Merge['Time'],lower)
                                 arcpy.AddMessage("\nMin inundation time is %s hours after removing the time lower than %s percent "%(minvalue, lower))
                                 arcpy.AddMessage("\nMax inundation time is %s hours after removing the time over %s percent "%(maxvalue, perct))

                                 shutil.copyfile(File14, File14_1)
                                 shutil.copyfile(File63,File63_1)
                                 shutil.copyfile(File63,File63_2)
                                 shutil.copyfile(File14,File14_2)

                                 with open(CtrlTxt_WSE, 'w') as file:
                                   file.write("%s,%s\n" % (File14,File63_2))  # file name
                                   file.write("0\n")  # compute WSE
                                   file.write("%s\n" % WSECtrl)  # output raster name
                                   file.write("%s\n" % Cell_size)  # output raster resolution
                                   file.write("1\n")  # 1:geographic
                                   file.write("1\n")  # multiplication factor
                                   file.write("%s\n" %xmin)  # Longxmin
                                   file.write("%s\n" %ymin)  # Latymin
                                   file.write("%s\n" %xmax)  # Longxmax
                                   file.write("%s\n" %ymax)  # Latymax
                                   file.write("%s\n" %UTMZone)  # UTMZone
                                   file.write("2\n")  # 2:NAD83
                                   file.write("0\n")  # Raster Output Type


                                 with open(CtrlTxt_Depth, 'w') as file:
                                   file.write("%s,%s\n" % (File14_1,File63_1))  # file name
                                   file.write("1\n")  # compute inundation depth
                                   file.write("%s\n" % DepthCtrl)  # output raster name
                                   file.write("%s\n" % Cell_size)  # output raster resolution
                                   file.write("1\n")  # 1:geographic
                                   file.write("1\n")  # multiplication factor
                                   file.write("%s\n" %xmin)  # Longxmin
                                   file.write("%s\n" %ymin)  # Latymin
                                   file.write("%s\n" %xmax)  # Longxmax
                                   file.write("%s\n" %ymax)  # Latymax
                                   file.write("%s\n" %UTMZone)  # UTMZone
                                   file.write("2\n")  # 2:NAD83
                                   file.write("0\n")  # Raster Output Type

                                 with open(CtrlTxt_Time, 'w') as file:
                                      file.write("%s,%s;%s\n" % (File14_2,File63,File63_time))  # file name
                                      file.write("0\n")  # compute inundation depth
                                      file.write("%s\n" % TimeCtrl)  # output raster name
                                      file.write("%s\n" % Cell_size)  # output raster resolution
                                      file.write("1\n")  # 1:geographic
                                      file.write("1\n")  # multiplication factor
                                      file.write("%s\n" %maxvalue)  # maxvalue
                                      file.write("%s\n" %minvalue)  # maxvalue
                                      file.write("%s\n" %xmin)  # Longxmin
                                      file.write("%s\n" %ymin)  # Latymin
                                      file.write("%s\n" %xmax)  # Longxmax
                                      file.write("%s\n" %ymax)  # Latymax
                                      file.write("%s\n" %UTMZone)  # UTMZone
                                      file.write("2\n")  # 2:NAD83
                                      file.write("0\n")  # Raster Output Type

                                 MESH2TIME.grd2dem_call(CtrlTxt_Time)
                                 arcpy.AddMessage("\nINUNDATION TIME RASTER DONE!")
                                 MESH2DEM.grd2dem_call(CtrlTxt_WSE)
                                 arcpy.AddMessage("\nWSE RASTER DONE!")
                                 MESH2DEM.grd2dem_call(CtrlTxt_Depth)
                                 arcpy.AddMessage("\nINUNDATION WATER DEPTH RASTER DONE!")


                                 ignore="DATA"
                                 arcpy.env.workspace = inWorkspace
                                 arcpy.CheckOutExtension("spatial")# Check out a spatial analysis licence
                                 refInput = arcpy.Describe(DepthRaster).spatialReference
                                 arcpy.env.overwriteOutput = True


                                 outPriFeature = inWorkspace + "\\" +"HUC_Prj" + ".shp"
                                 arcpy.Project_management(inFeature, outPriFeature, refInput)
                                 # Zonal Statistics as Table for Water Depth------------------------------------------------
                                 outWSE = ZonalStatisticsAsTable(outPriFeature, "OBJECTID", WSERaster, "meanSWETable" , ignore, "MEAN")
                                 arcpy.AddMessage("\nMEAN WATER SURFACE ELEVATION DONE!")


                                 # Zonal Statistics as Table for Land Elevation------------------------------------------------
                                 outDep = ZonalStatisticsAsTable(outPriFeature, "OBJECTID", DepthRaster, "meanDepthTable" , ignore, "MEAN")
                                 arcpy.AddMessage("\nMEAN INUNDATED DEPTH DONE!")

                                 # Zonal Statistics as Table for Inun Time------------------------------------------------
                                 outTime = ZonalStatisticsAsTable(outPriFeature, "OBJECTID", TimeRaster, "meanTimeTable" , ignore, "MEAN")
                                 arcpy.AddMessage("\nMEAN INUNDATION TIME DONE!")

                                 #  Zonal Statistics as Table for Calculating Volume------------------------------------------------
                                 outVol = ZonalStatisticsAsTable(outPriFeature, "OBJECTID", DepthRaster, "totalVolmTable", ignore, "SUM")
                                 #  End of Zonal Statistics as Table---------------------------------------------------------
                                 arcpy.AddMessage("\nTOTAL VOLUME DONE!")

                                 # Join Fields-----------------------------  -------------------------------------------------
                                 arcpy.JoinField_management(outPriFeature,"OBJECTID", outDep ,"OBJECTID", "MEAN")
                                 arcpy.JoinField_management(outPriFeature, "OBJECTID", outWSE, "OBJECTID", "MEAN")
                                 arcpy.JoinField_management(outPriFeature, "OBJECTID", outTime, "OBJECTID", "MEAN")
                                 arcpy.JoinField_management(outPriFeature, "OBJECTID", outDep, "OBJECTID", "AREA")
                                 arcpy.JoinField_management(outPriFeature, "OBJECTID", outVol, "OBJECTID", "SUM")


                                 # Writing shapefile
                                 #  List of fields to add
                                 fields = ["MeanWSE_m","MeanDep_m","AREA_Km2", "Volume_Km3","Percent", "InunTime_h"]
                                 addfield = partial(
                                     arcpy.AddField_management,
                                     outPriFeature,
                                     field_type="FLOAT",
                                     field_precision="10",
                                     field_scale="5")
                                 for field in fields:
                                     addfield(field)

                                 arcpy.CalculateField_management(outPriFeature, "MeanWSE_m",'!MEAN_1!', "PYTHON_9.3")
                                 arcpy.CalculateField_management(outPriFeature, "AREA_Km2",'!AREA!/1000000', "PYTHON_9.3")
                                 arcpy.CalculateField_management(outPriFeature, "MeanDep_m",'!MEAN!', "PYTHON_9.3")
                                 arcpy.CalculateField_management(outPriFeature, "Volume_Km3",'!SUM!', "PYTHON_9.3")
                                 arcpy.CalculateField_management(outPriFeature, "Percent",'((!AREA!/1000000)/!AreaSqKm!)*100', "PYTHON_9.3")
                                 arcpy.CalculateField_management(outPriFeature, "InunTime_h",'!MEAN_12!', "PYTHON_9.3")

                                 #description = arcpy.Describe(outExtractDepth)
                                 #CellSize = description.children[0].meanCellHeight
                                 cursor = arcpy.UpdateCursor(outPriFeature)
                                 row = cursor.next()
                                 gridsize = float(Cell_size)
                                 while row:
                                     field1="Volume_Km3"
                                     row.setValue(field1, row.getValue(field1)*gridsize*gridsize/1000000000)
                                     cursor.updateRow(row)
                                     row = cursor.next()

                                 # End of adding fields

                                 #  Feature to feature: Extracting "MeanWSE_m", "AREA_Km2", "MeanDep_m", "Volume" to new feature files
                                 # Setup field mappings
                                 Keepfields = ["OBJECTID",  "MeanWSE_m","MeanDep_m", "AREA_Km2","Volume_Km3", "Percent","InunTime_h" ]
                                 fms = arcpy.FieldMappings()
                                 fields = arcpy.ListFields(outPriFeature)
                                 for field in fields:
                                     if field.name in Keepfields:
                                         fm = arcpy.FieldMap()
                                         fm.addInputField(outPriFeature, field.name)
                                         fms.addFieldMap(fm)
                                     else:
                                         pass
                                 arcpy.FeatureClassToFeatureClass_conversion(outPriFeature,inWorkspace,outFeature,field_mapping=fms)

                                 # Delete the fields in the raw feature data
                                 arcpy.DeleteField_management(outPriFeature,["MEAN", "MEAN_1","AREA","SUM","PERCENTAGE", "MeanWSE_m", "MeanDep_m","AREA_Km2", "Volume_Km3","Percent", "InunTime_h"])
                                 arcpy.AddMessage("\nPROGRAM FINISHED!")





  def open_folder():

     filename = tkFileDialog.askdirectory()
     entry.delete(0, END)
     entry.insert(0, filename)
     return filename

  def open_file1():

     filename = tkFileDialog.askopenfilename()
     infile = open(filename, 'r')
     content = infile.read()
     entry1.delete(0, END)
     entry1.insert(0, filename)
     return filename

  def open_file2():

     filename = tkFileDialog.askopenfilename()
     infile = open(filename, 'r')
     content = infile.read()
     entry2.delete(0, END)
     entry2.insert(0, filename)
     return filename

  def open_file3():

     filename = tkFileDialog.askopenfilename()
     infile = open(filename, 'r')
     content = infile.read()
     entry3.delete(0, END)
     entry3.insert(0, filename)
     return filename

  def open_file4():

     filename = tkFileDialog.askopenfilename()
     infile = open(filename, 'r')
     content = infile.read()
     entry4.delete(0, END)
     entry4.insert(0, filename)
     return filename

  def checkbotton_value1(): #only WSE
      if (var1.get()):
          var2.set(0)
          var3.set(0)


  def checkbotton_value2():#only Inundation Depth
      if (var2.get()):
          var1.set(0)
          var3.set(0)


  def checkbotton_value3():#only Inundation Time
      if (var3.get()):
          var1.set(0)
          var2.set(0)


  def checkbotton_value4(): # WSE &Inundation Depth
      if (var1.get() & var2.get()):
          var3.set(1)

  def checkbotton_value5(): # wse & Inundation time
      if (var1.get() & var3.get()):
          var2.set(1)

  def checkbotton_value6():
      if (var2.get() & var3.get()): # Inundation depth & time
          var1.set(1)

  def checkbotton_value7():
      if (var1.get()&var2.get() & var3.get()): # ALL
          var1.set(2)





  #background_image=PhotoImage(file = "C:/Users/sgao7/Desktop/manual/background.gif")
  #background_label = Label(top, image=background_image)
  #background_label.place(x=0, y=0, relwidth=1, relheight=1)


  icon_dir = approott+"\\"+"icon_open"+".gif"
  icon_open = PhotoImage(file=icon_dir)
  icon_open = icon_open.subsample(1,1)

  Label(top,text="        ").grid(row=0, column=0, sticky='e')

  Label(top,text="Output Folder").grid(row=1, column=1, sticky='w')
  entry=Entry(top,textvariable=file_path, width=80)
  entry.grid(row=1,column=2,padx=20,pady=10,sticky='we',columnspan=10)
  Button(top,text="Open",image=icon_open, command = open_folder).grid(row=1,column=15,sticky='ew',padx=2,pady=2)

  Label(top, text="Element Mesh (.grd)").grid(row=2, column=1, sticky='w')
  entry1=Entry(top,textvariable=file_path)
  entry1.grid(row=2,column=2,padx=20,pady=10,sticky='we',columnspan=10)
  Button(top,text="Open",image=icon_open,command=open_file1).grid(row=2,column=15,sticky='ew',padx=2)

  Label(top, text="Water Surface Elevation").grid(row=3, column=1, sticky='w')
  entry2=Entry(top,textvariable=file_path)
  entry2.grid(row=3,column=2,padx=20,pady=10,sticky='we',columnspan=10)
  Button(top,text="Open",image=icon_open,command=open_file2).grid(row=3,column=15,sticky='ew',padx=2)

  Label(top, text="Inundation Time (Option)").grid(row=4, column=1, sticky='w')
  entry3=Entry(top,textvariable=file_path)
  entry3.grid(row=4,column=2,padx=20,pady=10,sticky='we',columnspan=10)
  Button(top,text="Open",image=icon_open,command=open_file3).grid(row=4,column=15,sticky='ew',padx=2)



  Label(top, text="Input Polygon File (.shp)").grid(row=5, column=1, sticky='w')
  entry4=Entry(top,textvariable=file_path)
  entry4.grid(row=5,column=2,padx=20,pady=10,sticky='we',columnspan=10)
  Button(top,text="Open",image=icon_open,command=open_file4).grid(row=5,column=15,sticky='ew',padx=2)

  Label(top, text="Output Feature Name").grid(row=6, column=1, sticky='w')
  entry5=Entry(top, width =20)
  entry5.grid(row=6,column=2,padx=20,pady=10,sticky='we',columnspan=10)

  Label(top, text="Cell Size (m)").grid(row=7, column=1, sticky='w')
  entry6=Entry(top, width =10)
  entry6.grid(row=7,column=2,padx=20,pady=10,sticky='we',columnspan=1)

  Label(top, width=10,text="XMIN").grid(row=9, column=4, sticky='e')
  entry7=Entry(top, width =15)
  entry7.grid(row=9,column=5,padx=2,pady=2,sticky='w',columnspan=1)

  Label(top, text="YMIN").grid(row=11, column=6, sticky='we')
  entry8=Entry(top, width =15)
  entry8.grid(row=10,column=6,padx=2,pady=1,sticky='we',columnspan=1)

  Label(top, text="XMAX").grid(row=9, column=8, sticky='w')
  entry9=Entry(top, width =15)
  entry9.grid(row=9,column=7,padx=2,pady=2,sticky='w',columnspan=1)

  Label(top, text="YMAX").grid(row=7, column=6, sticky='we')
  entry10=Entry(top, width =15)
  entry10.grid(row=8,column=6,padx=2,pady=2,sticky='w',columnspan=1)

  Label(top, text="UTMZone").grid(row=10, column=1, sticky='w')
  entry11=Entry(top, width =10)
  entry11.grid(row=10,column=2,padx=20,pady=10,sticky='we',columnspan=1)


  Label(top, text="Inundation Time Range (%)").grid(row=12, column=1, sticky='w', rowspan=3)

  Label(top, text="Lower").grid(row=12, column=2, sticky='we',columnspan=1)
  Label(top, text="Upper").grid(row=12, column=8, sticky='w')





  entry12=Entry(top, width =5)
  entry12.grid(row=12,column=3,padx=2,pady=1,sticky='w',columnspan=2)

  entry13=Entry(top, width =5)
  entry13.grid(row=12,column=7,padx=20,pady=10,sticky='e',columnspan=1)




  Label(top,text="                                                                          ").grid(row=18, column=10, sticky='e')
  photo_dir1= approott+"\\"+"ccr"+".gif"
  photo1 = PhotoImage(file=photo_dir1)
  photo1 = photo1.subsample(8,8)
  panel1=Label(top, image=photo1)
  panel1.grid(row=18, column=10, sticky='e')


  photo_dir2 = approott+"\\"+"scale"+".gif"
  photo2 = PhotoImage(file=photo_dir2)
  photo2 = photo2.subsample(1,1)
  panel2=Label(top, image=photo2)
  panel2.grid(row=13, column=2, sticky='w', columnspan=10)

  Button(top,text="OK", command=QSAT, width=20, compound=LEFT).grid(row=18,column=1,sticky='ew',padx=2)

  var1 = IntVar()
  Checkbutton(top, text="WSE", variable=var1).grid(row=16, column=1, sticky='e' )

  var2 = IntVar()
  Checkbutton(top, text="Inundation Depth", variable=var2).grid(row=16,column=2,sticky='w' )

  var3 = IntVar()
  Checkbutton(top, text="Inundation Time", variable=var3).grid(row=16,column=3,sticky='w' )


  top.mainloop()
if __name__ == "__main__":
    print ('Start Processing ...')
main()
raw_input("Enter enter key to exit...")
