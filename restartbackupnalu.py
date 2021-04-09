#!/usr/bin/env python
import sys
import os
import time
import shutil
import argparse

try:
    import ruamel.yaml as yaml
    print("# Loaded ruamel.yaml")
    useruemel=True
except:
    import yaml as yaml
    print("# Loaded yaml")
    useruemel=False

def getsuffix(file, default):
    if len(default)>0:
        return default
    else:
        lastmtime=os.path.getmtime(file)
        return time.strftime('%Y%m%d-%H-%M-%S', time.localtime(lastmtime))

# Set some options
doFASTALM=True
doBackup=False
doablstatbackup=True
runNsteps=1000

# Check the command line arguments
parser = argparse.ArgumentParser(description='Create a restart YAML file for Nalu.')
parser.add_argument('yamlfile', nargs='+')
parser.add_argument('--dobackup', action="store_true", help="Backup files [default=False]")
parser.add_argument('--addTime',   default=0.0, help="Add ADDTIME seconds to the run [default 0.0]")
parser.add_argument('--addNsteps', default=100, help="Add another ADDNSTEPS to the run [default 100]")
parser.add_argument('--runToNsteps', default=-1, help="Run until RUNTONSTEPS are reached [default is ADDNSTEPS, not RUNTONSTEPS]")
parser.add_argument('--suffix', default='',  help="Suffix to attach to backup files [default is date/time based suffix]")
parser.add_argument('--changerestartname',   default='',  help="Change the name of the restart_data_base_name [default is no change]")
parser.add_argument('--changeoutputname',    default='',  help="Change the name of the output_data_base_name [default is no change]")
parser.add_argument('--output', default='',  help="Write the new yaml file to OUTPUT")
args=parser.parse_args()


# Load the yaml filename
infile    = args.yamlfile[0]
doBackup  = args.dobackup
addTime   = float(args.addTime)
addNsteps = int(args.addNsteps)
runToNsteps = int(args.runToNsteps)
outputfile= args.output
#print(doBackup)
#print(runNsteps)
#sys.exit(1)

# See https://stackoverflow.com/questions/29518833/editing-yaml-file-by-python
if useruemel: yaml = yaml.YAML()

# Load the yaml file
with open(infile) as fp:
    data=yaml.load(fp)


# Get some basic restart stuff
restartname = data['realms'][0]['restart']['restart_data_base_name']
naludt      = data['Time_Integrators'][0]['StandardTimeIntegrator']['time_step']
maxstep     = None
maxtime     = None
if 'termination_step_count' in data['Time_Integrators'][0]['StandardTimeIntegrator']:
    maxstep     = data['Time_Integrators'][0]['StandardTimeIntegrator']['termination_step_count']
if 'termination_time' in data['Time_Integrators'][0]['StandardTimeIntegrator']:
    maxtime     = data['Time_Integrators'][0]['StandardTimeIntegrator']['termination_time']
if (maxstep is None) and (maxtime is None):
    print("Both termination_step_count and termination_time are missing from input file! EXITING... ")
    sys.exit(1)
if (maxstep is not None) and (maxtime is not None):
    print("Both termination_step_count and termination_time are specified in input file! EXITING... ")
    sys.exit(1)

# Get the last restart time
lastrestartfile=os.popen('ls -1rt %s.* |tail -n1'%restartname).read().strip()
#cmd="ncdump -v time_whole %s  | sed -ne '/time_whole =/,$ p' | sed -e 's/}//g'  -e 's/\;//g' |tr -d '\\n' | awk '{print $NF}'"
cmd="ncdump -v time_whole %s  | sed -ne '/time_whole =/,$ p' | sed -e 's/}//g'  -e 's/\;//g' -e 's/time_whole =//g' -e 's/,//g' -e 's/ /\\n/g' |sort -n |tail -n1"
restarttime=float(os.popen(cmd%lastrestartfile).read().strip())
print("# Last written restart file: %s"%lastrestartfile)
print("# Last restart time:         %f"%restarttime)

if 'actuator' in data['realms'][0]:
    doFASTALM = True
else:
    doFASTALM = False

# -- check a few things in the input file --
# Get the listed start_time 
start_time = data['Time_Integrators'][0]['StandardTimeIntegrator']['start_time']
restoration_time = start_time
# Get any initialization realms and check the start time
for irealm, realm in enumerate(data['realms']):
    if 'type' in realm:
        if realm['type']=='initialization':
            restoration_time=realm['solution_options']['input_variables_from_file_restoration_time']
# check restoration time
if abs(restoration_time - start_time)>1.0E-4:
    print("#!! WARNING: DIFFERENCE IN start_time VS input_variables_from_file_restoration_time")
    print("#!! WARNING: %f VS %f"%(start_time, restoration_time))
    print("#!! WARNING: Using %f as the start_time in input file"%restoration_time)
    start_time = restoration_time

