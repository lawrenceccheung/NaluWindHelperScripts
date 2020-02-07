#!/usr/bin/env python
# trace generated using paraview version 5.7.0
#
# To ensure correct image size when batch processing, please search 
# for and uncomment the line `# renderView*.ViewSize = [*,*]`

# Call with 
# /projects/viz/paraview/bin/pvbatch_skybridge_mesa_5.7.0 1 60 FY190020 ~/paraview/testsample2.py VTKFILE PNGFILE

import sys
import os
import argparse
import base64

# Load things if in paraview
try: 
    #### import the simple module from the paraview
    from paraview.simple import *
    #### disable automatic camera reset on 'Show'
    paraview.simple._DisableFirstRenderCameraReset()
    inParaview = True
except:
    inParaview = False

# Pulls a value from a dictionary, otherwise use a default:
#   getparam(keylabel, pdict, default) 
getparam = lambda keylabel, pdict, default: pdict[keylabel] if keylabel in pdict else default

# Function to load a vtk file and output a png file (for the HHplane)
def outputpng(vtkfile, pngfile, params={}):
    # create a new 'Legacy VTK Reader'
    hHplane_0009000_0_plane = LegacyVTKReader(FileNames=[vtkfile])

    # get animation scene
    animationScene1 = GetAnimationScene()

    # get the time-keeper
    timeKeeper1 = GetTimeKeeper()

    # update animation scene based on data timesteps
    animationScene1.UpdateAnimationUsingDataTimeSteps()

    # get active view
    renderView1 = GetActiveViewOrCreate('RenderView')
    # uncomment following to set a specific view size
    #renderView1.ViewSize = [1000, 1000]
    renderView1.ViewSize = getparam('ViewSize', params, [1000,1000]) #params['ViewSize'] if 'ViewSize' in params else [1000,1000]    

    # show data in view
    hHplane_0009000_0_planeDisplay = Show(hHplane_0009000_0_plane, renderView1)

    # trace defaults for the display properties.
    hHplane_0009000_0_planeDisplay.Representation = 'Surface'
    hHplane_0009000_0_planeDisplay.ColorArrayName = [None, '']
    hHplane_0009000_0_planeDisplay.OSPRayScaleArray = 'temperature_probe'
    hHplane_0009000_0_planeDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
    hHplane_0009000_0_planeDisplay.SelectOrientationVectors = 'None'
    hHplane_0009000_0_planeDisplay.ScaleFactor = 600.0
    hHplane_0009000_0_planeDisplay.SelectScaleArray = 'None'
    hHplane_0009000_0_planeDisplay.GlyphType = 'Arrow'
    hHplane_0009000_0_planeDisplay.GlyphTableIndexArray = 'None'
    hHplane_0009000_0_planeDisplay.GaussianRadius = 30.0
    hHplane_0009000_0_planeDisplay.SetScaleArray = ['POINTS', 'temperature_probe']
    hHplane_0009000_0_planeDisplay.ScaleTransferFunction = 'PiecewiseFunction'
    hHplane_0009000_0_planeDisplay.OpacityArray = ['POINTS', 'temperature_probe']
    hHplane_0009000_0_planeDisplay.OpacityTransferFunction = 'PiecewiseFunction'
    hHplane_0009000_0_planeDisplay.DataAxesGrid = 'GridAxesRepresentation'
    hHplane_0009000_0_planeDisplay.PolarAxes = 'PolarAxesRepresentation'
    hHplane_0009000_0_planeDisplay.ScalarOpacityUnitDistance = 189.34423142112703

    # init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
    hHplane_0009000_0_planeDisplay.ScaleTransferFunction.Points = [300.0, 0.0, 0.5, 0.0, 300.0625, 1.0, 0.5, 0.0]

    # init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
    hHplane_0009000_0_planeDisplay.OpacityTransferFunction.Points = [300.0, 0.0, 0.5, 0.0, 300.0625, 1.0, 0.5, 0.0]

    # reset view to fit data
    renderView1.ResetCamera()

    #changing interaction mode based on data extents
    renderView1.InteractionMode = '2D'
    renderView1.CameraPosition = [3000.0, 3000.0, 10020.0]
    renderView1.CameraFocalPoint = [3000.0, 3000.0, 20.0]

    # get the material library
    materialLibrary1 = GetMaterialLibrary()

    # update the view to ensure updated data information
    renderView1.Update()

    # set scalar coloring
    ColorBy(hHplane_0009000_0_planeDisplay, ('POINTS', 'velocity_probe', 'Magnitude'))

    # rescale color and/or opacity maps used to include current data range
    hHplane_0009000_0_planeDisplay.RescaleTransferFunctionToDataRange(True, False)

    # show color bar/color legend
    hHplane_0009000_0_planeDisplay.SetScalarBarVisibility(renderView1, True)

    # get color transfer function/color map for 'velocity_probe'
    velocity_probeLUT = GetColorTransferFunction('velocity_probe')
    # get opacity transfer function/opacity map for 'velocity_probe'
    velocity_probePWF = GetOpacityTransferFunction('velocity_probe')

    # change representation type
    hHplane_0009000_0_planeDisplay.SetRepresentationType('Points')
    
    # change representation type
    hHplane_0009000_0_planeDisplay.SetRepresentationType('Surface')

    # Properties modified on hHplane_0009000_0_planeDisplay.DataAxesGrid
    hHplane_0009000_0_planeDisplay.DataAxesGrid.GridAxesVisibility = 1

    # Properties modified on hHplane_0009000_0_planeDisplay.DataAxesGrid
    #hHplane_0009000_0_planeDisplay.DataAxesGrid.YTitle = 'Y Axis  '
    hHplane_0009000_0_planeDisplay.DataAxesGrid.XTitleColor = [0.0, 0.0, 0.0]
    hHplane_0009000_0_planeDisplay.DataAxesGrid.YTitleColor = [0.0, 0.0, 0.0]
    hHplane_0009000_0_planeDisplay.DataAxesGrid.AxesToLabel = 3

    # Properties modified on hHplane_0009000_0_planeDisplay.DataAxesGrid
    hHplane_0009000_0_planeDisplay.DataAxesGrid.XLabelColor = [0.0, 0.0, 0.0]
    hHplane_0009000_0_planeDisplay.DataAxesGrid.YLabelColor = [0.0, 0.0, 0.0]

    # Properties modified on hHplane_0009000_0_planeDisplay.DataAxesGrid
    YTitle = params['YTitle'] if 'YTitle' in params else 'Y Axis     '
    hHplane_0009000_0_planeDisplay.DataAxesGrid.YTitle = YTitle
    XTitle = params['XTitle'] if 'XTitle' in params else 'X Axis     '
    hHplane_0009000_0_planeDisplay.DataAxesGrid.XTitle = XTitle

    # Change some font sizes
    fontsize = getparam('fontsize',params,10)
    hHplane_0009000_0_planeDisplay.DataAxesGrid.YTitleFontSize = fontsize
    hHplane_0009000_0_planeDisplay.DataAxesGrid.XTitleFontSize = fontsize
    hHplane_0009000_0_planeDisplay.DataAxesGrid.YLabelFontSize = fontsize
    hHplane_0009000_0_planeDisplay.DataAxesGrid.XLabelFontSize = fontsize


    # get color legend/bar for velocity_probeLUT in view renderView1
    velocity_probeLUTColorBar = GetScalarBar(velocity_probeLUT, renderView1)

    # Properties modified on velocity_probeLUTColorBar
    velocity_probeLUTColorBar.TitleColor = [0.0, 0.0, 0.0]
    velocity_probeLUTColorBar.LabelColor = [0.0, 0.0, 0.0]

    # change representation type
    hHplane_0009000_0_planeDisplay.SetRepresentationType('Surface')
    
    # set scalar coloring
    # ColorBy(hHplane_0009000_0_planeDisplay, ('POINTS', 'temperature_probe'))
    
    # Hide the scalar bar for this color map if no visible data is colored by it.
    HideScalarBarIfNotNeeded(velocity_probeLUT, renderView1)

    # rescale color and/or opacity maps used to include current data range
    hHplane_0009000_0_planeDisplay.RescaleTransferFunctionToDataRange(True, False)

    # show color bar/color legend
    hHplane_0009000_0_planeDisplay.SetScalarBarVisibility(renderView1, True)

    # get color transfer function/color map for 'temperature_probe'
    temperature_probeLUT = GetColorTransferFunction('temperature_probe')
    
    # get opacity transfer function/opacity map for 'temperature_probe'
    temperature_probePWF = GetOpacityTransferFunction('temperature_probe')
    
    # change representation type
    hHplane_0009000_0_planeDisplay.SetRepresentationType('Surface')

    # Rescale transfer function
    #velocity_probeLUT.RescaleTransferFunction(5.0, 15.0)
    cmin = params['colorlims'][0] if 'colorlims' in params else 0.0
    cmax = params['colorlims'][1] if 'colorlims' in params else 10.0
    velocity_probeLUT.RescaleTransferFunction(cmin, cmax)
    
    # change scalar bar placement
    #velocity_probeLUTColorBar.Position = [0.6, 0.1]
    velocity_probeLUTColorBar.ScalarBarLength = 0.250
    velocity_probeLUTColorBar.ScalarBarThickness = 10
    velocity_probeLUTColorBar.TitleFontSize = fontsize #10
    velocity_probeLUTColorBar.LabelFontSize = fontsize #10
    velocity_probeLUTColorBar.WindowLocation = 'AnyLocation'

    # reset view to fit data bounds
    xmin = params['xylims'][0] if 'xylims' in params else 0.0
    xmax = params['xylims'][1] if 'xylims' in params else 6000.0
    ymin = params['xylims'][2] if 'xylims' in params else 0.0
    ymax = params['xylims'][3] if 'xylims' in params else 6000.0
    #renderView1.ResetCamera(0.0, 6000.0, 0.0, 6000.0, 20.0, 20.0)
    renderView1.ResetCamera(xmin, xmax, ymin, ymax, 20.0, 20.0)
    renderView1.Background=[1,1,1]
    renderView1.OrientationAxesVisibility = 0

    colorbarpos = params['colorbarpos'] if 'colorbarpos' in params else [0.9, 0.25]    
    velocity_probeLUTColorBar.Position = colorbarpos

    imagesize=params['imagesize'] if 'imagesize' in params else [1000,1000]    
    SaveScreenshot(pngfile, renderView1, ImageResolution=imagesize)

    # destroy hHplane_0009000_0_plane
    Delete(hHplane_0009000_0_plane)
    del hHplane_0009000_0_plane

