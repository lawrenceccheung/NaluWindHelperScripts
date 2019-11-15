# Nalu-Wind Helper Scripts

Scripts to help with Nalu-Wind

**Contents**
- [Plot mesh script](#plot-mesh-refinement): [plotmesh.py](plotmesh.py)
- [Mesh refinement script](#mesh-refinement-script): [buildrefinemesh.sh](buildrefinemesh.sh)
- [Slice mesh utility](#slice-mesh-utility): [slicemesh.sh](slicemesh.sh)
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

```
buildrefinemesh.sh YAMLFILE [OPTIONS]

Arguments
  YAMFILE   : a yaml file containing the mesh definitions

Options: 
  -o|--output-mesh OUTFILE  : Output filename (default: refinedmesh.exo)
  -n|--ncores      NPU      : Number of cores to use (default: 8)
  --no-createmesh           : Do not create basic mesh
  --no-preproc              : Do not use the preprocessor to define mesh refinem ent zones
  --no-refine               : Do not use mesh_adapt to refine mesh
  -h|--help                 : This help file

```
The argument `YAMLFILE` should point to a yaml input file like this:  
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

When you execute the script, for instance
```bash
$ ./buildrefinemesh.sh testmesh.yaml -o testmesh.exo
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

At the very end, it will copy over the final mesh and report the new mesh blocks which are included:
```
‘tempmesh2.e’ -> ‘testmesh.exo’

New mesh blocks: 
 eb_names =
  "fluid_part",
  "fluid_part.pyramid_5._urpconv",
  "fluid_part.tetrahedron_4._urpconv",
  "fluid_part.pyramid_5._urpconv.Tetrahedron_4._urpconv" ;
}
```

## Slice mesh utility
**[slicemesh.sh](slicemesh.sh): Creates the slice geometry for a mesh**  
#### Usage
```bash
./slicemesh.sh MESHYAMLFILE [OPTIONS]
```
where MESHYAMLFILE is the yaml file containing the slice mesh parameters.

Optional Arguments:
```bash
  -y|--yaml-output YAMLFILE    Print out the corresponding yaml inputs needed to include the slice mesh 
                               output during the simulation.  YAMLFILE is the main simulation yamlfile
  -v|--extra-vars  VARLIST     An extra list of variables to include when writing out the sliced meshes.
                               VARLIST is of the form "var1:N var2:N ..." where var1, var2, are the
                               variable names, and N is the number of components for that variable
```

The MESHYAMLFILE input file defining the slices to take:
```yaml
slice_mesh:
  output_db: temp.exo # sliceplanes.exo

  slices:
    # X-Y plane
    - axis1: [1.0, 0.0, 0.0]
      axis2: [0.0, 1.0, 0.0]
      axis3: [0.0, 0.0, 1.0]
      origin: [0.0, 0.0, 0.0]
      grid_lengths: [2500.0, 2500.0]
      grid_dx: [4.0, 4.0]
      num_planes: 1
      plane_offsets: [0.0]
      part_name_prefix: turbineHH

    # Y-Z plane 
    - axis1: [1.0, 1.0, 0.0]
      axis2: [0.0, 0.0, 1.0]
      axis3: [-1,  1.0, 0.0]
      origin: [0.0, 00, -100.0]
      grid_lengths: [3000.0, 200.0]
      grid_dx: [4.0, 4.0]
      num_planes: 1
      plane_offsets: [0.0]
      part_name_prefix: turbineSlice2

```

If you execute it with the input files:
```bash
$ slicemesh.sh mesh1.yaml 
yamlfile    = mesh1.yaml
simyamlfile = 
extravars   = 
Loading modules
Output mesh name = temp.exo
Slice Mesh Generation Utility
Input file: mesh1.yaml
Loading slice inputs... 
Initializing slices... 
Slice: Registering parts to meta data: 
  -  turbineHH_1
Slice: Registering parts to meta data: 
  -  turbineSlice2_1
Generating slices for: turbineHH
Creating nodes... 10% 20% 30% 40% 50% 60% 70% 80% 90% 100% 
Creating elements... 10% 20% 30% 40% 50% 60% 70% 80% 90% 100% 
Generating coordinate field
 - turbineHH_1
Generating slices for: turbineSlice2
Creating nodes... 10% 20% 30% 40% 50% 60% 70% 80% 90% 100% 
Creating elements... 10% 20% 30% 40% 50% 60% 70% 80% 90% 100% 
Generating coordinate field
 - turbineSlice2_1
Writing mesh to file: temp.exo

Memory usage: Avg:  156.043 MB; Min:  156.043 MB; Max:  156.043 MB
```

If you execute it with the `-y` option, like `slicemesh.sh
mesh1test.yaml -y alm_simulation.yaml`, then some additional output will be generated:
```bash
# === Auto-generated YAML below ======

# Goes under [realms:]
- name: ioRealm
  mesh: temp.exo
  type: input_output
  automatic_decomposition_type: rcb

  field_registration:
    specifications:
    - field_name: velocity_slice
      target_name: &fieldreg [ turbineHH_1, turbineSlice2_1 ]
      field_size: 3
      field_type: node_rank
  output:
    output_data_base_name: ./sliceDataInstantaneous/temp.exo
    output_frequency: 1
    output_node_set: no
    output_variables:
    - velocity_slice
transfers:
- name: turbineHH_1
  type: geometric
  realm_pair: [realm_1, ioRealm]
  to_target_name: turbineHH_1
  from_target_name: ['fluid_part', 'fluid_part.Pyramid_5._urpconv', 'fluid_part.Tetrahedron_4._urpconv']
  objective: input_output
  transfer_variables:
  - [velocity, velocity_slice]
- name: turbineSlice2_1
  type: geometric
  realm_pair: [realm_1, ioRealm]
  to_target_name: turbineSlice2_1
  from_target_name: ['fluid_part', 'fluid_part.Pyramid_5._urpconv', 'fluid_part.Tetrahedron_4._urpconv']
  objective: input_output
  transfer_variables:
  - [velocity, velocity_slice]

# === End auto-generated YAML ======
```

These yaml parameters can be added to `alm_simulation.yaml` to extract
the slice during simulations.

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

## Backup and write a restart YAML file
**[restartbackupnalu.py](restartbackupnalu.py): Backups up a simulation from a YAML file**
#### Usage
```bash
usage: restartbackupnalu.py [-h] [--dobackup] [--Nsteps NSTEPS]
                            [--suffix SUFFIX]
                            yamlfile [yamlfile ...]

Create a restart YAML file for Nalu.

positional arguments:
  yamlfile

optional arguments:
  -h, --help       show this help message and exit
  --dobackup       Backup files [default=False]
  --Nsteps NSTEPS  Run another NSTEPS
  --suffix SUFFIX  Suffix to attach to backup files [default is date/time
                   based suffix]

```
