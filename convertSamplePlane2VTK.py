#!/usr/bin/env python

from numpy import *
import argparse
import os

# This is the header that goes at the top of all VTK files
vtkheader="""# vtk DataFile Version 3.0
vtk output
ASCII
DATASET STRUCTURED_GRID
"""

# Load all of the information needed from the file
def loadplanefile(filename):
    dat=loadtxt(filename, skiprows=2)
    # Get the maximum indices
    numplanes = int(max(dat[:,0]))
    Numj      = int(max(dat[:,1]))
    Numi      = int(max(dat[:,2]))
    #print numplanes, Numi, Numj
    with open(filename) as fp:
        timestring = fp.readline().strip().split()[1]
        headers    = fp.readline().strip().split()[1:]
    time=float(timestring)
    #print time, headers
    fp.close()
    return dat, time, headers

# group the list of variables
def groupvars(allvarlist):
    justvarnames = [x.split("[")[0] for x in allvarlist]
    uniquevars   = []
    [uniquevars.append(x) for x in justvarnames if x not in uniquevars]
    varsizes = [[x, justvarnames.count(x)] for x in uniquevars]
    return varsizes

# Convert a file into vtk format    
def convertfile(filename, planenum=-1, outdir=''):
    basefile=os.path.splitext(filename)[0]
    print("Converting "+filename)
    dat, time, headers=loadplanefile(filename)
    allvars   = headers[6:]
    groupedvars=groupvars(allvars)
    numplanes = int(max(dat[:,0]))+1
    Numj      = int(max(dat[:,1]))+1
    Numi      = int(max(dat[:,2]))+1
    Nvars     = len(allvars)
    Ngroupedvars=len(groupedvars)
    #print Numi, Numj, numplanes, Nvars, Ngroupedvars
    #print allvars, groupedvars
    if planenum<0:
        doplanes=arange(numplanes)
    else:
        doplanes=[planenum]

    # Go through each plane
    for planenum in doplanes:
        planedat  = dat[dat[:,0]==planenum,:]
        Npoints   = (Numi)*(Numj)
        Ncells    = (Numi-1)*(Numj-1)
        newfile   = basefile+"_plane"+repr(planenum)+".vtk"
        if len(outdir)>0: newfile = outdir+'/'+newfile
        print(" -> writing "+newfile)
        f = open(newfile,"w")
        # Write the header and coordinates
        f.write(vtkheader)
        f.write("DIMENSIONS %i %i 1\n"%(Numi, Numj))
        f.write("POINTS %i float\n"%(Npoints))
        for row in planedat:
            f.write("%e %e %e\n"%(row[3], row[4], row[5]))
        f.write("CELL_DATA %i\n"%Ncells)
        f.write("POINT_DATA %i\n"%Npoints)
        # Write the variables
        f.write("FIELD FieldData %i\n"%Ngroupedvars)
        icol=6
        for ivar, var in enumerate(groupedvars):
            varname=var[0]
            varcomp=var[1]
            f.write("%s %i %i float\n"%(varname, varcomp, Npoints))
            for row in planedat:
                f.write(" ".join([repr(x) for x in row[icol:icol+varcomp]]))
                f.write("\n")
            icol = icol+varcomp
        f.close()
    return

# Handle arguments
parser = argparse.ArgumentParser(description='Convert sample planes to ASCII VTK format')
parser.add_argument('PLANEFILE',  nargs='+',   help="Sample plane file(s) to convert")
parser.add_argument('--planenum', default=-1,  help="Convert only this offset plane number [default: convert all planes]")
parser.add_argument('--outdir',   default='',  help="Write output files in that directory")
args=parser.parse_args()

# Get the default and user arguments
filelist  = args.PLANEFILE
planenum  = int(args.planenum)
outdir    = args.outdir

#print filelist
for file in filelist:
    convertfile(file, planenum=planenum, outdir=outdir)