# ----- Default settings -----------------------
defaultpvbatch   = 'module load viz; pvbatch'
skybridgepvbatch = '/projects/viz/paraview/bin/pvbatch_skybridge_mesa_5.7.0 '
chamapvbatch     = '/projects/viz/paraview/bin/pvbatch_chama_mesa_5.7.0 '
NCPUS            = 1
CPUTIME          = 60

defaultdict      = {'colorlims':[0, 10],
                    'colorbarpos':[0.90, 0.25],
                    'XTitle':'X [m]',
                    'YTitle':'Y [m]       ',
                    #'XTitle':'X Axis',
                    #'YTitle':'Y Axis     ',
                    'xylims':[0, 6000, 0, 6000],
                    'ViewSize':[1000, 1000],
                    'imagesize':[1000, 1000],
                    'fontsize':10,
                    }

# ----- Main program -----------------------
parser = argparse.ArgumentParser(description='Run paraview batch program')
parser.add_argument('VTKFILE',     nargs="+")
parser.add_argument('--pvbatchcmd', 
                    default=defaultpvbatch,
                    help="Command to execute to call pvbatch [Default: '%s']"%defaultpvbatch)
parser.add_argument('--useparams',    default='{}',
                    help="dictionary with parameters to override")
parser.add_argument('--printparams',  dest='printparams', action='store_true',
                    help="Print the default dictionary parameters")
