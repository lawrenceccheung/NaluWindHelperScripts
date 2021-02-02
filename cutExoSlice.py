# trace generated using paraview version 5.7.0
#
# To ensure correct image size when batch processing, please search 
# for and uncomment the line `# renderView*.ViewSize = [*,*]`

import argparse, os

#### import the simple module from the paraview
from paraview.simple import *
#### disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()

def cutExoSlice(filelist, outfile, origin, normal, time, loadvars=['temperature', 'velocity_'], elemparts=['fluid_part']):
    # create a new 'ExodusIIReader'
    print("Loading files")
    abl_6km_6km_1km_neutralexo384 = ExodusIIReader(FileName=filelist)
    abl_6km_6km_1km_neutralexo384.PointVariables = []
    abl_6km_6km_1km_neutralexo384.NodeSetArrayStatus = []
    abl_6km_6km_1km_neutralexo384.SideSetArrayStatus = []

    # get animation scene
    animationScene1 = GetAnimationScene()

    # get the time-keeper
    timeKeeper1 = GetTimeKeeper()

    # update animation scene based on data timesteps
    animationScene1.UpdateAnimationUsingDataTimeSteps()

    # Properties modified on abl_6km_6km_1km_neutralexo384
    abl_6km_6km_1km_neutralexo384.PointVariables = loadvars 
    abl_6km_6km_1km_neutralexo384.ElementBlocks  = elemparts
    abl_6km_6km_1km_neutralexo384.FilePrefix = ''
    abl_6km_6km_1km_neutralexo384.FilePattern = ''

    # get active view
    renderView1 = GetActiveViewOrCreate('RenderView')
    # uncomment following to set a specific view size
    # renderView1.ViewSize = [1420, 1101]

    # show data in view
    abl_6km_6km_1km_neutralexo384Display = Show(abl_6km_6km_1km_neutralexo384, renderView1)

    # trace defaults for the display properties.
    abl_6km_6km_1km_neutralexo384Display.Representation = 'Surface'
    abl_6km_6km_1km_neutralexo384Display.ColorArrayName = [None, '']
    abl_6km_6km_1km_neutralexo384Display.OSPRayScaleArray = 'GlobalNodeId'
    abl_6km_6km_1km_neutralexo384Display.OSPRayScaleFunction = 'PiecewiseFunction'
    abl_6km_6km_1km_neutralexo384Display.SelectOrientationVectors = 'GlobalNodeId'
    abl_6km_6km_1km_neutralexo384Display.ScaleFactor = 199.5
    abl_6km_6km_1km_neutralexo384Display.SelectScaleArray = 'GlobalNodeId'
    abl_6km_6km_1km_neutralexo384Display.GlyphType = 'Arrow'
    abl_6km_6km_1km_neutralexo384Display.GlyphTableIndexArray = 'GlobalNodeId'
    abl_6km_6km_1km_neutralexo384Display.GaussianRadius = 9.975
    abl_6km_6km_1km_neutralexo384Display.SetScaleArray = ['POINTS', 'GlobalNodeId']
    abl_6km_6km_1km_neutralexo384Display.ScaleTransferFunction = 'PiecewiseFunction'
    abl_6km_6km_1km_neutralexo384Display.OpacityArray = ['POINTS', 'GlobalNodeId']
    abl_6km_6km_1km_neutralexo384Display.OpacityTransferFunction = 'PiecewiseFunction'
    abl_6km_6km_1km_neutralexo384Display.DataAxesGrid = 'GridAxesRepresentation'
    abl_6km_6km_1km_neutralexo384Display.PolarAxes = 'PolarAxesRepresentation'
    abl_6km_6km_1km_neutralexo384Display.ScalarOpacityUnitDistance = 16.03899608528416
    abl_6km_6km_1km_neutralexo384Display.ExtractedBlockIndex = 2

    # init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
    abl_6km_6km_1km_neutralexo384Display.ScaleTransferFunction.Points = [1.0, 0.0, 0.5, 0.0, 6087867.0, 1.0, 0.5, 0.0]

    # init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
    abl_6km_6km_1km_neutralexo384Display.OpacityTransferFunction.Points = [1.0, 0.0, 0.5, 0.0, 6087867.0, 1.0, 0.5, 0.0]

    # reset view to fit data
    renderView1.ResetCamera()

    #changing interaction mode based on data extents
    renderView1.InteractionMode = '3D'

    # get the material library
    materialLibrary1 = GetMaterialLibrary()

    # update the view to ensure updated data information
    renderView1.Update()

    # set scalar coloring
    ColorBy(abl_6km_6km_1km_neutralexo384Display, ('FIELD', 'vtkBlockColors'))

    # show color bar/color legend
    abl_6km_6km_1km_neutralexo384Display.SetScalarBarVisibility(renderView1, True)

    # get color transfer function/color map for 'vtkBlockColors'
    vtkBlockColorsLUT = GetColorTransferFunction('vtkBlockColors')

    # get opacity transfer function/opacity map for 'vtkBlockColors'
    vtkBlockColorsPWF = GetOpacityTransferFunction('vtkBlockColors')

    print("Creating slice")
    # create a new 'Slice'
    slice1 = Slice(Input=abl_6km_6km_1km_neutralexo384)
    slice1.SliceType = 'Plane'
    slice1.SliceOffsetValues = [0.0]
    
    # init the 'Plane' selected for 'SliceType'
    #slice1.SliceType.Origin = [750.0, 750.0, 997.5]

    # Properties modified on slice1.SliceType
    slice1.SliceType.Origin = origin 
    slice1.SliceType.Normal = normal 

    # get active view
    renderView1 = GetActiveViewOrCreate('RenderView')
    # uncomment following to set a specific view size
    # renderView1.ViewSize = [1420, 1101]

    # show data in view
    slice1Display = Show(slice1, renderView1)

    # get color transfer function/color map for 'velocity_'
    velocity_LUT = GetColorTransferFunction('velocity_')

    # trace defaults for the display properties.
    slice1Display.Representation = 'Surface'
    slice1Display.ColorArrayName = ['POINTS', 'velocity_']
    slice1Display.LookupTable = velocity_LUT
    slice1Display.OSPRayScaleArray = 'velocity_'
    slice1Display.OSPRayScaleFunction = 'PiecewiseFunction'
    slice1Display.SelectOrientationVectors = 'None'
    slice1Display.ScaleFactor = 150.0
    slice1Display.SelectScaleArray = 'None'
    slice1Display.GlyphType = 'Arrow'
    slice1Display.GlyphTableIndexArray = 'None'
    slice1Display.GaussianRadius = 7.5
    slice1Display.SetScaleArray = ['POINTS', 'velocity_']
    slice1Display.ScaleTransferFunction = 'PiecewiseFunction'
    slice1Display.OpacityArray = ['POINTS', 'velocity_']
    slice1Display.OpacityTransferFunction = 'PiecewiseFunction'
    slice1Display.DataAxesGrid = 'GridAxesRepresentation'
    slice1Display.PolarAxes = 'PolarAxesRepresentation'
    
    # init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
    slice1Display.ScaleTransferFunction.Points = [4.647858031593322, 0.0, 0.5, 0.0, 10.310738554289241, 1.0, 0.5, 0.0]
    
    # init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
    slice1Display.OpacityTransferFunction.Points = [4.647858031593322, 0.0, 0.5, 0.0, 10.310738554289241, 1.0, 0.5, 0.0]

    # show color bar/color legend
    slice1Display.SetScalarBarVisibility(renderView1, True)
    
    # Properties modified on animationScene1
    animationScene1.AnimationTime = time #25000.0

    # Properties modified on timeKeeper1
    timeKeeper1.Time = time #25000.0
    
    # save data
    print("Saving slice")
    SaveData(outfile, proxy=slice1, WriteAllTimeSteps=0)

    #### saving camera placements for all active views

    # current camera placement for renderView1
    # renderView1.CameraPosition = [4093.833232027152, -3774.0096668602637, 997.5]
    # renderView1.CameraFocalPoint = [750.0, 750.0, 997.5]
    # renderView1.CameraViewUp = [0.0, 0.0, 1.0]
    # renderView1.CameraParallelScale = 1456.0241241133335

