#!/usr/bin/env python

import numpy as np
import sys, os
import argparse
import gzip
import threading
import time

import avgSamplePlanes as avgplane

globali = 0

def avgPlanes(filelist, savefile, lock, Ntotal, coordfile='', getheaders=False, skiprows=2, progressbar=None):
    global globali
    """
    Average sample planes
    """
    Nfiles=len(filelist)
    for ip, planefile in enumerate(filelist):
        if progressbar=='file' or progressbar=='both':
            lock.acquire()
            print(planefile)
            lock.release()
        if progressbar=='bar' or progressbar=='both':
            lock.acquire()
            globali += 1
            avgplane.progress(globali, Ntotal, suffix='[%i/%i]'%(globali,Ntotal))
            lock.release()
        #if progressbar: progress(ip+1, Nfiles, suffix='[%i/%i]'%(ip+1,Nfiles))
        #if progressbar: print(planefile)
        if ip==0:
            alldat =  np.loadtxt(planefile, skiprows=skiprows)
        else:
            alldat += np.loadtxt(planefile, skiprows=skiprows)
    #if progressbar=='bar': print("")
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
    # Save the result
    headerinfo='%s to %s'%(filelist[0], filelist[-1])
    avgplane.saveavg(returndat, headers, savefile, headerinfo=headerinfo)
    #return avgdat, []

def avgThread(filelist, savefile, lock, Ntotal, coordfile='', getheaders=False, 
              skiprows=2, progressbar='bar'):
    #print("Thread starting %s"%savefile)
    avgPlanes(filelist, savefile, lock, Ntotal,
              coordfile=coordfile, 
              getheaders=getheaders, skiprows=skiprows, 
              progressbar=progressbar)
    # dat, headers=avgplane.avgPlanes(filelist, coordfile=coordfile, 
    #                                 getheaders=getheaders, skiprows=skiprows, 
    #                                 progressbar=progressbar)
    # lock.acquire()
    # #avgplane.saveavg(dat, headers, savefile)
    # lock.release()
    #print("Thread finished %s"%savefile)
    

def parallelAvgPlanes(filelist, nthreads, savefile,
                      coordfile='', tempfileformat='tempfile_{iter}.dat.gz',
                      getheaders=False, verbose=False,
                      skiprows=2, progressbar=None, deletetemp=False):
    global globali

    def splitlist(a, n):
        k, m = divmod(len(a), n)
        return [a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n)]

    # First make sure that the filelist is divisible
    Nfilelist = len(filelist)
    if Nfilelist % nthreads != 0:
        print("Num files = %i"%Nfilelist)
        print("Nthreads  = %i"%nthreads)
        print("ERROR: not divisible")
        return
    Nchunks = Nfilelist/nthreads
    
    splitfilelist = splitlist(filelist, nthreads)
    tempfilenames = [tempfileformat.format(iter=i) for i in range(nthreads)]

    globali = 0

    # Launch threads
    threads = list()
    lock= threading.Lock()
    for i in range(nthreads):
        if verbose: print("Thread %i: %s"%(i, tempfilenames[i]))
        t = threading.Thread(target=avgThread, 
                             args=(splitfilelist[i], tempfilenames[i], lock,
                                   Nfilelist),
                             kwargs={'coordfile':coordfile, 
                                     'getheaders':getheaders, 
                                     'skiprows':skiprows, 
                                     'progressbar':progressbar, 
                                 })
        threads.append(t)
        if verbose: print("Starting thread %i"%i)
        t.start()

    # Collect all threads
    for index, thread in enumerate(threads):
        thread.join()
        if verbose: print("Closing thread %i"%index)
        
    # Average over the averages
    print("")
    print("Averaging over temp avg files")
    avgdat, headers=avgplane.avgPlanes(tempfilenames, getheaders=True, progressbar=progressbar)
    headerinfo='%s to %s'%(filelist[0], filelist[-1])
    avgplane.saveavg(avgdat, headers, savefile, headerinfo=headerinfo)

    if deletetemp:
        for tfile in tempfilenames:
            os.remove(tfile)