if doFASTALM:
    # Turbine stuff
    Nturbines   = data['realms'][0]['actuator']['n_turbines_glob']
    dt_fast     = data['realms'][0]['actuator']['dt_fast']
    print("# Number of turbines:        %i"%Nturbines)
    print("# Restart filename:          %s"%restartname)
    print("# dt_fast:                   %s"%dt_fast)

    # Get the delta between FAST start and Nalu Start
    tstart_fast  = data['realms'][0]['actuator']['t_start']
    delta_tstart_fast = start_time - tstart_fast
    print("# delta_tstart_fast = %f"%delta_tstart_fast)

    # Get all of the fast files
    fastfiles=[]
    for i in range(0,Nturbines):
        fastfiles.append(data['realms'][0]['actuator']['Turbine%i'%i]['fast_input_filename'])
    #print fastfiles

    # Check the FAST file DT's match up
    for fst in fastfiles:
        cmd="grep DT %s | head -n1 | awk '{print $1}'"
        fstfile_dt=float(os.popen(cmd%fst).read().strip())
        if (abs(fstfile_dt-dt_fast)>1.0E-6):
            print(" dt difference: %f <-- MISMATCH"%(fstfile_dt-dt_fast))
            sys.exit(1)
        else:
            print("# dt difference: %f OKAY"%(fstfile_dt-dt_fast))

    # Back up the actuator files
    if doBackup:
        for i in range(0,Nturbines):
            fastfile = data['realms'][0]['actuator']['Turbine%i'%i]['fast_input_filename']
            fastfilebase=os.path.splitext(fastfile)[0]
            sumfile=fastfilebase+".T%i.sum"%(i+1)
            outfile=fastfilebase+".T%i.out"%(i+1)
            print("#Working on fast file %s"%fastfilebase)
            #lastmtime=os.path.getmtime(sumfile)
            #suffix=time.strftime('%Y%m%d-%H-%M-%S', time.localtime(lastmtime))
            suffix=getsuffix(sumfile, args.suffix)
            # Copy the out file
            newoutfile=fastfilebase+".T%i.out.%s"%(i+1,suffix)
            print("# copying: %s --> %s"%(outfile, newoutfile))
            shutil.copy2(outfile, newoutfile)
            # Copy the sum file
            newsumfile=fastfilebase+".T%i.sum.%s"%(i+1,suffix)
            print("# copying: %s --> %s"%(sumfile, newsumfile))
            shutil.copy2(sumfile, newsumfile)

# backup the restart file
if doBackup:
    print("# Backing up the log file")
    # Backup the old logs
    logfile=os.path.splitext(infile)[0]+".log"
    #lastmtime=os.path.getmtime(logfile)
    #suffix=time.strftime('%Y%m%d-%H-%M-%S', time.localtime(lastmtime))
    suffix=getsuffix(logfile, args.suffix)
    print("# Log file: %s -> %s"%(logfile,logfile+"."+suffix))
    shutil.copy2(logfile, logfile+"."+suffix)

    # Get the number of cores in the previous run
    cmd="grep 'number of processors' %s | awk '{print $NF}'"
    Nprocs=int(os.popen(cmd%logfile).read().strip())
    print("# Number of cores in previous run: %i"%Nprocs)
    
    # Back up the restart files
    # Get the last modified time
    #lastmtime=os.path.getmtime(restartname+".%i.%s"%(Nprocs,str(0).zfill(len(repr(Nprocs)))))
    #suffix=time.strftime('%Y%m%d-%H-%M-%S', time.localtime(lastmtime))
    suffix=getsuffix(restartname+".%i.%s"%(Nprocs,str(0).zfill(len(repr(Nprocs)))), args.suffix)
    for i in range(0,Nprocs):
        restartfilename=restartname+".%i.%s"%(Nprocs,str(i).zfill(len(repr(Nprocs))))
        print("# Backing up %s -> %s"%(restartfilename,restartfilename+"."+suffix))
        shutil.copy2(restartfilename,restartfilename+"."+suffix)

    # Back up the output restart files
    outputname = data['realms'][0]['output']['output_data_base_name']
    for i in range(0,Nprocs):
        outputfilename=outputname+".%i.%s"%(Nprocs,str(i).zfill(len(repr(Nprocs))))
        print("# Backing up %s -> %s"%(outputfilename,outputfilename+"."+suffix))
        shutil.copy2(outputfilename,outputfilename+"."+suffix)

