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
parser.add_argument('--addNsteps', default=100, help="Add another ADDNSTEPS to the run [default 100]")
parser.add_argument('--runToNsteps', default=-1, help="Run until RUNTONSTEPS are reached [default is ADDNSTEPS, not RUNTONSTEPS]")
parser.add_argument('--suffix', default='',  help="Suffix to attach to backup files [default is date/time based suffix]")
args=parser.parse_args()


# Load the yaml filename
infile    = args.yamlfile[0]
doBackup  = args.dobackup
addNsteps = int(args.addNsteps)
runToNsteps = int(args.runToNsteps)
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
maxstep     = data['Time_Integrators'][0]['StandardTimeIntegrator']['termination_step_count']

# Get the last restart time
lastrestartfile=os.popen('ls -1rt %s.* |tail -n1'%restartname).read().strip()
cmd="ncdump -v time_whole %s  | sed -ne '/time_whole =/,$ p' | sed -e 's/}//g'  -e 's/\\;//g' |tr -d '\\n' | awk '{print $NF}'"
restarttime=float(os.popen(cmd%lastrestartfile).read().strip())
print("# Last written restart file: %s"%lastrestartfile)
print("# Last restart time:         %f"%restarttime)

if 'actuator' in data['realms'][0]:
    doFASTALM = True
else:
    doFASTALM = False


if doFASTALM:
    # Turbine stuff
    Nturbines   = data['realms'][0]['actuator']['n_turbines_glob']
    dt_fast     = data['realms'][0]['actuator']['dt_fast']
    print("# Number of turbines:        %i"%Nturbines)
    print("# Restart filename:          %s"%restartname)
    print("# dt_fast:                   %s"%dt_fast)

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
if (runToNsteps>0): finalstep = runToNsteps
else:               finalstep = maxstep + addNsteps
data['Time_Integrators'][0]['StandardTimeIntegrator']['termination_step_count'] = finalstep

# Change the restart_time
data['realms'][0]['restart']['restart_time'] = restarttime

# Change turbine simStart
if doFASTALM:
    data['realms'][0]['actuator']['simStart'] = "restartDriverInitFAST"
    data['realms'][0]['actuator']['t_start']  = restarttime 
    data['realms'][0]['actuator']['t_max']    = restarttime +naludt*maxstep+1000
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
if useruemel: 
    yaml.dump(data, sys.stdout)
else: 
    yaml.dump(data, sys.stdout, default_flow_style=False)
