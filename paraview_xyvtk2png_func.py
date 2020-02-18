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
    renderView1.ViewSize = getparam('ViewSize', params, [1000,1000]) 

    # create a new 'Calculator'
    calculator1 = Calculator(Input=hHplane_0009000_0_plane)
    calculator1.Function = ''

    # Properties modified on calculator1
    calculator1.ResultArrayName = 'Velocity_Horizontal'
    #calculator1.Function = 'sqrt(velocity_probe_X^2 + velocity_probe_Y^2)'
    #calcFunc = 'sqrt(velocity_probe_X^2 + velocity_probe_Y^2)'
    displayTitle = getparam('displayTitle', params, 'Horiz_Velocity')
    displayVar   = getparam('displayVar', params, 'sqrt(velocity_probe_X^2 + velocity_probe_Y^2)')
    calculator1.Function = displayVar

    # get active view
    renderView1 = GetActiveViewOrCreate('RenderView')
    # uncomment following to set a specific view size
    # renderView1.ViewSize = [1420, 764]

    # show data in view
    Hide(hHplane_0009000_0_plane, renderView1)
    calculator1Display = Show(calculator1, renderView1)

    # get color transfer function/color map for 'Velocity_Horizontal'
    velocity_HorizontalLUT = GetColorTransferFunction('Velocity_Horizontal')

    # get opacity transfer function/opacity map for 'Velocity_Horizontal'
    velocity_HorizontalPWF = GetOpacityTransferFunction('Velocity_Horizontal')

    # trace defaults for the display properties.
    calculator1Display.Representation = 'Surface'
    calculator1Display.ColorArrayName = ['POINTS', 'Velocity_Horizontal']
    calculator1Display.LookupTable = velocity_HorizontalLUT
    calculator1Display.OSPRayScaleArray = 'Velocity_Horizontal'
    calculator1Display.OSPRayScaleFunction = 'PiecewiseFunction'
    calculator1Display.SelectOrientationVectors = 'None'
    calculator1Display.ScaleFactor = 600.0
    calculator1Display.SelectScaleArray = 'Velocity_Horizontal'
    calculator1Display.GlyphType = 'Arrow'
    calculator1Display.GlyphTableIndexArray = 'Velocity_Horizontal'
    calculator1Display.GaussianRadius = 30.0
    calculator1Display.SetScaleArray = ['POINTS', 'Velocity_Horizontal']
    calculator1Display.ScaleTransferFunction = 'PiecewiseFunction'
    calculator1Display.OpacityArray = ['POINTS', 'Velocity_Horizontal']
    calculator1Display.OpacityTransferFunction = 'PiecewiseFunction'
    calculator1Display.DataAxesGrid = 'GridAxesRepresentation'
    calculator1Display.PolarAxes = 'PolarAxesRepresentation'
    calculator1Display.ScalarOpacityFunction = velocity_HorizontalPWF
    calculator1Display.ScalarOpacityUnitDistance = 189.34423142112703

    # init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
    calculator1Display.ScaleTransferFunction.Points = [3.098678881954074, 0.0, 0.5, 0.0, 6.711336360706567, 1.0, 0.5, 0.0]
    
    # init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
    calculator1Display.OpacityTransferFunction.Points = [3.098678881954074, 0.0, 0.5, 0.0, 6.711336360706567, 1.0, 0.5, 0.0]

    # show color bar/color legend
    calculator1Display.SetScalarBarVisibility(renderView1, True)

    # Start changing user parameters
    # ---------------------------------------------------
    YTitle = getparam('YTitle', params, 'Y Axis     ')
    XTitle = getparam('XTitle', params, 'X Axis     ')
    calculator1Display.DataAxesGrid.YTitle = YTitle
    calculator1Display.DataAxesGrid.XTitle = XTitle

    # Change some font colors
    axeson = getparam('GridAxesVisibility', params, 1)
    calculator1Display.DataAxesGrid.GridAxesVisibility = axeson

    calculator1Display.DataAxesGrid.XTitleColor = [0.0, 0.0, 0.0]
    calculator1Display.DataAxesGrid.YTitleColor = [0.0, 0.0, 0.0]
    calculator1Display.DataAxesGrid.AxesToLabel = 3

    calculator1Display.DataAxesGrid.XLabelColor = [0.0, 0.0, 0.0]
    calculator1Display.DataAxesGrid.YLabelColor = [0.0, 0.0, 0.0]

    # Change some font sizes
    fontsize = getparam('fontsize',params,10)
    calculator1Display.DataAxesGrid.YTitleFontSize = fontsize
    calculator1Display.DataAxesGrid.XTitleFontSize = fontsize
    calculator1Display.DataAxesGrid.YLabelFontSize = fontsize
    calculator1Display.DataAxesGrid.XLabelFontSize = fontsize
    
    [cmin, cmax] = getparam('colorlims', params, [0.0, 10.0]) 
    # Rescale transfer function
    velocity_HorizontalLUT.RescaleTransferFunction(cmin, cmax)
    # Rescale transfer function
    velocity_HorizontalPWF.RescaleTransferFunction(cmin, cmax)

    # change scalar bar placement
    velocity_probeLUTColorBar = GetScalarBar(velocity_HorizontalLUT, renderView1)
    velocity_probeLUTColorBar.ScalarBarLength = 0.250
    velocity_probeLUTColorBar.ScalarBarThickness = 10
    velocity_probeLUTColorBar.TitleFontSize = fontsize #10
    velocity_probeLUTColorBar.LabelFontSize = fontsize #10
    velocity_probeLUTColorBar.WindowLocation = 'AnyLocation'
    colorbarpos = getparam('colorbarpos',params, [0.9, 0.25])
    velocity_probeLUTColorBar.Position = colorbarpos

    velocity_probeLUTColorBar.TitleColor = [0.0, 0.0, 0.0]
    velocity_probeLUTColorBar.LabelColor = [0.0, 0.0, 0.0]

    # reset view to fit data bounds
    [xmin, xmax, ymin, ymax] = getparam('xylims', params, [0, 6000, 0, 6000])
    renderView1.ResetCamera(xmin, xmax, ymin, ymax, 20.0, 20.0)
    renderView1.Background=[1,1,1]
    renderView1.OrientationAxesVisibility = 0

    imagesize=getparam('imagesize', params, [1000,1000])
    SaveScreenshot(pngfile, renderView1, ImageResolution=imagesize)

    Delete(calculator1Display)
    del calculator1Display

    # destroy hHplane_0009000_0_plane
    Delete(hHplane_0009000_0_plane)
    del hHplane_0009000_0_plane

    # --------------------------------------


# ----- Default settings -----------------------
defaultpvbatch   = 'module load viz; pvbatch'
skybridgepvbatch = '/projects/viz/paraview/bin/pvbatch_skybridge_mesa_5.7.0 '
chamapvbatch     = '/projects/viz/paraview/bin/pvbatch_chama_mesa_5.7.0 '
NCPUS            = 1
CPUTIME          = 60

defaultdict      = {'colorlims':[0, 10],
                    'colorbarpos':[0.85, 0.25],
                    'XTitle':'X [m]',
                    'YTitle':'Y [m]       ',
                    'xylims':[0, 6000, 0, 6000],
                    'ViewSize':[1000, 1000],
                    'imagesize':[1000, 1000],
                    'fontsize':16,
                    'GridAxesVisibility':1,
                    'displayTitle':'Horiz_Velocity',
                    'displayVar':'sqrt(velocity_probe_X^2 + velocity_probe_Y^2)',
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
printparams = args.printparams
useskybridge= args.useskybridge
usechama    = args.usechama

if printparams: 
    defaultdict.update(eval(args.useparams))
    print(defaultdict)
    sys.exit(0)

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
    thisfile    = sys.argv[0]

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