# Backup the ABL stats
if doBackup:
    if 'boundary_layer_statistics' in data['realms'][0]:
        statsfile=data['realms'][0]['boundary_layer_statistics']['stats_output_file']
        suffix=getsuffix(statsfile, args.suffix)
        print("# Backing up the ABL stats file %s -> %s"%
              (statsfile,statsfile+"."+suffix))
        shutil.copy2(statsfile, statsfile+"."+suffix)

        

# -- Start changing stuff in the yaml file --
print("")
# Change the start mesh
print("# CHANGING realms:mesh = %s"%restartname)
data['realms'][0]['mesh'] = restartname

# Change the automatic_decomposition_type
print("# CHANGING realms:automatic_decomposition_type = None")
data['realms'][0]['automatic_decomposition_type'] = "None"

# Change the start_time
print("# CHANGING Time_Integrators:StandardTimeIntegrator:start_time = %f"%restarttime)
data['Time_Integrators'][0]['StandardTimeIntegrator']['start_time'] = restarttime

# Change the termination_step_count
if maxstep is not None:
    if (runToNsteps>0): finalstep = runToNsteps
    else:               finalstep = maxstep + addNsteps
    data['Time_Integrators'][0]['StandardTimeIntegrator']['termination_step_count'] = finalstep
else:
    finaltime = maxtime + addTime
    data['Time_Integrators'][0]['StandardTimeIntegrator']['termination_time'] = finaltime

# Change the restart_time
data['realms'][0]['restart']['restart_time'] = restarttime
# Change the restart name
if len(args.changerestartname)>0:
    print("# CHANGING restartname: %s to %s"%(
        data['realms'][0]['restart']['restart_data_base_name'],
        args.changerestartname))
    data['realms'][0]['restart']['restart_data_base_name'] = args.changerestartname

# Change the output name
if len(args.changeoutputname)>0:
    print("# CHANGING outputname: %s to %s"%(
        data['realms'][0]['output']['output_data_base_name'],
        args.changeoutputname))
    data['realms'][0]['output']['output_data_base_name'] = args.changeoutputname


# Get a list of initialization realms
initializationrealms=[]
deleterealms=[]
for irealm, realm in enumerate(data['realms']):
    if 'type' in realm:
        if realm['type']=='initialization':
            print("# REMOVING %s from realms"%realm['name'])
            initializationrealms.append(realm['name'])
            deleterealms.append(irealm)
#print(initializationrealms, deleterealms)
for realm in deleterealms:
    data['realms'].pop(realm)

# Check transfers for badrealms and delete them
deletetransfers=[]
if 'transfers' in data:
    for ixfer, xfer in enumerate(data['transfers']):
        check = any(realm in xfer['realm_pair'] for realm in initializationrealms)
        if check: 
            #print(repr(xfer['name'])+' has realm in '+repr(initializationrealms))
            print("# REMOVING %s from transfers section"%xfer['name'])
            deletetransfers.append(ixfer)
for xfer in deletetransfers:
    data['transfers'].pop(xfer)
            
# Check the time integration realms
timeint_realms = data['Time_Integrators'][0]['StandardTimeIntegrator']['realms']
for realm in initializationrealms: 
    print("# REMOVING %s from StandardTimeIntegrator realms"%realm)
    timeint_realms.remove(realm)
data['Time_Integrators'][0]['StandardTimeIntegrator']['realms'] = timeint_realms

# Change turbine simStart
if doFASTALM:
    extratime = None
    if maxstep is not None: extratime = naludt*maxstep + 100000
    if maxtime is not None: extratime = finaltime      + 100000.0
    data['realms'][0]['actuator']['simStart'] = "restartDriverInitFAST"
    data['realms'][0]['actuator']['t_start']  = restarttime - delta_tstart_fast
    data['realms'][0]['actuator']['t_max']    = restarttime + extratime
    for i in range(0,Nturbines):
        # Get the latest checkpoint file
        fastfile = data['realms'][0]['actuator']['Turbine%i'%i]['fast_input_filename']
        fastfilebase=os.path.splitext(fastfile)[0]
        cmd = "ls -1 -rt %s.*[0-9].chkp  |tail -n1"%(fastfilebase+".T%i"%(i+1))
        fastchkp=os.popen(cmd).read().strip()
        fastrestart=os.path.splitext(fastchkp)[0]        
        data['realms'][0]['actuator']['Turbine%i'%i]['restart_filename'] = fastrestart


print("")
print("# ------------------------------ #")
# Write it out
if len(outputfile)>0:
    fout = open(outputfile,'w')
    print("# Writing new restart file to "+outputfile)
else:
    fout = sys.stdout

if useruemel: 
    yaml.dump(data, fout)
else: 
    yaml.dump(data, fout, default_flow_style=False)

if len(outputfile)>0: 
    fout.close()