#### uncomment the following to render all views
# RenderAllViews()
# alternatively, if you want to write images, you can use SaveScreenshot(...).


# ----- Main program -----------------------
parser = argparse.ArgumentParser(description='Run paraview batch program')
parser.add_argument('EXOFILES',     nargs="+")
parser.add_argument('-c','--center',  required=True, default='[0,0,0]', #nargs='+',
                    help="Center point for cut")
parser.add_argument('-n','--normal',  required=True, default='[1,1,1]', #nargs='+',
                    help="Normal vector for cut")
parser.add_argument('-o','--outfile', required=False, default='slice.exo',
                    help="Output slice filename (default: slice.exo)")
parser.add_argument('-t','--time',  required=False, default='last', 
                    help="Time to extract slice")


# Set up the arguments
args        = parser.parse_args()
center      = eval(args.center) #eval(' '.join(args.center))
normal      = eval(args.normal) #eval(' '.join(args.normal))
outfile     = args.outfile
time        = args.time
exofiles    = args.EXOFILES

# Get the time to pull
if (time == 'last'):
    cmd="ncdump -v time_whole %s  | sed -ne '/time_whole =/,$ p' | sed -e 's/}//g'  -e 's/\;//g' |tr -d '\\n' | awk '{print $NF}'"
    pulltime=float(os.popen(cmd%exofiles[0]).read().strip())
else:
    pulltime=float(time)
print(pulltime)

print(center)
print(normal)
#print(exofiles)
print("Cutting slice")
cutExoSlice(exofiles, outfile, center, normal, pulltime)
