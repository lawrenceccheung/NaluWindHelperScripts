# Nalu-Wind Helper Scripts

Scripts to help with Nalu-Wind

**Contents**
- [buildrefinemesh.sh](#buildrefinemesh-sh)
- [plotmesh.py](#plotmesh-py)
- [plotFAST.py](#plotfast-py)

## buildrefinemesh.sh
**Creates a mesh, does local refinement**

Requires an yaml input file like this:  
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
#  - init_abl_fields

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
    refinement_levels:
      - [ 7.0, 12.0, 7.0, 7.0 ]
      - [ 5.0, 10.0, 5.0, 5.0 ]
      - [ 3.0, 6.0, 3.0, 3.0 ]
#      - [ 1.5, 3.0, 1.2, 1.2 ]

```

## plotmesh.py
**Plots the mesh refinement levels**

## plotFAST.py
**Plots FAST output**