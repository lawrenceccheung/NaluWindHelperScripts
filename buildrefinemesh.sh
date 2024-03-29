#!/bin/bash

yamlfile=abl_preprocess.yaml
outputmesh=refinedmesh.exo
NCORES=8
NPERNODE=36
CREATEMESH=true
RUNNALUPREPROC=true
RUNREFINE=true
CLUSTERARGS=""
#NALUUTILDIR=~/nscratch/buildNalu/Nalu_intel/install/intel/nalu-wind/bin/
#NALUUTILDIR=/ascldap/users/lcheung/wind_uq/NaluBuilds/ghost.20201216/install/intel/wind-utils/bin/
#NALUUTILDIR=/projects/wind_uq/lcheung/NaluBuilds/cee-compute.20210305/install/gcc/wind-util/bin/

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
  --on-cluster              : Job is being run on cluster like skybridge, chama, etc.
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
	--on-cluster)
	    CLUSTERARGS="--bind-to core --npernode $NPERNODE"
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

# Check the number of arguments
if [ $# -lt 1 ]; then
    help $0
    exit 1
fi
yamlfile=$1

echo "yamlfile   = $yamlfile"
echo "outputmesh = $outputmesh"
echo "NCORES     = $NCORES"
echo "CREATEMESH = $CREATEMESH"
echo "RUNNALUPREPROC=$RUNNALUPREPROC"
echo "RUNREFINE  = $RUNREFINE"
echo "CLUSTERARGS= $CLUSTERARGS"
#exit 


# Load all of the stuff required to get Nalu up and running
echo "Loading modules"

#MODULEFILE=/projects/wind_uq/lcheung/NaluBuilds/ghost.20201216/source/nalu-wind/build-intel/loadnalumods.sh
#MODULEFILE=$NALUUTILDIR/loadnalumods.sh
MODULEFILE=/hpc_projects/wind_uq/lcheung/SpackManagerBuilds/spack-manager.20230309/loadexawind.sh
if test -f "$MODULEFILE"; then
    source $MODULEFILE
    NALUX=`which naluX`
    NALUUTILDIR=`dirname $NALUX`
else
    echo "Cannot load modules"
    exit 1
fi

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
print(yamldata['nalu_preprocess']['output_db'])
DOC`
echo "Output mesh name = $meshbasename"

# Get the number of refinement levels
# -------
Nrefinement=`python - <<DOC
$READYAMLHEADER
print(len(yamldata['nalu_preprocess']['mesh_local_refinement']['refinement_levels']))
DOC`
echo "Nrefinement = $Nrefinement"

# Get the adapt file names
percept_file_prefix=`python - <<DOC
$READYAMLHEADER
print(yamldata['nalu_preprocess']['mesh_local_refinement']['percept_file_prefix'])
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
    #mpirun $CLUSTERARGS -n $NCORES $NALUUTILDIR/nalu_preprocess -i $yamlfile    
    $NALUUTILDIR/nalu_preprocess -i $yamlfile    
fi

# ------------------------
# Run the mesh refinement
# ------------------------
if $RUNREFINE; then
    echo "Running mesh refinement step"
    module purge
    module load sierra
    module load seacas
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
	    echo "mpirun $CLUSTERARGS -n $NCORES mesh_adapt --refine=DEFAULT --input_mesh=$meshprev --output_mesh=$meshnext --RAR_info=$adaptfile --ioss_read_options=\"auto-decomp:yes\" --ioss_write_options=\"large,auto-join:yes\" "
	    mpirun $CLUSTERARGS -n $NCORES mesh_adapt --refine=DEFAULT --input_mesh=$meshprev --output_mesh=$meshnext --RAR_info=$adaptfile --ioss_read_options="auto-decomp:yes" --ioss_write_options="large,auto-join:yes"
	elif [ $i -eq 1 ]; then
	    # First refinement level
	    echo "mpirun $CLUSTERARGS -n $NCORES mesh_adapt --refine=DEFAULT --input_mesh=$meshprev --output_mesh=$meshnext --RAR_info=$adaptfile --ioss_read_options=\"auto-decomp:yes\" "
	    mpirun $CLUSTERARGS -n $NCORES mesh_adapt --refine=DEFAULT --input_mesh=$meshprev --output_mesh=$meshnext --RAR_info=$adaptfile --ioss_read_options="auto-decomp:yes"
	elif [ $i -eq $Nrefinement ]; then
	    # Last refinement level
	    echo "mpirun $CLUSTERARGS -n $NCORES mesh_adapt --refine=DEFAULT --input_mesh=$meshprev --output_mesh=$meshnext --RAR_info=$adaptfile  --ioss_write_options=\"large,auto-join:yes\""
	    mpirun $CLUSTERARGS -n $NCORES mesh_adapt --refine=DEFAULT --input_mesh=$meshprev --output_mesh=$meshnext --RAR_info=$adaptfile  --ioss_write_options="large,auto-join:yes"
	else
	    # Normal refinement level
	    echo "mpirun $CLUSTERARGS -n $NCORES mesh_adapt --refine=DEFAULT --input_mesh=$meshprev --output_mesh=$meshnext --RAR_info=$adaptfile "
	    mpirun $CLUSTERARGS -n $NCORES mesh_adapt --refine=DEFAULT --input_mesh=$meshprev --output_mesh=$meshnext --RAR_info=$adaptfile 
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
    ncdump -v eb_names $outputmesh | sed -ne '/eb_names =/,$ p' |sed 's/pyramid_5._urpconv.Tetrahedron_4._urpconv/pyramid_5._urpconv.Tetrahedron_4._urpconv (IGNORE THIS ONE)/g'

fi
