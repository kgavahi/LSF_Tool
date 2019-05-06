##############################################################################################
#                                          LSF-tool                                          #
##                                     By Kayhan Gavahi                                     ##
###                                Last Update : 05/03/2019                                ###
##############################################################################################
import arcpy
from arcpy.sa import *
import shutil

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Toolbox"
        self.alias = ""

        # List of tool classes associated with this toolbox
        self.tools = [LSF_tool]


class LSF_tool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "LSF-tool"
        self.description = "LS factor calculation considering soil deposition and channel network"
        self.canRunInBackground = False

    def getParameterInfo(self):
		"""Define parameter definitions"""
		param0 = arcpy.Parameter()
		param0.name="Input DEM raster file"
		param0.displayName="Input DEM raster file:"
		param0.parameterType="Required"
		param0.direction="Input"
		param0.datatype= "Raster Layer"
		
		param1 = arcpy.Parameter()
		param1.name="Input Slope Decrease Threshold"
		param1.displayName="Input Slope Decrease Threshold"
		param1.parameterType="Required"
		param1.direction="Input"
		param1.datatype= "Double"
		
		param2 = arcpy.Parameter()
		param2.name="Input Flow Accumulation Threshold for Channel Network"
		param2.displayName="Input Flow Accumulation Threshold for Channel Network"
		param2.parameterType="Required"
		param2.direction="Input"
		param2.datatype= "Long"  
		
		param3 = arcpy.Parameter()
		param3.name="Output Corrected Flow Accumulation grid"
		param3.displayName="Output Corrected Flow Accumulation grid"
		param3.direction="Output"
		param3.datatype= "Raster Layer"
		
		param4 = arcpy.Parameter()
		param4.name="Output LS Factor grid"
		param4.displayName="Output LS Factor grid"
		param4.direction="Output"
		param4.datatype= "Raster Layer"  
		return [param0, param1, param2, param3, param4]

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
		
        #Check out the ArcGIS Spatial Analyst extension license
        arcpy.CheckOutExtension("Spatial")
		
        input_DEM             =  parameters[0].valueAsText
        input_slope_threshold =  parameters[1].valueAsText
        input_f_acc_threshold =  parameters[2].valueAsText
        output_f_acc_cor      =  parameters[3].valueAsText
        output_LS             =  parameters[4].valueAsText

        messages.addMessage("Input DEM raster file = "                                 + input_DEM)
        messages.addMessage("Input Slope Decrease Threshold = "                        + input_slope_threshold)
        messages.addMessage("Input Flow Accumulation Threshold for Channel Network = " + input_f_acc_threshold)
		
        import os
        path = arcpy.Describe(input_DEM).path + '\\temp_LSF_Tool'
        exists = os.path.isdir(path)
        if  not exists:
			os.mkdir(path)
        else:
            shutil.rmtree(path, ignore_errors=True, onerror=None)
            os.mkdir(path)

		# Process: Slope
        messages.addMessage("Process: Slope ... ")       
        slope = Slope(input_DEM, "DEGREE", "","","")

		# Process: Fill
        messages.addMessage("Process: Fill ... ")
        fill = Fill(input_DEM, "")
		
		# Process: Flow Direction
        messages.addMessage("Process: Flow Direction ... ")
        f_dir = FlowDirection(fill, "NORMAL", "","D8")
		
		# Process: Flow Accumulation
        messages.addMessage("Process: Flow Accumulation ... ")
        f_acc = FlowAccumulation(f_dir)
		
		# Process: Get Raster Properties
        CellSize_pos = str(arcpy.GetRasterProperties_management(input_DEM, "CELLSIZEX", ""))
        CellSize_neg = str(float(CellSize_pos) * (-1))
        
		# Process: Shift 1
        messages.addMessage("Process: Shift DEM in Direction 1 ... ")
        name = 'shift_1'
        shift_1 = os.path.join(path,name)
        arcpy.Shift_management(input_DEM, shift_1, CellSize_pos, "0", "")
        
		# Process: Shift 2
        messages.addMessage("Process: Shift DEM in Direction 2 ... ")		
        name = 'shift_2'
        shift_2 = os.path.join(path,name)
        arcpy.Shift_management(input_DEM, shift_2, CellSize_pos, CellSize_neg, "")

		
		# Process: Shift 4
        messages.addMessage("Process: Shift DEM in Direction 4 ... ")
        name = 'shift_4'
        shift_4 = os.path.join(path,name)
        arcpy.Shift_management(input_DEM, shift_4, "0", CellSize_neg, "")

		
		# Process: Shift 8
        messages.addMessage("Process: Shift DEM in Direction 8 ... ")
        name = 'shift_8'
        shift_8 = os.path.join(path,name)
        arcpy.Shift_management(input_DEM, shift_8, CellSize_neg, CellSize_neg, "")

		
		# Process: Shift 16
        messages.addMessage("Process: Shift DEM in Direction 16 ... ")
        name = 'shift_16'
        shift_16 = os.path.join(path,name)
        arcpy.Shift_management(input_DEM, shift_16, CellSize_neg, "0", "")

		
		# Process: Shift 32
        messages.addMessage("Process: Shift DEM in Direction 32 ... ")
        name = 'shift_32'
        shift_32 = os.path.join(path,name)
        arcpy.Shift_management(input_DEM, shift_32, CellSize_neg, CellSize_pos, "")

		
		# Process: Shift 64
        messages.addMessage("Process: Shift DEM in Direction 64 ... ")
        name = 'shift_64'
        shift_64 = os.path.join(path,name)
        arcpy.Shift_management(input_DEM, shift_64, "0", CellSize_pos, "")

		
        # Process: Shift 128
        messages.addMessage("Process: Shift DEM in Direction 128 ... ")		
        name = 'shift_128'
        shift_128 = os.path.join(path,name)
        arcpy.Shift_management(input_DEM, shift_128, CellSize_pos, CellSize_pos, "")

		# Process: Shift flow direction 1
        messages.addMessage("Process: Shift flow direction in Direction 1 ... ")
        name = 'f_dir_1'
        f_dir_1 = os.path.join(path,name)
        arcpy.Shift_management(f_dir, f_dir_1, CellSize_pos, "0", "")


		# Process: Shift 2
        messages.addMessage("Process: Shift flow direction in Direction 2 ... ")
        name = 'f_dir_2'
        f_dir_2 = os.path.join(path,name)
        arcpy.Shift_management(f_dir, f_dir_2, CellSize_pos, CellSize_neg, "")

		
		# Process: Shift 4
        messages.addMessage("Process: Shift flow direction in Direction 4 ... ")
        name = 'f_dir_4'
        f_dir_4 = os.path.join(path,name)
        arcpy.Shift_management(f_dir, f_dir_4, "0", CellSize_neg, "")

		
		# Process: Shift 8
        messages.addMessage("Process: Shift flow direction in Direction 8 ... ")
        name = 'f_dir_8'
        f_dir_8 = os.path.join(path,name)
        arcpy.Shift_management(f_dir, f_dir_8, CellSize_neg, CellSize_neg, "")

		
		# Process: Shift 16
        messages.addMessage("Process: Shift flow direction in Direction 16 ... ")
        name = 'f_dir_16'
        f_dir_16 = os.path.join(path,name)
        arcpy.Shift_management(f_dir, f_dir_16, CellSize_neg, "0", "")

		
		# Process: Shift 32
        messages.addMessage("Process: Shift flow direction in Direction 32 ... ")
        name = 'f_dir_32'
        f_dir_32 = os.path.join(path,name)
        arcpy.Shift_management(f_dir, f_dir_32, CellSize_neg, CellSize_pos, "")

		
		# Process: Shift 64
        messages.addMessage("Process: Shift flow direction in Direction 64 ... ")
        name = 'f_dir_64'
        f_dir_64 = os.path.join(path,name)
        arcpy.Shift_management(f_dir, f_dir_64, "0", CellSize_pos, "")

		
        # Process: Shift 128
        messages.addMessage("Process: Shift flow direction in Direction 128 ... ")
        name = 'f_dir_128'
        f_dir_128 = os.path.join(path,name)
        arcpy.Shift_management(f_dir, f_dir_128, CellSize_pos, CellSize_pos, "")
			
        # Process: Map Algebra Direction 1
        messages.addMessage("Process: UP_slope_1 ... ")	
        atan = ATan( (Raster(shift_1) - Raster(input_DEM)) / float(CellSize_pos) )
        UP_slope_1 = Con(Raster(f_dir_1) == 1,1,0) * atan * 180.0/3.14159265358979323
	

        # Process: Map Algebra Direction 2
        messages.addMessage("Process: UP_slope_2 ... ")	
        atan = ATan( (Raster(shift_2) - Raster(input_DEM)) / (float(CellSize_pos) * 1.4142135623730950488016887242097) )
        UP_slope_2 = Con(Raster(f_dir_2) == 2,1,0) * atan * 180.0/3.14159265358979323

	
		
        # Process: Map Algebra Direction 4
        messages.addMessage("Process: UP_slope_4 ... ")	
        atan = ATan( (Raster(shift_4) - Raster(input_DEM)) / float(CellSize_pos) )
        UP_slope_4 = Con(Raster(f_dir_4) == 4,1,0) * atan * 180.0/3.14159265358979323



        # Process: Map Algebra Direction 8
        messages.addMessage("Process: UP_slope_8 ... ")	
        atan = ATan( (Raster(shift_8) - Raster(input_DEM)) / (float(CellSize_pos) * 1.4142135623730950488016887242097) )
        UP_slope_8 = Con(Raster(f_dir_8) == 8,1,0) * atan * 180.0/3.14159265358979323



        # Process: Map Algebra Direction 16
        messages.addMessage("Process: UP_slope_16 ... ")	
        atan = ATan( (Raster(shift_16) - Raster(input_DEM)) / float(CellSize_pos) )
        UP_slope_16 = Con(Raster(f_dir_16) == 16,1,0) * atan * 180.0/3.14159265358979323



        # Process: Map Algebra Direction 32
        messages.addMessage("Process: UP_slope_32 ... ")	
        atan = ATan( (Raster(shift_32) - Raster(input_DEM)) / (float(CellSize_pos) * 1.4142135623730950488016887242097) )
        UP_slope_32 = Con(Raster(f_dir_32) == 32,1,0) * atan * 180.0/3.14159265358979323



        # Process: Map Algebra Direction 64
        messages.addMessage("Process: UP_slope_64 ... ")	
        atan = ATan( (Raster(shift_64) - Raster(input_DEM)) / float(CellSize_pos) )
        UP_slope_64 = Con(Raster(f_dir_64) == 64,1,0) * atan * 180.0/3.14159265358979323



        # Process: Map Algebra Direction 128
        messages.addMessage("Process: UP_slope_128 ... ")	
        atan = ATan( (Raster(shift_128) - Raster(input_DEM)) / (float(CellSize_pos) * 1.4142135623730950488016887242097) )
        UP_slope_128 = Con(Raster(f_dir_128) == 128,1,0) * atan * 180.0/3.14159265358979323

		# Process: Cell Statistics
        UP_slope = CellStatistics([UP_slope_1, UP_slope_2, UP_slope_4, UP_slope_8, UP_slope_16, UP_slope_32 , UP_slope_128], "MAXIMUM", "DATA")

        # Process: Map Algebra Downslope
        messages.addMessage("Process: Downslope ... ")	
		
        atan = ATan( (Raster(input_DEM) - Raster(shift_16)) / float(CellSize_pos) )
        con1 = Con(f_dir == 1,1,0) * atan * 180.0/3.14159265358979323

        atan = ATan( (Raster(input_DEM) - Raster(shift_32)) / (float(CellSize_pos) * 1.4142135623730950488016887242097) )
        con2 = Con(f_dir == 2,1,0) * atan * 180.0/3.14159265358979323	

        atan = ATan( (Raster(input_DEM) - Raster(shift_64)) / float(CellSize_pos) )
        con4 = Con(f_dir == 4,1,0) * atan * 180.0/3.14159265358979323

        atan = ATan( (Raster(input_DEM) - Raster(shift_128)) / (float(CellSize_pos) * 1.4142135623730950488016887242097) )
        con8 = Con(f_dir == 8,1,0) * atan * 180.0/3.14159265358979323

        atan = ATan( (Raster(input_DEM) - Raster(shift_1)) / float(CellSize_pos) )
        con16 = Con(f_dir == 16,1,0) * atan * 180.0/3.14159265358979323

        atan = ATan( (Raster(input_DEM) - Raster(shift_2)) / (float(CellSize_pos) * 1.4142135623730950488016887242097) )
        con32 = Con(f_dir == 32,1,0) * atan * 180.0/3.14159265358979323

        atan = ATan( (Raster(input_DEM) - Raster(shift_4)) / float(CellSize_pos) )
        con64 = Con(f_dir == 64,1,0) * atan * 180.0/3.14159265358979323

        atan = ATan( (Raster(input_DEM) - Raster(shift_8)) / (float(CellSize_pos) * 1.4142135623730950488016887242097) )
        con128 = Con(f_dir == 128,1,0) * atan * 180.0/3.14159265358979323	

        DW_slope = con1 + con2 + con4 + con8 + con16 + con32 + + con64 + con128
		
		# Process: Slope Change
        name = 'slope_ch'
        slope_ch = os.path.join(path,name)
        con_thr = Con( (UP_slope - DW_slope) > float(input_slope_threshold),1,0) + Con( f_dir > float(input_f_acc_threshold),1,0)
		
		# Process: SetNull
        f_dir_null = SetNull(con_thr, f_dir, "VALUE > 0")
		
		# Process: Flow Accumulation
        messages.addMessage("Process: Flow Accumulation ... ")
        f_acc_cor = FlowAccumulation(f_dir_null)
        f_acc_cor.save(output_f_acc_cor)
		
        LS_pow = Power(f_acc_cor * float(CellSize_pos) / 22.13 , 0.4 ) * Power(Sin(slope * 3.14159265359/180.0 ) / 0.0896 , 1.2 )
        LS_pow.save(output_LS)
		
        shutil.rmtree(path, ignore_errors=True, onerror=None)
        return


