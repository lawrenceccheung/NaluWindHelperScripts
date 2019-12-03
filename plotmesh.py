#!/usr/bin/env python
import math
import numpy as np
import yaml
import sys
import matplotlib.pyplot    as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches     import Rectangle
import argparse

# Handle arguments
parser = argparse.ArgumentParser(description='Plot mesh refinement and probe locations')
parser.add_argument('YAMLFILE',  nargs='+',   help="Parse this yaml file for mesh and refinement information")
parser.add_argument('--almyaml', default='',  help="Parse ALMYAML for the turbine and probe information")
parser.add_argument('--slicemeshyaml', default='',  help="Parse SLICEMESHYAML for the slice_mesh specifications")
args=parser.parse_args()


yamlfile=args.YAMLFILE[0]
almyamlfile=args.almyaml
slicemeshyaml=args.slicemeshyaml
# #yamlfile='abl_preprocess.yaml'
# if len(sys.argv)>1:
#     yamlfile=sys.argv[1]
# else:
#     print 'ARGUMENT REQUIRED'
#     print ' Usage: %s ABLFILE'%sys.argv[0]
#     sys.exit(1)



with open(yamlfile) as stream:
    try:
        yamldata=yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)


if 'nalu_preprocess' in yamldata:
    has_preprocess = True
else:
    has_preprocess = False

if has_preprocess:
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
    y1 = turbXY[1]-1.0*refineDim[2]*turbD
    y2 = turbXY[1]+1.0*refineDim[2]*turbD

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
    rect=Rectangle((p0[0], p0[1]), p1[0]-p0[0], p1[1]-p0[1])
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
    plt.fill(x,y, fill=False, hatch='\\\///', lw=0, edgecolor='w')
    plt.plot(x,y, color='k', linestyle='--', linewidth=1.5)
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

# Plot the arrow to indicate wind direction
def plotwinddirarrow(p0, p1, winddir):
    # get the mesh center
    center=0.5*(np.array(p0)+np.array(p1))
    # get the dimensions of the sides
    length=0.5*((p1[0]-p0[0]) + (p1[1]-p0[1]))
    alength=0.1*length
    # Get the theta angle
    theta = (270.0-winddir)*math.pi/180.0
    dx = alength*math.cos(theta)
    dy = alength*math.sin(theta)
    plt.arrow(center[0], center[1], dx, dy, width=0.05*alength)
    return

def plotLineOfSite(tip, tail, npoints):
    # construct the line of points
    dx=(np.array(tip)-np.array(tail))/float(npoints-1)
    x=[]
    y=[]
    z=[]
    for i in range(npoints):
        pt=np.array(tail)+float(i)*dx
        x.append(pt[0])
        y.append(pt[1])
        z.append(pt[2])
    plt.plot(x, y, '.', color='k')
    return

def plotSamplePlane(corner, edge1, edge2, edge1N, edge2N, offsetdir=[], offsetspacings=[]):
    # construct the line of points
    dx=(np.array(edge1))/float(edge1N-1)
    dy=(np.array(edge2))/float(edge2N-1)
    x=[]
    y=[]
    z=[]
    for i in range(edge1N):
        for j in range(edge2N):
            pt=np.array(corner) + float(i)*dx + float(j)*dy
            x.append(pt[0])
            y.append(pt[1])
            z.append(pt[2])
    if ((len(offsetdir)>0) and (len(offsetspacings)>0)):
        for s in offsetspacings:
            plt.plot(np.array(x)+s*offsetdir[0], np.array(y)+s*offsetdir[1], '.', color='k')
    else:
        plt.plot(x, y, '.', color='k')
    return

def readFASTfile(FASTfile, keyword):
    # go through the file line-by-line
    with open(FASTfile) as fp:
        line=fp.readline()
        while line:
            linesplit=line.strip().split()
            if linesplit[1]==keyword: 
                return linesplit[0]
            #print line
            line=fp.readline()
    return


# Initialize and plot the base mesh
# ---------------------------------
fig, ax = plt.subplots(1)

## Load data from the yamlfile
if 'nalu_abl_mesh' in yamldata:
    # -- mesh extents --
    meshvertices     = yamldata['nalu_abl_mesh']['vertices']
    x0               = meshvertices[0]
    x1               = meshvertices[1]
    
    # -- mesh dimensions --
    meshdimensions   = yamldata['nalu_abl_mesh']['mesh_dimensions']
    plotbasemeshXY(x0, x1, meshdimensions)


# Plot the local mesh refinement
# ---------------------------------
if has_preprocess:
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

        plotwinddirarrow(x0, x1, winddir)
    else:
        print("No local mesh refinement")


# Plot the mesh slices
# ---------------------------------
if len(slicemeshyaml)>0:
    with open(slicemeshyaml) as stream:
        try:
            SMyamldata=yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
else:
    SMyamldata = yamldata

if 'slice_mesh' in SMyamldata:
    print("Going through slices")
    allslices=SMyamldata['slice_mesh']['slices']
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
    print("No slice_mesh specification")

# Load the realms YAML file (if necessary)
# ---------------------------------    
if len(almyamlfile)>0:
    with open(almyamlfile) as stream:
        try:
            yamldata=yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

# Plot everything in realms
# ---------------------------------
if 'realms' in yamldata:

    # Plot the turbines
    if 'actuator' in yamldata['realms'][0]:
        nturbs = yamldata['realms'][0]['actuator']['n_turbines_glob']
        # Loop through all of the turbines
        for iturb in range(nturbs):
            turbxy= yamldata['realms'][0]['actuator']['Turbine'+repr(iturb)]['turbine_hub_pos']
            fastfile= yamldata['realms'][0]['actuator']['Turbine'+repr(iturb)]['fast_input_filename']
            # get the fast information
            #print(turbxy, fastfile)
            EDFile=readFASTfile(fastfile, 'EDFile').strip('\"')
            TipRad=float(readFASTfile(EDFile, 'TipRad'))
            NacYaw=float(readFASTfile(EDFile, 'NacYaw'))
            print(EDFile, TipRad, NacYaw)
            turbpts=getTurbXYPoints(turbxy, 2*TipRad, 270-NacYaw)
            plotXYpoints(turbpts)
            
    else:
        print("No actuator line turbines to plot")

    # Plot the data probes
    if 'data_probes' in yamldata['realms'][0]:
        specdata=yamldata['realms'][0]['data_probes']['specifications']
        for spec in specdata:
            # Plot the line-of-site vectors
            if 'line_of_site_specifications' in spec:
                alllos=spec['line_of_site_specifications']
                for los in alllos:
                    Npoints = los['number_of_points']
                    tip     = los['tip_coordinates']
                    tail    = los['tail_coordinates']
                    plotLineOfSite(tip, tail, Npoints)
            # Plot the line-of-site vectors
            if 'plane_specifications' in spec:
                allplanes=spec['plane_specifications']
                for plane in allplanes:
                    corner  = plane['corner_coordinates']
                    edge1   = plane['edge1_vector']
                    edge2   = plane['edge2_vector']
                    edge1N  = plane['edge1_numPoints']
                    edge2N  = plane['edge2_numPoints']
                    if 'offset_vector' in plane:
                        offset_vector   = plane['offset_vector']
                    else:
                        offset_vector=[]
                    if 'offset_spacings' in plane:
                        offset_spacings = plane['offset_spacings']
                    else:
                        offset_spacings=[]
                    plotSamplePlane(corner, edge1, edge2, edge1N, edge2N, 
                                    offsetdir=offset_vector,
                                    offsetspacings=offset_spacings)

else:
    print("No realms to plot")

plt.axis("square")
plt.show()

