import glob, os
import gzip

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
    #print('timestring = ',timestring)
    time=float(timestring.replace(',',''))
    return time

allfiles=sorted(glob.glob(plane_files.replace(os.sep, '/')))
if verbose: print(allfiles)
print('Loading timesteps from files')
timeSteps = [getFileTime(x) for x in allfiles]
if verbose: print(timeSteps)
 
if len(timeSteps)>0:
    outInfo = self.GetOutputInformation(0)
    
    timeRange = [timeSteps[0], timeSteps[-1]]
    outInfo.Set(vtk.vtkStreamingDemandDrivenPipeline.TIME_RANGE(), timeRange, 2)
    outInfo.Set(vtk.vtkStreamingDemandDrivenPipeline.TIME_STEPS(), timeSteps, len(timeSteps))
