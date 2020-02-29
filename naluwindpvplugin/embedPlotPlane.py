import os, sys
import glob
import numpy as np
import paraview.simple as pvs
import gzip

# group the list of variables
def groupvars(allvarlist):
    justvarnames = [x.split('[')[0] for x in allvarlist]
    uniquevars   = []
    [uniquevars.append(x) for x in justvarnames if x not in uniquevars]
    varsizes = [[x, justvarnames.count(x)] for x in uniquevars]
    return varsizes

# Make a plane based on planefile
def makePlane(planefile, planes=[]):
    # Read the plane
    dat=loadtxt(planefile, skiprows=2)
    numplanes = int(max(dat[:,0]))+1
    Numj      = int(max(dat[:,1]))+1
    Numi      = int(max(dat[:,2]))+1
    # Take care of headers and variables
    headers=getHeaders(planefile)
    numvariables = len(headers)-6
    groupedvars=groupvars(headers[6:])
    if verbose: print(groupedvars)
    allvars   = []
    # for ivar in range(0, numvariables):
    #     print('Added variable ',headers[6+ivar])
    #     vals = vtk.vtkDoubleArray()
    #     vals.SetName(headers[6+ivar])
    #     allvars.append(vals)
    for ivar in range(0, len(groupedvars)):
        name   = groupedvars[ivar][0]
        Ncomps = groupedvars[ivar][1]
        if verbose: print('Adding variable ',name,' comps: ',Ncomps)
        vals   = vtk.vtkDoubleArray()
        vals.SetNumberOfComponents(Ncomps)
        vals.SetName(name)
        allvars.append(vals)
    ## vals1     = vtk.vtkDoubleArray()
    ## vals1.SetName(headers[6])
    pdo = self.GetPolyDataOutput()
    points = vtk.vtkPoints()
    for irow, row in enumerate(dat):
        x = row[3]
        y = row[4]
        z = row[5]
        points.InsertPoint(irow, x, y, z) 
        # Add field variables
        icol=6
        for ivar in range(0, len(groupedvars)):
            Ncomps = groupedvars[ivar][1]
            if Ncomps==1:
                vval = row[icol]
                allvars[ivar].InsertNextValue(vval)
                icol = icol + 1
            else:
                vval=[]
                for icomp in range(0,Ncomps):
                    vval.append(row[icol])
                    icol = icol + 1
                allvars[ivar].InsertNextTuple(vval)
        # for ivar in range(0, numvariables):
        #     vval = row[6+ivar]
        #     allvars[ivar].InsertNextValue(vval)
        ## v1= row[6]
        ## vals1.InsertNextValue(v1)

    pdo.SetPoints(points)
    if (len(groupedvars)>0):
        for ivar in range(0, len(groupedvars)):
            pdo.GetPointData().AddArray(allvars[ivar])
    pdo.Allocate(numplanes*Numj*Numi, 4)
    # Set up the plane cells
    rect = vtk.vtkPolygon()
    rect.GetPointIds().SetNumberOfIds(4)

    iplane = 0
    npts=0
    if (len(planes)==0):
        planevec=range(0,numplanes)
    else:
        planevec=planes
    allplanes=range(0,numplanes)
    for iplane in planevec:
        if (iplane not in allplanes):
            print('WARNING: Cannot plot plane number: %i'%iplane, file=sys.stderr) 
            print('WARNING: Plane out of range')
            return
        for j in range(0, Numj-1):
            for i in range(0, Numi-1):
                p0 = iplane*Numj*Numi + j*Numi + i
                p1 = iplane*Numj*Numi + (j+1)*Numi + i
                p2 = iplane*Numj*Numi + (j+1)*Numi + (i+1)
                p3 = iplane*Numj*Numi + (j)*Numi + (i+1)
                rectpts=[p0, p1, p2, p3]
                #print(p0, p1, p2, p3)
                npts=npts+1
                for p in range(0, 4):
                    rect.GetPointIds().SetId(p, rectpts[p])
                pdo.InsertNextCell(rect.GetCellType(), rect.GetPointIds())
    if verbose: print(numplanes, Numi, Numj, npts)
    #print('ncells =',npts)

    #pd = self.GetPolyDataOutput()
    #pd.ShallowCopy(points.GetOutput())

# Read the time from the dat file
def getFileTime(filename):
    fname, fext = os.path.splitext(filename)
    if ((fext == '.gz') or (fext == '.GZ')):
        with gzip.open(filename) as fp:
            timestring = fp.readline().strip().split()[1]
        timestring=timestring.decode('utf-8')
    else:
        with open(filename) as fp:
            timestring = fp.readline().strip().split()[1]
    #if verbose: print('timestring = ',timestring)
    print('%s %s'%(filename, timestring))
    time=float(timestring.replace(',',''))
    return time

def getHeaders(filename):
    fname, fext = os.path.splitext(filename)
    if ((fext == '.gz') or (fext == '.GZ')):
        with gzip.open(filename) as fp:
            timestring = fp.readline().strip().decode('utf-8').split()[1]
            headers    = fp.readline().strip().decode('utf-8').split()[1:]
    else:
        with open(filename) as fp:
            timestring = fp.readline().strip().split()[1]
            headers    = fp.readline().strip().split()[1:]
    time=float(timestring.replace(',',''))
    return headers

# Get the list of files and times
allfiles=sorted(glob.glob(plane_files.replace(os.sep, '/')))
print(allfiles)
timeSteps = [getFileTime(x) for x in allfiles]

outInfo = self.GetOutputInformation(0)
if outInfo.Has(vtk.vtkStreamingDemandDrivenPipeline.UPDATE_TIME_STEP()):
  time = outInfo.Get(vtk.vtkStreamingDemandDrivenPipeline.UPDATE_TIME_STEP())
else:
  time = 0

# Get the list of planes to plot
if plane_chooser.strip().upper() == 'ALL':
    planes = []
else:
    planes = [int(x) for x in plane_chooser.strip().replace(',',' ').split()]

if verbose: print('Planes to plot: ', planes)

# Find the file that corresponds to that time
index=np.abs(np.array(timeSteps)-time).argmin()
print('Loading file: ',allfiles[index])
makePlane(allfiles[index], planes=planes)
