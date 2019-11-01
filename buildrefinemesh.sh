#!/bin/sh

yamlfile=abl_preprocess.yaml
outputmesh=refinedmesh.exo
NCORES=8
CREATEMESH=true
RUNNALUPREPROC=true
RUNREFINE=true
NALUUTILDIR=~/nscratch/buildNalu/Nalu_intel/install/intel/nalu-wind/bin/

# Help for this script
function help() {
cat <<EOF
Usage: 
  $1 YAMLFILE [OPTIONS]

Arguments
  YAMFILE   : a yaml file containing the mesh definitions

Options: 
  -o|--output-mesh OUTFILE  : Output filename (default: $outputmesh)
  -n|--ncores      NPU      : Number of cores to use (default: $NCORES)
  --no-createmesh           : Do not create basic mesh
  --no-preproc              : Do not use the preprocessor to define mesh refinem ent zones
  --no-refine               : Do not use mesh_adapt to refine mesh
  -h|--help                 : This help file
EOF
}

# Parse the arguments and options
# --------------------------
# For arg parsing details/example, see https://medium.com/@Drew_Stokes/bash-argument-parsing-54f3b81a6a8f
PARAMS=""
while (( "$#" )); do
    case "$1" in
	-o|--output-mesh)
	    outputmesh=$2
	    shift 2
	    ;;
	-n|--ncores) 
	    NCORES=$2
	    shift 2
	    ;;
	--no-createmesh)
	    CREATEMESH=false
	    shift 
	    ;;
	--no-preproc) 
	    RUNNALUPREPROC=false
	    shift 
	    ;;
	--no-refine)
	    RUNREFINE=false
	    shift 
	    ;;
	-h|--help)
	    help $0
	    exit
	    ;;
	--) # end argument parsing
	    shift
	    break
	    ;;
	-*|--*=) # unsupported flags
	    echo "Error: Unsupported flag $1" >&2
	    exit 1
	    ;;
	*) # preserve positional arguments
	    PARAMS="$PARAMS $1"
	    shift
	    ;;
    esac
done # set positional arguments in their proper place
eval set -- "$PARAMS"
yamlfile=$1

echo "yamlfile   = $yamlfile"
echo "outputmesh = $outputmesh"
echo "NCORES     = $NCORES"
echo "CREATEMESH = $CREATEMESH"
echo "RUNNALUPREPROC=$RUNNALUPREPROC"
echo "RUNREFINE  = $RUNREFINE"
#exit 


# Load all of the stuff required to get Nalu up and running
echo "Loading modules"
module purge
module load intel/18.0.2.199 gnu/7.3.1 mkl/18.0.2.199  openmpi-intel/2.1
source /nscratch/lcheung/buildNalu/Nalu_intel/spack/share/spack/setup-env.sh
spack load boost; 
spack load netcdf; 
spack load hdf5
module load canopy

# Get the header needed to read the yaml file
read -r -d '' READYAMLHEADER << EOM
import yaml
with open('$yamlfile') as stream:
    try:
        yamldata=yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)
EOM

# Get the mesh output name
# ------
meshbasename=`python - <<DOC
$READYAMLHEADER
print yamldata['nalu_preprocess']['output_db']
DOC`
echo "Output mesh name = $meshbasename"

# Get the number of refinement levels
# -------
Nrefinement=`python - <<DOC
$READYAMLHEADER
print len(yamldata['nalu_preprocess']['mesh_local_refinement']['refinement_levels'])
DOC`
echo "Nrefinement = $Nrefinement"

# Get the adapt file names
percept_file_prefix=`python - <<DOC
$READYAMLHEADER
print yamldata['nalu_preprocess']['mesh_local_refinement']['percept_file_prefix']
DOC`
echo "percept_file_prefix = $percept_file_prefix"

# ------------------------
# Create the mesh
# ------------------------
if $CREATEMESH; then
    echo "Creating the mesh"
    $NALUUTILDIR/abl_mesh -i $yamlfile
fi

# ------------------------
# Run the preprocessor
# ------------------------
if $RUNNALUPREPROC; then
    echo "Running the preprocessor"
    $NALUUTILDIR/nalu_preprocess -i $yamlfile    
fi

# ------------------------
# Run the mesh refinement
# ------------------------
if $RUNREFINE; then
    echo "Running mesh refinement step"
    module purge
    module load sierra
    tempmesh=tempmesh
    # link the mesh file to the first one
    ln -s $meshbasename ${tempmesh}0.e
    for i in `seq 1 $Nrefinement`; do
	im1=$((i-1))
	meshprev=${tempmesh}${im1}.e
	meshnext=${tempmesh}${i}.e
	adaptfile=${percept_file_prefix}${i}.yaml
	echo "------------------"
	echo "STAGE $i REFINEMENT: $meshprev --> $meshnext"	
	echo "------------------"
	if [ $i -eq 1 ] && [ $i -eq $Nrefinement ] ; then
	    # First refinement level
	    echo "mpirun -n $NCORES mesh_adapt --refine=DEFAULT --input_mesh=$meshprev --output_mesh=$meshnext --RAR_info=$adaptfile --ioss_read_options=\"auto-decomp:yes\" --ioss_write_options=\"large,auto-join:yes\" "
	    mpirun -n $NCORES mesh_adapt --refine=DEFAULT --input_mesh=$meshprev --output_mesh=$meshnext --RAR_info=$adaptfile --ioss_read_options="auto-decomp:yes" --ioss_write_options="large,auto-join:yes"
	elif [ $i -eq 1 ]; then
	    # First refinement level
	    echo "mpirun -n $NCORES mesh_adapt --refine=DEFAULT --input_mesh=$meshprev --output_mesh=$meshnext --RAR_info=$adaptfile --ioss_read_options=\"auto-decomp:yes\" "
	    mpirun -n $NCORES mesh_adapt --refine=DEFAULT --input_mesh=$meshprev --output_mesh=$meshnext --RAR_info=$adaptfile --ioss_read_options="auto-decomp:yes"
	elif [ $i -eq $Nrefinement ]; then
	    # Last refinement level
	    echo "mpirun -n $NCORES mesh_adapt --refine=DEFAULT --input_mesh=$meshprev --output_mesh=$meshnext --RAR_info=$adaptfile  --ioss_write_options=\"large,auto-join:yes\""
	    mpirun -n $NCORES mesh_adapt --refine=DEFAULT --input_mesh=$meshprev --output_mesh=$meshnext --RAR_info=$adaptfile  --ioss_write_options="large,auto-join:yes"
	else
	    # Normal refinement level
	    echo "mpirun -n $NCORES mesh_adapt --refine=DEFAULT --input_mesh=$meshprev --output_mesh=$meshnext --RAR_info=$adaptfile "
	    mpirun -n $NCORES mesh_adapt --refine=DEFAULT --input_mesh=$meshprev --output_mesh=$meshnext --RAR_info=$adaptfile 
	fi
	echo
    done
    
    # copy the mesh to the final output mesh
    cp -av $meshnext $outputmesh

    # Clean up
    rm -rf ${tempmesh}*.e*
    
    # 
    #echo "Don't forget:"
    #echo "Use \"ncdump -v eb_names $outputmesh\" to determine the mesh blocks"
    echo
    echo "New mesh blocks: "
    ncdump -v eb_names $outputmesh | sed -ne '/eb_names =/,$ p'
fi
