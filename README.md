# Nalu-Wind Helper Scripts

Scripts to help with Nalu-Wind

**Contents**
- [Plot mesh script](#plot-mesh-refinement): [plotmesh.py](plotmesh.py)
- [Mesh refinement script](#mesh-refinement-script): [buildrefinemesh.sh](buildrefinemesh.sh)
- [Plot FAST output script](#plot-fast-output): [plotFAST.py](plotFAST.py)

## Plot mesh refinement
**[plotmesh.py](plotmesh.py): Plots the mesh refinement levels, turbine locations, and cut-slices**  
#### Usage
```bash
$ module load canopy
$ plotmesh.py YAMLFILE
```
Here `YAMLFILE` is a yaml file containing the mesh definition, refinement windows, and (optionally) the slice mesh parameters.

Output:  
![image](https://gitlab.sandia.gov/uploads/-/system/personal_snippet/542/c9fd9123b82f1f19452878e0e1c05a0a/image.png)

Each different colored rectangle represents a halving of the mesh resolution (8x refinement).  The arrow in the middle of the domain points in the wind direction.

If you include the `slice_mesh` section in the YAML file, then it will also include the areas where the sections are being taken, like this:  
![image](https://gitlab.sandia.gov/uploads/-/system/personal_snippet/542/9092a382b8f005629ebd69dc216d8f0c/image.png)

## Mesh refinement script
**[buildrefinemesh.sh](buildrefinemesh.sh): Creates a mesh, does local refinement**
#### Usage
Edit the beginning of the file with the input variables (Change this later to be more flexible)
```bash
yamlfile=abl_preprocess.yaml
outputmesh=refinedmesh.exo
NCORES=8
CREATEMESH=true
RUNNALUPREPROC=true
RUNREFINE=true
NALUUTILDIR=~/nscratch/buildNalu/Nalu_intel/install/intel/nalu-wind/bin/
```
The variable `yamlfile` should point to a yaml input file like this:  
```yaml
nalu_abl_mesh:
  output_db: mesh_abl.exo
  spec_type: bounding_box
  fluid_part_name: fluid_part

  vertices:
  - [0.0, 0.0, 0.0]
  - [1000.0, 1000.0, 300.0]
  mesh_dimensions: [100, 100, 30]

  xmin_boundary_name: west
  xmax_boundary_name: east
  ymin_boundary_name: south
  ymax_boundary_name: north
  zmin_boundary_name: lower
  zmax_boundary_name: upper

# Mandatory section for Nalu preprocessing
nalu_preprocess:
  # Name of the input exodus database
  input_db: mesh_abl.exo
  # Name of the output exodus database
  output_db: mesh_abl.exo

  # Nalu preprocessor expects a list of tasks to be performed on the mesh and
  # field data structures
  tasks:
    - mesh_local_refinement

  mesh_local_refinement:
    fluid_parts: [fluid_part]
    write_percept_files: true
    percept_file_prefix: adapt
    search_tolerance: 11.0
    turbine_locations:
      - [ 200.0, 200.0, 0.0 ]
      - [ 230.0, 300.0, 0.0 ]
    turbine_diameters: 15.0        # Provide a list for variable diameters
    turbine_heights: 50.0          # Provide a list for variable tower heights
    orientation:
      type: wind_direction
      wind_direction: 225.0
    refinement_levels:             # Numbers are for upstream, downstream, lateral and vertical length in turbine diameters
      - [ 7.0, 12.0, 7.0, 7.0 ]
      - [ 5.0, 10.0, 5.0, 5.0 ]
      - [ 3.0, 6.0, 3.0, 3.0 ]
```

When you execute the script,
```bash
$ ./buildrefinemesh.sh
```
the first stage should be the mesh creation part
```
Nalu ABL Mesh Generation Utility
Input file: testmesh.yaml
HexBlockBase: Registering parts to meta data
	Mesh block: fluid_part
Num. nodes = 41616; Num elements = 37500
	Generating nodes...done
	Generating elements...done
	Creating element connectivity... done
	Generating X Sideset: west
	Generating X Sideset: east
	Generating Y Sideset: south
	Generating Y Sideset: north
	Generating Z Sideset: lower
	Generating Z Sideset: upper
	Finalizing bulk data modifications ... done
	Generating coordinates...
	 Generating x spacing: constant_spacing
	 Generating y spacing: constant_spacing
	 Generating z spacing: constant_spacing
Writing mesh to file: mesh_abl.exo
```
Followed by the preprocessing stage which marks out areas for local refinement:
```
Nalu Preprocessing Utility
Input file: testmesh.yaml
Found 1 tasks
    - mesh_local_refinement

Performing metadata updates... 
Metadata update completed
Reading mesh bulk data... done.

--------------------------------------------------
Begin task: mesh_local_refinement
```
Then it will run mesh_adapt through the multiple stages of refinement:
```
Running mesh refinement step
------------------
STAGE 1 REFINEMENT: tempmesh0.e --> tempmesh1.e
------------------
mpirun -n 8 mesh_adapt --refine=DEFAULT --input_mesh=tempmesh0.e --output_mesh=tempmesh1.e --RAR_info=adapt1.yaml --ioss_read_options="auto-decomp:yes" 
INFO: ioss_read_options=auto-decomp:yes ioss_write_options=
PerceptMesh:: opening tempmesh0.e

Using decomposition method 'RIB' on 8 processors.

```

## Plot FAST output
**[plotFAST.py](plotFAST.py): Plots FAST output**  
#### Usage  
```bash
$ module load canopy
$ plotFAST.py FAST.T1.out [FAST.T2.out  ... ]
```
Output:  
![image](https://gitlab.sandia.gov/uploads/-/system/personal_snippet/542/8f0b2d522459db26ee33962f8a36559f/image.png)

It's pretty self-explanatory.  Check the variables on the left you would like to plot, and hit `Plot`.
If the output files get updated, hit `Reload data` to reread the files from disk.
