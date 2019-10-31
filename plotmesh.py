#!/usr/bin/env python
import math
import numpy as np
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

if 'mesh_local_refinement' in yamldata['nalu_preprocess']:
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

# Plot a single mesh slice
def plotslicemesh(axis1, axis2, origin, grid_lengths):
    # Construct the lines to plot
    # axis1 and axis2 are the lines
    p1=np.array(origin)
    p2=p1+axis1*grid_lengths[0]
    p3=p2+axis2*grid_lengths[1]
    p4=p1+axis2*grid_lengths[1]
    p5=p1
    x=[p1[0], p2[0], p3[0], p4[0], p5[0]]
    y=[p1[1], p2[1], p3[1], p4[1], p5[1]]
    #print p1,p2,p3,p4,p5
    plt.fill(x,y, fill=False, hatch='\\\///', lw=0)
    plt.plot(x,y, 'k--', linewidth=0.25)
    return

# Plot a single mesh slice
def plotallslicemesh(axis1, axis2, axis3, origin, grid_lengths, 
                     num_planes, plane_offsets):
    if (num_planes != len(plane_offsets)):
        # Some wrong input here
        print("num_planes != len(plane_offsets)")
        sys.exit(1)
    for poffset in plane_offsets:
        neworigin=np.array(origin)+poffset*np.array(axis3)
        plotslicemesh(axis1, axis2, neworigin, grid_lengths)

    return

def plotwinddirarrow(p0, p1, winddir):
    # get the mesh center
    center=0.5*(np.array(p0)+np.array(p1))
    # Get the theta angle
    theta = (270.0-winddir)*math.pi/180.0
    
    return

# Initialize and plot the base mesh
# ---------------------------------
fig, ax = plt.subplots(1)
plotbasemeshXY(x0, x1, meshdimensions)

# Plot the local mesh refinement
# ---------------------------------
if 'mesh_local_refinement' in yamldata['nalu_preprocess']:
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
else:
    print "No local mesh refinement"


# Plot the mesh slices
# ---------------------------------
if 'slice_mesh' in yamldata:
    print "Going through slices"
    allslices=yamldata['slice_mesh']['slices']
    for slice in allslices:
        axis1        = np.array(slice['axis1'])
        axis2        = np.array(slice['axis2'])
        axis3        = np.array(slice['axis3'])
        origin       = slice['origin']
        grid_lengths = slice['grid_lengths']
        num_planes   = slice['num_planes']
        plane_offsets= slice['plane_offsets']
        # normalize some quantities
        axis1        = axis1/np.linalg.norm(axis1)
        axis2        = axis2/np.linalg.norm(axis2)
        axis3        = axis3/np.linalg.norm(axis3)
        plotallslicemesh(axis1, axis2, axis3, origin, grid_lengths, 
                         num_planes, plane_offsets)
else:
    print "No slicemesh specification"
    

plt.axis("square")
plt.show()

