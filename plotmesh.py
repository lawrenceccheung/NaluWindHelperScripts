#!/usr/bin/env python
import math
import yaml
import sys
import matplotlib.pyplot    as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches     import Rectangle

#yamlfile='abl_preprocess.yaml'
if len(sys.argv)>1:
    yamlfile=sys.argv[1]
else:
    print 'ARGUMENT REQUIRED'
    print ' Usage: %s ABLFILE'%sys.argv[0]
    sys.exit(1)

with open(yamlfile) as stream:
    try:
        yamldata=yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)


## Load data from the yamlfile
# -- mesh extents --
meshvertices     = yamldata['nalu_abl_mesh']['vertices']
x0               = meshvertices[0]
x1               = meshvertices[1]
# -- mesh dimensions --
meshdimensions   = yamldata['nalu_abl_mesh']['mesh_dimensions']

# -- turbine locations --
turbineXY  = yamldata['nalu_preprocess']['mesh_local_refinement']['turbine_locations']
turbineDin = yamldata['nalu_preprocess']['mesh_local_refinement']['turbine_diameters']
turbineHHin= yamldata['nalu_preprocess']['mesh_local_refinement']['turbine_heights']
# make sure turbineD is the right size
if isinstance(turbineDin, list):  turbineD = turbineDin
else:                             turbineD = [turbineDin]*len(turbineXY)
# make sure turbineHH is the right size
if isinstance(turbineHHin, list):  turbineHH = turbineHHin
else:                              turbineHH = [turbineHHin]*len(turbineXY)

# -- Wind direction --
orienttype = yamldata['nalu_preprocess']['mesh_local_refinement']['orientation']['type']
winddir    = yamldata['nalu_preprocess']['mesh_local_refinement']['orientation']['wind_direction']

# -- refinement boxes --
refineboxes      = yamldata['nalu_preprocess']['mesh_local_refinement']['refinement_levels']

#print refineboxes

# Rotates a point pt about origin orig
# Here theta is measured w.r.t. the x-axis
def rotatepoint(pt, orig, theta):
    dx = pt[0]-orig[0]
    dy = pt[1]-orig[1]
    p2=[0.0, 0.0, 0.0]
    p2[0] = dx*math.cos(theta) - dy*math.sin(theta) + orig[0]
    p2[1] = dx*math.sin(theta) + dy*math.cos(theta) + orig[1]
    p2[2] = pt[2]
    return p2

# Get XY points for the turbine
def getTurbXYPoints(turbXY, D, winddir):
    turbR = 0.5*D
    # First define the turbine points
    turbpts = []
    x0=turbXY[0]
    y0=turbXY[1]
    z0=turbXY[2]
    # Points for the blades
    turbpts.append([[x0, y0, z0], [x0, y0+turbR, z0]])  # blade 1
    turbpts.append([[x0, y0, z0], [x0, y0-turbR, z0]])  # blade 2
    # Points for the nacelle
    turbpts.append([[x0-0.05*D, y0-0.05*D, z0], [x0-0.05*D, y0+0.05*D, z0]])  
    turbpts.append([[x0-0.05*D, y0+0.05*D, z0], [x0+0.10*D, y0+0.05*D, z0]])  
    turbpts.append([[x0+0.10*D, y0+0.05*D, z0], [x0+0.10*D, y0-0.05*D, z0]])  
    turbpts.append([[x0-0.05*D, y0-0.05*D, z0], [x0+0.10*D, y0-0.05*D, z0]])  
    
    # Get the theta angle
    theta = (270.0-winddir)*math.pi/180.0
    plotXY=[]
    for vec in turbpts:
        plotXY.append([rotatepoint(p, turbXY, theta) for p in vec ])
    return plotXY

# Get the refinement box
def getRefineBoxXY(turbXY, turbD, refineDim, windDir):
    x1 = turbXY[0]-refineDim[0]*turbD
    x2 = turbXY[0]+refineDim[1]*turbD
    y1 = turbXY[1]-0.5*refineDim[2]*turbD
    y2 = turbXY[1]+0.5*refineDim[2]*turbD

    XYbox = [[x1, y1, 0.0], [x1, y2, 0.0], [x2, y2, 0.0], [x2, y1, 0.0]]

    # Get the theta angle
    theta = (270.0-windDir)*math.pi/180.0
    XYbox2= [rotatepoint(p, turbXY, theta) for p in XYbox ]
    return XYbox2

def plotRefineBox(plotXY, color):
    xpts=[]
    ypts=[]
    for ip, p in enumerate(plotXY):
        xpts.append(p[0])
        ypts.append(p[1])
    xpts.append(plotXY[0][0])
    ypts.append(plotXY[0][1])

    plt.fill(xpts,ypts, color)
    plt.plot(xpts,ypts, 'k', linewidth=0.25)

# Plot a series of XY points
def plotXYpoints(XYpoints):
    for vec in XYpoints:
        p1=vec[0]
        p2=vec[1]
        plt.plot([p1[0], p2[0]], [p1[1], p2[1]], 'k')
    return

# Plot the base mesh
def plotbasemeshXY(p0, p1, meshdimensions):
    rect=Rectangle((p0[0], p0[1]), p1[0]-p0[0], p1[1]-p0[0])
    currentAxis = plt.gca()
    currentAxis.add_patch(rect)
    return

fig, ax = plt.subplots(1)
plotbasemeshXY(x0, x1, meshdimensions)

# Plot the refinement boxes
refinecolors=['c','y','g','r']
for iturb, turb in enumerate(turbineXY):
    for ibox, box in enumerate(refineboxes):
        boxXY = getRefineBoxXY(turb, turbineD[iturb], box, winddir)
        plotRefineBox(boxXY, refinecolors[ibox])


# Plot the turbines
for iturb, turb in enumerate(turbineXY):
    turbpts=getTurbXYPoints(turb, turbineD[iturb], winddir)
    plotXYpoints(turbpts)


#plt.xlim([-10, x1[0]*1.1])
#plt.ylim([-10, x1[1]*1.1])
plt.axis("square")
plt.show()
