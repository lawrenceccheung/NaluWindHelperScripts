import os, json
import sys
import numpy as np
import paraview.simple as pvs
import tempfile

# NOTE NOTE NOTE: do not use the double-quotation mark in this file.
# it will mess up the xml embedding. Single quotes are fine.

def makeBox(pdo, v1, v2):
    points = vtk.vtkPoints()
    x1 = v1[0]
    y1 = v1[1]
    z1 = v1[2]
    x2 = v2[0]
    y2 = v2[1]
    z2 = v2[2]

    points.InsertPoint(0, x1, y1, z1)  #A
    points.InsertPoint(1, x1, y1, z2)  #B
    points.InsertPoint(2, x1, y2, z2)  #C
    points.InsertPoint(3, x1, y2, z1)  #D

    points.InsertPoint(4, x2, y1, z1)  #E
    points.InsertPoint(5, x2, y1, z2)  #F
    points.InsertPoint(6, x2, y2, z2)  #G
    points.InsertPoint(7, x2, y2, z1)  #H

    #pdo = self.GetPolyDataOutput()
    pdo.SetPoints(points)
    pdo.Allocate(8, 4)

    rect = vtk.vtkPolygon()
    rect.GetPointIds().SetNumberOfIds(4)

    faces = [[0,1,2,3], [0,1,5,4], [3,2,6,7], [4,5,6,7], [0,4,7,3],[1,5,6,2]]
    #rectpts = [0,1,2,3]
    for rectpts in faces:
        for p in range(0, 4):
            rect.GetPointIds().SetId(p, rectpts[p])
        pdo.InsertNextCell(rect.GetCellType(), rect.GetPointIds())
    
def makeSamplePlane(cornerpt, edge1, edge2, Nx, Ny, name=''):
    # create a new 'Plane'
    plane1 = pvs.Plane()

    # Properties modified on plane1
    plane1.Origin = cornerpt
    plane1.Point1 = cornerpt+edge1
    plane1.Point2 = cornerpt+edge2
    plane1.XResolution = Nx
    plane1.YResolution = Ny
    if (len(name)>0):
        # rename source object
        pvs.RenameSource(name, plane1)
    return plane1

def makeLineOfSight(p1, p2, resolution, name=''):
    # create a new 'Line'
    line1 = pvs.Line()
    # Properties modified on line1
    line1.Point1 = p1
    line1.Point2 = p2
    line1.Resolution = resolution
    if (len(name)>0):
        # rename source object
        pvs.RenameSource(name, line1)
    return line1

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

def plotTower(basexy, height, name):
    # Define some constants
    towerres = 30
    towerR   = 1.5
    # create a new 'Cylinder'
    towercyl = pvs.Cylinder()
    # Properties modified on cylinder1
    towercyl.Height = height
    towercyl.Resolution = towerres
    towercyl.Radius = towerR
    towercyl.Center = [0,0,0]
    # create a new 'Transform'
    transcyl = pvs.Transform(Input=towercyl)
    transcyl.Transform = 'Transform'
    # Properties modified on transform1.Transform
    transcyl.Transform.Translate = [basexy[0], basexy[1], basexy[2]+0.5*height]
    transcyl.Transform.Rotate = [90.0, 0.0, 0.0]
    #towercyl.RenameSource(name+'_tower_temp', towercyl)
    pvs.RenameSource(name+'_tower', transcyl)
    return

def plotNacelle(basexy, height, NacYaw, name):
    # Define some constants
    nacellewidth  = 5    
    nacellelength = 15
    # create a new nacelle
    nacellebox = pvs.Box()
    nacellebox.XLength = nacellelength
    nacellebox.YLength = nacellewidth
    nacellebox.ZLength = nacellewidth
    nacellebox.Center  = [0.5*nacellelength,0,0] #[basexy[0], basexy[1], basexy[2]+height]
    transnacelle       = pvs.Transform(Input=nacellebox)
    transnacelle.Transform.Translate = [basexy[0], basexy[1], basexy[2]+height] #[0.3*nacellelength, 0, 0]
    transnacelle.Transform.Rotate = [0.0, 0.0, NacYaw]
    pvs.RenameSource(name+'_nacelle', transnacelle)
    return

