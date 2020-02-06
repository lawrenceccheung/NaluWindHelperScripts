import os, json
import numpy as np
import paraview.simple as pvs

def makeBox(v1, v2):
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

    pdo = self.GetPolyDataOutput()
    pdo.SetPoints(points)
    pdo.Allocate(4, 4)

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

filestring='import json, yaml, sys; f=open(\\\'%s\\\'); data=yaml.load(f, Loader=yaml.FullLoader);  sys.stdout.write(json.dumps(data, indent=2));'
f=open('tempexec.py', 'w')
f.write(filestring%yaml_file)
f.close()

#print(filestring)
stream=os.popen('python tempexec.py; rm tempexec.py')
#stream=os.popen(cmdstring)
output=stream.read()
data=json.loads(output)
#print(json.dumps(data, indent=2))

plotdomain=True
if ((plotdomain) and ('nalu_abl_mesh' in data) ):
    print(data['nalu_abl_mesh'])
    v1 = data['nalu_abl_mesh']['vertices'][0]
    v2 = data['nalu_abl_mesh']['vertices'][1]
    print(v1)
    print(v2)
    makeBox(v1,v2)
    
#plotdataprobes=True
if ((plotdataprobes) and ('data_probes' in data['realms'][0])):
    data_probe_specs=data['realms'][0]['data_probes']['specifications']
    for spec in data_probe_specs:
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
                planename = name+repr(si)
                newcorner = corner + s*offsetvec
                makeSamplePlane(newcorner, edge1, edge2, Nx, Ny, name=planename)
        for line in spec['line_of_site_specifications']:
            name    = line['name']
            Npoints = line['number_of_points']
            tip     = line['tip_coordinates']
            tail    = line['tail_coordinates']
            makeLineOfSight(tail, tip, Npoints-1, name=name)
            
