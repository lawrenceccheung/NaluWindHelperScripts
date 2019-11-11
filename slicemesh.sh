#!/bin/sh

meshyamlfile=mesh1.yaml
simyamlfile=
GENERATEYAML=false
extravars=""
NALUUTILDIR=~/nscratch/buildNalu/Nalu_intel/install/intel/nalu-wind/bin/

# Help for this script
function help() {
cat <<EOF
Creates a mesh slice 

Usage: 
  $1 MESHYAMLFILE [OPTIONS]
where
  MESHYAMLFILE is the yaml file containing the slice mesh parameters.

Optional Arguments:
  -y|--yaml-output YAMLFILE    Print out the corresponding yaml inputs needed to include the slice mesh 
                               output during the simulation.  YAMLFILE is the main simulation yamlfile
  -v|--extra-vars  VARLIST     An extra list of variables to include when writing out the sliced meshes.
                               VARLIST is of the form "var1:N var2:N ..." where var1, var2, are the
                               variable names, and N is the number of components for that variable
                               Default: velocity (3 components) is always included, no need repeat it
EOF
}

# Parse the arguments and options
# --------------------------
# For arg parsing details/example, see https://medium.com/@Drew_Stokes/bash-argument-parsing-54f3b81a6a8f
PARAMS=""
while (( "$#" )); do
    case "$1" in
	-v|--extra-vars)
	    extravars=$2
	    shift 2
	    ;;
	-y|--yaml-output)
	    GENERATEYAML=true
	    simyamlfile=$2
	    shift 2
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

# Set some of the arguments
yamlfile=$1

# Print out some of the variables
echo "yamlfile    = $yamlfile"
echo "simyamlfile = $simyamlfile"
echo "extravars   = $extravars"

# Load all of the stuff required to get Nalu up and running
echo "Loading modules"
module purge
module load intel/18.0.2.199 gnu/7.3.1 mkl/18.0.2.199  openmpi-intel/2.1
source /nscratch/lcheung/buildNalu/Nalu_intel/spack/share/spack/setup-env.sh
spack load boost; 
spack load netcdf; 
spack load hdf5
module load canopy

READYAMLHEADER=''
function getyamlheader {
# Get the header needed to read the yaml file
# This is stored in the variable READYAMLHEADER
read -r -d '' READYAMLHEADER << EOM
import yaml
with open('$1') as stream:
    try:
        yamldata=yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)
EOM
}


# Run the slice mesh utility
# ----------------------------
# Get the mesh output name
# ------
getyamlheader $meshyamlfile
slicemeshname=`python - <<DOC
$READYAMLHEADER
print yamldata['slice_mesh']['output_db']
DOC`
echo "Output mesh name = $slicemeshname"


$NALUUTILDIR/slice_mesh -i $yamlfile

surfacenames=`ncdump -v eb_names $slicemeshname | sed -ne '/eb_names =/,$ p' | sed -e '1d' -e 's/}//g' -e 's/,//g' -e 's/\;//g' -e 's/\"//g'`
echo $surfacenames

# construct targetname
targetname="["
for surf in $surfacenames; do
    targetname="$targetname $surf,"
done
targetname=${targetname::-1}   # Delete the last comma
targetname="$targetname ]"
echo $targetname


# Generate extra fields to register
function generatefieldreg() {
    for var in $extravars; do
	varname=`echo "$var"| awk 'BEGIN{ FS=":" } {print $1}' `
	varn=`echo "$var"| awk 'BEGIN{ FS=":" } {print $2}'`
	varslicename="${varname}_slice"
	cat <<EOF
    - field_name: $varslicename
      target_name: *fieldreg 
      field_size: $varn
      field_type: node_rank
EOF
    done
}

function generatetransferpairs() {
    for var in $extravars; do
	varname=`echo "$var"| awk 'BEGIN{ FS=":" } {print $1}' `
	varslicename="${varname}_slice"
	cat <<EOF
  - [$varname, $varslicename]
EOF
    done
}

if $GENERATEYAML; then
# Get the simulation yaml names
# -------------------------------------
getyamlheader $simyamlfile
simrealmname=`python - <<DOC
$READYAMLHEADER
print yamldata['realms'][0]['name']
DOC`
echo "Output parts name = $simrealmname"

simpartsname=`python - <<DOC
$READYAMLHEADER
print yamldata['realms'][0]['material_properties']['target_name']
DOC`
echo "Output parts name = $simpartsname"


echo "# === Auto-generated YAML below ======"
echo
echo "# Goes under [realms:]"
cat <<EOF
- name: ioRealm
  mesh: $slicemeshname
  type: input_output
  automatic_decomposition_type: rcb

  field_registration:
    specifications:
    - field_name: velocity_slice
      target_name: &fieldreg $targetname
      field_size: 3
      field_type: node_rank
EOF
# Add any extra field registration
for var in $extravars; do
    varname=`echo "$var"| awk 'BEGIN{ FS=":" } {print $1}' `
    varn=`echo "$var"| awk 'BEGIN{ FS=":" } {print $2}'`
    varslicename="${varname}_slice"
    cat <<EOF
    - field_name: $varslicename
      target_name: *fieldreg 
      field_size: $varn
      field_type: node_rank
EOF
done

cat <<EOF
  output:
    output_data_base_name: ./sliceDataInstantaneous/$slicemeshname
    output_frequency: 1
    output_node_set: no
    output_variables:
    - velocity_slice
EOF
# Add any extra field registration
for var in $extravars; do
    varname=`echo "$var"| awk 'BEGIN{ FS=":" } {print $1}' `
    varslicename="${varname}_slice"
    cat<<EOF
    - $varslicename
EOF
done

# Write out the transfers
cat <<EOF
transfers:
EOF
for surf in $surfacenames; do
cat <<EOF
- name: $surf
  type: geometric
  realm_pair: [$simrealmname, ioRealm]
  to_target_name: $surf
  from_target_name: $simpartsname
  objective: input_output
  transfer_variables:
  - [velocity, velocity_slice]
EOF
generatetransferpairs
done
echo
echo "# === End auto-generated YAML ======"

fi