def plotRotorDisk(hubxy, turbR, NacYaw, name):
    # Define some constants
    rotorres     = 30
    rotorthick   = 1
    # create a new 'Cylinder'
    rotordisk = pvs.Cylinder()
    rotordisk.Height     = rotorthick
    rotordisk.Resolution = rotorres
    rotordisk.Radius     = turbR
    #rotordisk.Center     = hubxy
    # create a new 'Transform'
    rotortrans = pvs.Transform(Input=rotordisk)
    rotortrans.Transform = 'Transform'
    rotortrans.Transform.Translate = hubxy
    rotortrans.Transform.Rotate = [0.0, 0.0, 90+NacYaw]
    pvs.RenameSource(name+'_rotordisk', rotortrans)
    return

def plotTurbine(hubxy, basexy, turbR, NacYaw, name):
    # Some constants
    towerres      = 100   # Resolution for tower
    nacellelength = 7.5

    # --- Plot the tower ---
    towerheight = hubxy[2] - basexy[2]
    plotTower(basexy, towerheight, name)
    # towerline = pvs.Line()
    # towerline.Point1 = basexy
    # towerline.Point2 = np.array(basexy) + towerheight*np.array([0,0,1])
    # towerline.Resolution = towerRes
    # pvs.RenameSource(name+'_tower', towerline)
    # --- Plot the nacelle ---
    plotNacelle(basexy, towerheight, NacYaw, name)
    # --- Plot the rotor disk ---
    plotRotorDisk(hubxy, turbR, NacYaw, name)
    # --- Group the datasets together ---
    turbine0_rotordisk = pvs.FindSource(name+'_rotordisk')
    turbine0_nacelle = pvs.FindSource(name+'_nacelle')
    turbine0_tower = pvs.FindSource(name+'_tower')
    groupDatasets1 = pvs.GroupDatasets(Input=[turbine0_rotordisk, turbine0_nacelle, turbine0_tower])
    pvs.RenameSource(name+'_allobjects', groupDatasets1)    
    return

def checkfilepath(filename, basepath):
    if (filename[0]=='/'): # Absolute path, do nothing
        return filename
    else:
        return basepath+'/'+filename

def checkfileexists(filename):
    if os.path.isfile(filename):
        return True
    else:
        print('WARNING: file does not exist: %s'%filename, file=sys.stderr)        
        return False

def fixslash(filename):
    return filename.replace(os.sep, '/')

debug=verbose

# Quit if there's nothing in yaml_file yet
if (len(yaml_file)==0): return

basepath=fixslash(os.path.dirname(fixslash(yaml_file)))

tempf      =tempfile.NamedTemporaryFile(mode='w+t', suffix='.py', delete=False)
temppyfile =tempf.name #basepath+'/tempexec.py'
pythonexe=fixslash(python_exe)


# Read the yaml file, convert it to json, and read that as a string
filestring='import json, yaml, sys; f=open(\\\'%s\\\'); data=yaml.load(f);  sys.stdout.write(json.dumps(data, indent=2));'
#f=open(temppyfile, 'w')
tempf.writelines(filestring%fixslash(yaml_file))
tempf.seek(0)
tempf.flush()
tempf.close()

#f.close()

if debug:
    print('\npython exe is %s'%pythonexe, file=sys.stderr)
    print('\ntemp py file is %s'%temppyfile, file=sys.stderr)

#print(filestring)
#stream=os.popen('%s %s; rm %s'%(python_exe, temppyfile, temppyfile))
stream=os.popen('%s %s'%(pythonexe, temppyfile))
#stream=os.popen('python tempexec.py; rm tempexec.py')
#stream=os.popen('python tempexec.py')
#stream=os.popen(cmdstring)
output=stream.read()
if debug:
    print('Output of exe is:\n', file=sys.stderr)
    print(output+'\n', file=sys.stderr)
data=json.loads(output)
#print(json.dumps(data, indent=2))


pdo = self.GetPolyDataOutput()

