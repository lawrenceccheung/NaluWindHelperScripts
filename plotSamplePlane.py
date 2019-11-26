#!/usr/bin/env python

from numpy import *
import matplotlib
import matplotlib.pyplot as plt
import sys
import argparse

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
    
def getplotplane(dat, planenum, col):
    Numj      = int(max(dat[:,1]))+1
    Numi      = int(max(dat[:,2]))+1

    planedat=dat[dat[:,0]==planenum,:]
    plotplane=planedat[:,[1,2,col]]

    # Get the corner point
    cornerrow =planedat[(planedat[:,1]==0)&(planedat[:,2]==0),:][0][3:6]
    dxrow     =planedat[(planedat[:,1]==0)&(planedat[:,2]==1),:][0][3:6]
    dyrow     =planedat[(planedat[:,1]==1)&(planedat[:,2]==0),:][0][3:6]
    #print cornerrow
    #print dxrow
    #print dyrow
    dX=linalg.norm(array(dxrow)-array(cornerrow))
    dY=linalg.norm(array(dyrow)-array(cornerrow))

    # Get the X, Y, Z arrays
    Y=reshape(plotplane[:,0], (Numj, Numi))*dY
    X=reshape(plotplane[:,1], (Numj, Numi))*dX
    Z=reshape(plotplane[:,2], (Numj, Numi))
    return X, Y, Z

# Handle arguments
parser = argparse.ArgumentParser(description='Plot sample mesh')
parser.add_argument('PLANEFILE',  nargs='+',   help="Plot this sample plane")
parser.add_argument('--planenum', default=0,   help="Plot this plane number")
parser.add_argument('--varnum',   default=6,   help="Plot this variable number")
args=parser.parse_args()

# Get the default and user arguments
planefile=args.PLANEFILE[0]
planenum=int(args.planenum)
plotcol=int(args.varnum)


dat, time, headers=loadplanefile(planefile)
X,Y,Z=getplotplane(dat, planenum, plotcol)
plt.contourf(X, Y, Z)
plt.colorbar()
#plt.plot(X, Y, '.k') # Plot the mesh grid
plt.axis('equal')
plt.title('Time = %.3f %s'%(time, headers[plotcol]))
plt.show()