parser.add_argument('--useskybridge', dest='useskybridge', action='store_true',
                    help="Use skybridge's pvbatch")
parser.add_argument('--usechama',     dest='usechama', action='store_true',
                    help="Use chama's pvbatch")
parser.add_argument('--b64params',    default='',
                    help=argparse.SUPPRESS)

parser.set_defaults(printparams  = False)
parser.set_defaults(useskybridge = False)
parser.set_defaults(usechama     = False)

args        = parser.parse_args()
allvtkfiles = vars(args)['VTKFILE']
pvbatchcmd  = args.pvbatchcmd
#print("args.useparams: "+args.useparams)
#print("args.b64params: "+args.b64params)
printparams = args.printparams
useskybridge= args.useskybridge
usechama    = args.usechama
thisfile    = sys.argv[0]


if (inParaview): # --- Do this in paraview ---
    # Update the dictionary with defaults
    #updatedict  = eval("{"+args.useparams+"}")
    if len(args.b64params)>0:
        updatedict   = base64.b64decode(args.b64params)
        #print("decoded str:")
        #print(eval(updatedict))
        defaultdict.update(eval(updatedict))
    print("Using dict:")
    print(defaultdict)
    # Loop through all of the vtk files    
    for vtkfile in allvtkfiles:
        basefile, ext = os.path.splitext(vtkfile)
        pngfile = basefile+'.png'
        print("Working on "+vtkfile)
        outputpng(vtkfile, pngfile, params=defaultdict)

else:            # --- Call pvbatch ---
    allargs = ' '.join(allvtkfiles)
    if (args.useparams != '{}'):
        allargs = allargs+" --b64params %s "%(base64.b64encode(args.useparams))
    if (useskybridge or usechama):
        WCID             = os.getenv('WCID')
        if WCID == None:
            print("Please set WCID environment variable")
            print("e.g., in bash:")
            print("  export WCID=XYZ123")
            sys.exit(1)
        if useskybridge:
            pvbatchcmd=skybridgepvbatch
        if usechama:
            pvbatchcmd=chamapvbatch
        pvbatchcmd = pvbatchcmd+' %i %i %s'%(NCPUS, CPUTIME, WCID)
    runcmd  = pvbatchcmd+' '+thisfile+' '+allargs
    #defaultdict.update(updatedict)
    if printparams: 
        defaultdict.update(eval(args.useparams))
        print(defaultdict)
        sys.exit(0)
    print("running paraview: "+runcmd)
    print(os.popen(runcmd).read().strip())