#plotdomain=True
if ((plotablmesh) and ('nalu_abl_mesh' in data) ):
    print(data['nalu_abl_mesh'])
    v1 = data['nalu_abl_mesh']['vertices'][0]
    v2 = data['nalu_abl_mesh']['vertices'][1]
    print(v1)
    print(v2)
    makeBox(pdo, v1,v2)

#pdo2 = self.GetPolyDataOutput()
#makeBox(pdo2, [0,0,0],[10,10,10])

#plotexomesh = True
if ((plotexomesh) and ('mesh' in data['realms'][0])):
    inputmeshfilename = data['realms'][0]['mesh']
    # Double check and santize meshfilename
    root_ext = os.path.splitext(inputmeshfilename)
    if (len(root_ext)>1):
        if ((root_ext[1] != '.exo') and (root_ext[1] != '.e')):
            print('Cannot load exo mesh from: %s'%inputmeshfilename, file=sys.stderr)        
            print('Possibly not an exodus file', file=sys.stderr)
            plotexomesh = False
    meshfilename = checkfilepath(fixslash(inputmeshfilename), basepath)
    if (not checkfileexists(meshfilename)):
        print('Cannot load exo mesh from: %s'%meshfilename, file=sys.stderr)        
        plotexomesh = False
    if plotexomesh:
        print('Loading exo mesh from: %s'%meshfilename)
        meshexo = pvs.ExodusIIReader(FileName=[meshfilename])
        pvs.RenameSource(meshfilename, meshexo)    
    
#plotdataprobes=True
if ((plotdataprobes) and ('data_probes' in data['realms'][0])):
    data_probe_specs=data['realms'][0]['data_probes']['specifications']
    # Stuff
    for spec in data_probe_specs:
        if 'plane_specifications' in spec:
            for plane in spec['plane_specifications']:
                name   = plane['name']
                corner = np.array(plane['corner_coordinates'])
                edge1  = np.array(plane['edge1_vector'])
                edge2  = np.array(plane['edge2_vector'])
                Nx     = plane['edge1_numPoints']-1
                Ny     = plane['edge2_numPoints']-1
                offsetvec   = np.array([0,0,0])
                offsetspace = [0]
                if (('offset_vector' in plane) and ('offset_spacings' in plane)):
                    offsetvec   = np.array(plane['offset_vector'])
                    offsetspace = np.array(plane['offset_spacings'])
                for si, s in enumerate(offsetspace):
                    planename = name+'_'+repr(si)
                    newcorner = corner + s*offsetvec
                    makeSamplePlane(newcorner, edge1, edge2, Nx, Ny, name=planename)
        if 'line_of_site_specifications' in spec:
            for line in spec['line_of_site_specifications']:
                name    = line['name']
                Npoints = line['number_of_points']
                tip     = line['tip_coordinates']
                tail    = line['tail_coordinates']
                makeLineOfSight(tail, tip, Npoints-1, name=name)
            

# Plot the turbines
if (plotturbines and 'actuator' in data['realms'][0]):
    nturbs = data['realms'][0]['actuator']['n_turbines_glob']
    actuatorsection = data['realms'][0]['actuator']
    print('nturbs = ',nturbs)
    # Loop through all of the turbines
    for iturb in range(nturbs):
        turbname = 'Turbine'+repr(iturb)
        turbxy   = actuatorsection[turbname]['turbine_hub_pos']
        basexy   = actuatorsection[turbname]['turbine_base_pos']
        fastfile = actuatorsection[turbname]['fast_input_filename']
        loadfastfile = checkfilepath(fixslash(fastfile), basepath)
        fstbasepath=os.path.dirname(loadfastfile)
        EDFile=fixslash(checkfilepath(eval(readFASTfile(loadfastfile, 'EDFile')), fstbasepath))
        TipRad=float(readFASTfile(EDFile, 'TipRad'))
        NacYaw=float(readFASTfile(EDFile, 'NacYaw'))
        print(EDFile, TipRad, NacYaw)
        # Plot the turbines
        plotTurbine(turbxy, basexy, TipRad, NacYaw, turbname)
