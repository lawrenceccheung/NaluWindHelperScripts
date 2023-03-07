#!/usr/bin/env python
#

import numpy as np
import sys, os
import argparse
import gzip

# See https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
def progress(count, total, suffix=''):
    """
    print out a progressbar
    """
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))
    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)
    sys.stdout.write('[%s] %s%s %s\r' % (bar, percents, '%', suffix))
    sys.stdout.flush()  

def avgPlanes(filelist, coordfile='', getheaders=False, skiprows=2, progressbar=True):
    """
    Average sample planes
    """
    Nfiles=len(filelist)
    for ip, planefile in enumerate(filelist):
        if progressbar: progress(ip+1, Nfiles, suffix='[%i/%i]'%(ip+1,Nfiles))
        if ip==0:
            alldat =  np.loadtxt(planefile, skiprows=skiprows)
        else:
            alldat += np.loadtxt(planefile, skiprows=skiprows)
    if progressbar: print("")
    avgdat=alldat/Nfiles
    # Add the coordinates if necessary
    if len(coordfile)>0:
        cdat=np.loadtxt(coordfile, skiprows=skiprows)
        returndat = np.hstack((cdat, avgdat))
    else:
        returndat = avgdat
    # Get the headers if necessary
    headers=[]
    if getheaders:
        fname, fext = os.path.splitext(filelist[0])
        # Load the headers from the coordfile
        if len(coordfile)>0:
            if ((fext == '.gz') or (fext == '.GZ')):
                with gzip.open(coordfile) as fp:
                    junk = fp.readline().strip().split()[1]
                    headers.extend(fp.readline().strip().split()[1:])
            else:
                with open(coordfile) as fp:
                    junk = fp.readline().strip().split()[1]
                    headers.extend(fp.readline().replace('#','').strip().split()[:])        
        # Else just use the one file headers
        if ((fext == '.gz') or (fext == '.GZ')):
            with gzip.open(filelist[0]) as fp:
                timestring = fp.readline().strip().split()[1]
                headers.extend(fp.readline().strip().split()[1:])
        else:
            with open(filelist[0]) as fp:
                timestring = fp.readline().strip().split()[1]
                headers.extend(fp.readline().replace('#','').strip().split()[:])
    # return everything
    return returndat, headers

def avgPlanesUU(filelist, avgdat, coordfile='', 
                getheaders=False, skiprows=2, progressbar=True):
    """
    Average sample planes
    """
    Nfiles=len(filelist)
    for ip, planefile in enumerate(filelist):
        if progressbar: progress(ip+1, Nfiles, suffix='[%i/%i]'%(ip+1,Nfiles))
        u = np.loadtxt(planefile, skiprows=skiprows)
        Ncols = u.shape[1]
        up = u - avgdat[:,-Ncols:]
        if ip==0:
            alldat =  up*up
        else:
            alldat += up*up
    if progressbar: print("")
    avgdat=alldat/Nfiles
    # Add the coordinates if necessary
    if len(coordfile)>0:
        cdat=np.loadtxt(coordfile, skiprows=skiprows)
        returndat = np.hstack((cdat, avgdat))
    else:
        returndat = avgdat
    # Get the headers if necessary
    headers=[]
    if getheaders:
        fname, fext = os.path.splitext(filelist[0])
        # Load the headers from the coordfile
        if len(coordfile)>0:
            if ((fext == '.gz') or (fext == '.GZ')):
                with gzip.open(coordfile) as fp:
                    junk = fp.readline().strip().split()[1]
                    headers.extend(fp.readline().strip().split()[1:])
            else:
                with open(coordfile) as fp:
                    junk = fp.readline().strip().split()[1]
                    headers.extend(fp.readline().strip().split()[1:])        
        # Else just use the one file headers
        if ((fext == '.gz') or (fext == '.GZ')):
            with gzip.open(filelist[0]) as fp:
                timestring = fp.readline().strip().split()[1]
                headers.extend(fp.readline().strip().split()[1:])
        else:
            with open(filelist[0]) as fp:
                timestring = fp.readline().strip().split()[1]
                headers.extend(fp.readline().replace('#','').strip().split()[:])
#            with open(filename) as fp:
#                timestring = fp.readline().strip().split()[1]
#                headers.extend(fp.readline().strip().split()[1:])
    # return everything
    return returndat, headers

def saveavg(avgdat, headers, savefile, headerinfo=''):
    # construct the headers
    colheaders=' '.join(headers)
    topheader='#Time: 0.0 AVERAGED PLANES '+headerinfo
    np.savetxt(savefile, avgdat, header=topheader+'\n# '+colheaders, comments='')
    return

def main():
    # Handle arguments
    parser = argparse.ArgumentParser(description='Average sample planes')
    parser.add_argument('PLANEFILE',      nargs='*',  help="Plot these sample plane(s)")
    parser.add_argument('--noprogressbar',    action='store_true',
			help="Do not display progress bar")
    parser.set_defaults(noprogressbar=False)
    parser.add_argument('--coordfile',    default='',  help="Specify coordinate file")
    parser.add_argument('--savefile',     default='',  help="Save averaged plane to this file")
    parser.add_argument('--headerinfo',   default='',  help="Add extra string to header")
    parser.add_argument('--skiprows',     help="Number of comment rows to skip in each datafile",
                        type=int, default=2)
    parser.add_argument('--filetemplate', default='',  help="Template for filenames")
    parser.add_argument('--iters',        help="Iterations to be used with --filetemplate argument",
                        type=int, nargs='+')

    # Get the default and user arguments
    args=parser.parse_args()
    filelist    = args.PLANEFILE
    progressbar = (not args.noprogressbar)
    coordfile   = args.coordfile
    savefile    = args.savefile
    skiprows    = args.skiprows
    headerinfo  = args.headerinfo
    filetemplate= args.filetemplate
    iters       = args.iters

    # Construct the filelist
    if (len(filetemplate)>0 and len(iters)>0):
        for i in iters: filelist.append(filetemplate%i)
    #print(filelist)
    #print(iters)
    # Average the data
    avgdat, headers=avgPlanes(filelist, coordfile=coordfile, skiprows=skiprows, getheaders=True, progressbar=progressbar)
    if len(savefile)>0:
        print('Saving '+savefile)
        saveavg(avgdat, headers, savefile, headerinfo=headerinfo)
    return

   
if __name__ == "__main__":
    # Call the main function
    main()
