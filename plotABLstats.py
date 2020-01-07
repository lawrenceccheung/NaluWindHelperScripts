#!/usr/bin/env python

# Following some previous people's work in 
# https://www.javatpoint.com/python-tkinter-frame
# https://www.python-course.eu/tkinter_checkboxes.php
# https://stackoverflow.com/questions/30774281/update-matplotlib-plot-in-tkinter-gui

import netCDF4 as ncdf
import numpy as np
from scipy import interpolate
import math

from numpy import *
import matplotlib
matplotlib.use('TkAgg')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
# implement the default mpl key bindings
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from itertools import cycle
import argparse

import sys, os
if sys.version_info[0] < 3:
    import Tkinter as Tk
else:
    import tkinter as Tk

nogui=True

class ScrollableFrame(Tk.Frame):
    def __init__(self, master, height=250, **kwargs):
        Tk.Frame.__init__(self, master, **kwargs)

        # create a canvas object and a vertical scrollbar for scrolling it
        self.vscrollbar = Tk.Scrollbar(self, orient=Tk.VERTICAL)
        self.vscrollbar.pack(side='right', fill="y",  expand="false")
        self.canvas = Tk.Canvas(self,
                                bg='#444444', bd=1,
                                width=150, height=height,
                                highlightthickness=0,
                                yscrollcommand=self.vscrollbar.set)
        self.canvas.pack(side="left") #, fill="both", expand="true")
        self.vscrollbar.config(command=self.canvas.yview)

        # reset the view
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = Tk.Frame(self.canvas, **kwargs)
        self.canvas.create_window(0, 0, window=self.interior, anchor="nw")

        self.bind('<Configure>', self.set_scrollregion)


    def set_scrollregion(self, event=None):
        """ Set the scroll region on the canvas"""
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))

class RadioBbar(Tk.Frame):
   def __init__(self, parent=None, picks=[], title="", offset=0,
                side=Tk.LEFT, anchor=Tk.W):
      Tk.Frame.__init__(self, parent)
      Tk.Label(self, text=title, pady=10).pack()
      self.v = Tk.IntVar()
      for i, pick in enumerate(picks):
          rb=Tk.Radiobutton(self, text=pick, variable=self.v, indicatoron=1, 
                            value=i+offset)
          rb.pack(side=Tk.TOP, anchor=anchor)
   def state(self):
      return self.v.get()

class ABLStatsFileClass():
    '''
    Interface to ABL Statistics NetCDF file
    '''

    def __init__(self, stats_file='abl_statistics.nc'):
        '''
        Args:
            stats_file (path): Absolute path to the NetCDF file
        '''
        # Read in the file using netcdf
        self.abl_stats = ncdf.Dataset(stats_file)

        print('The netcdf file contains the variables:')
        for key in self.abl_stats.variables.keys(): 
            print(key, np.shape(self.abl_stats[key]))

        # Extract the heights
        self.heights = self.abl_stats['heights']
    
        # Extract the time
        self.time = self.abl_stats.variables['time']

        # Extract the utau
        self.utau = self.abl_stats.variables['utau']
    
        # Velocity
        # Index - [time, height, (x, y, z)]
        velocity = self.abl_stats.variables['velocity']

        # Velocity components as a function of time for given height
        self.u_h = interpolate.interp1d(self.heights, velocity[:, :, 0], axis=1)
        self.v_h = interpolate.interp1d(self.heights, velocity[:, :, 1], axis=1)
        self.w_h = interpolate.interp1d(self.heights, velocity[:, :, 2], axis=1)

    def time_average(self, field='velocity', index=0, times=[0., 100], scalar=False):
        '''
        Provide field time average
        field - the field to time-average
        index - the component index (for example: velocity has 3 components)
        times - the times to average
        '''
        
        # Filter the field based on the times
        filt = ((self.time[:] >= times[0]) & (self.time[:] <= times[1]))
        # Filtered time
        t = self.time[filt]
        # The total time
        dt = np.amax(t) - np.amin(t)

        # Filtered field
        if scalar:    f = self.abl_stats[field][filt,:]
        else:         f = self.abl_stats[field][filt,:,index]

        # Compute the time average as an integral
        integral = np.trapz(f, x=t, axis=0) / dt

        return integral


# Define some key actions
def on_key_event(event):
    global plotvar, planen, plotfile
    key_press_handler(event, canvas, toolbar)
    if (event.key == 'right'):
        if (plotfile.state()<(len(filelist)-1)): plotfile.v.set(plotfile.state()+1)
        else: plotfile.v.set(0)
        #print("Plotting: "+filelist[plotfile.state()])
        _plotdata()
    if (event.key=='left'):
        if (plotfile.state()>0): plotfile.v.set(plotfile.state()-1)
        else:              plotfile.v.set(len(filelist)-1)
        #print("Plotting: "+filelist[plotfile.state()])
        _plotdata()
    if (event.key.upper()=='P'):
        print("Plotting data")
        _plotdata()

def _quit():
    global center
    center.quit()     # stops mainloop
    center.destroy()  # this is necessary on Windows to prevent
                      # Fatal Python Error: PyEval_RestoreThread: NULL tstate


# Define all plot functions here

def plotvelocityhistory(data, figax, tlims=[], **kwargs):
    global nogui
    time = data.time
    # The heights to plot [m]
    if 'heights' in kwargs: 
        heights=kwargs['heights']
    else:
        heights = [float(x) for x in hhentry.get().split(',')]
    # Loop through all the heights
    for z in heights:
        # Velocity as function of time
        u = data.u_h(z)
        v = data.v_h(z)
        # Velocity magnitude
        u_mag = np.sqrt(u**2 + v**2)
        figax.plot(time, u_mag, label=r'$U_{\rm mag},$ $z=$'+str(z)+' [m]')
    figax.legend(loc='best')
    figax.set_xlabel('Time [s]')
    figax.set_ylabel('Velocity [m/s]')
    return

def plotutauhistory(data, figax, tlims=[], **kwargs):
    time = data.time
    utau = data.utau
    figax.plot(time, utau, label=r'$U_{\tau}$')
    figax.set_xlabel('Time [s]')
    figax.set_ylabel('Utau Velocity [m/s]')
    return

def plotvelocityprofile(data, figax, tlims=[], **kwargs):
    if len(tlims)>0:
        t1 = tlims[0]
        t2 = tlims[1]
    else:
        t1 = float(t1entry.get())
        t2 = float(t2entry.get())
    z = data.heights
    u = data.time_average(field='velocity', index=0, times=[t1, t2])
    v = data.time_average(field='velocity', index=1, times=[t1, t2])
    u_mag = np.sqrt(u**2 + v**2)
    figax.plot(u, z, '-o', label='U')
    figax.plot(v, z, '-o', label='V')
    figax.plot(u_mag, z, '-o', label='U mag')
    figax.legend(loc='best')
    figax.set_xlabel('Velocity [m/s]')
    figax.set_ylabel('z [m]')
    if 'focusz'    in kwargs: figax.set_ylim(kwargs['focusz'])
    if 'hubheight' in kwargs: figax.hlines(kwargs['hubheight'], min(u_mag), max(u_mag), linestyles='dashed', linewidth=0.5)
    return

def plotveerprofile(data, figax, tlims=[], **kwargs):
    if len(tlims)>0:
        t1 = tlims[0]
        t2 = tlims[1]
    else:
        t1 = float(t1entry.get())
        t2 = float(t2entry.get())
    z = data.heights
    u = data.time_average(field='velocity', index=0, times=[t1, t2])
    v = data.time_average(field='velocity', index=1, times=[t1, t2])
    veer = 270-np.arctan2(v, u)*180.0/math.pi
    figax.plot(veer, z, '-o', label='Wind Dir')
    figax.legend(loc='best')
    figax.set_xlabel('Wind Direction [deg]')
    figax.set_ylabel('z [m]')
    if 'focusz' in kwargs: figax.set_ylim(kwargs['focusz'])
    if 'hubheight' in kwargs: figax.hlines(kwargs['hubheight'], min(veer), max(veer), linestyles='dashed', linewidth=0.5)
    return

def plottkeprofile(data, figax, tlims=[], **kwargs):
    if len(tlims)>0:
        t1 = tlims[0]
        t2 = tlims[1]
    else:
        t1 = float(t1entry.get())
        t2 = float(t2entry.get())
    z  = data.heights
    uu = data.time_average(field='resolved_stress', index=0, times=[t1, t2])
    vv = data.time_average(field='resolved_stress', index=3, times=[t1, t2])
    ww = data.time_average(field='resolved_stress', index=5, times=[t1, t2])
    tke = 0.5*(uu+vv+ww)
    figax.plot(uu, z, '-o', label='uu')
    figax.plot(vv, z, '-o', label='vv')
    figax.plot(ww, z, '-o', label='ww')
    figax.plot(tke, z, '-o', label='TKE')
    figax.legend(loc='best')
    figax.set_xlabel("Resolved Stress [m^2/s^2]")
    figax.set_ylabel('z [m]')
    if 'focusz' in kwargs: figax.set_ylim(kwargs['focusz'])
    if 'hubheight' in kwargs: figax.hlines(kwargs['hubheight'], min(tke), max(tke), linestyles='dashed', linewidth=0.5)
    return


def plottemperatureprofile(data, figax, tlims=[], **kwargs):
    if len(tlims)>0:
        t1 = tlims[0]
        t2 = tlims[1]
    else:
        t1 = float(t1entry.get())
        t2 = float(t2entry.get())
    z = data.heights
    T = data.time_average(field='temperature', index=0, times=[t1, t2], scalar=True)
    figax.plot(T, z, '-o', label='Temp')
    figax.legend(loc='best')
    figax.set_xlabel('Temperature [K]')
    figax.set_ylabel('z [m]')
    if 'focusz' in kwargs: figax.set_ylim(kwargs['focusz'])
    if 'hubheight' in kwargs: figax.hlines(kwargs['hubheight'], min(T), max(T), linestyles='dashed', linewidth=0.5)
    return

def plotShearAlpha(data, figax, tlims=[], **kwargs):
    if len(tlims)>0:
        t1 = tlims[0]
        t2 = tlims[1]
    else:
        t1 = float(t1entry.get())
        t2 = float(t2entry.get())
    z = data.heights
    u = data.time_average(field='velocity', index=0, times=[t1, t2])
    v = data.time_average(field='velocity', index=1, times=[t1, t2])
    u_mag = np.sqrt(u**2 + v**2)
    dudz = (u_mag[1:]-u_mag[0:-1])/(z[1:]-z[0:-1])
    dudz=np.append(dudz, dudz[-1])
    alpha=z/u_mag*dudz
    figax.plot(alpha, z, '-o', label='Shear Alpha')
    figax.legend(loc='best')
    figax.set_xlabel('Shear Exponent [-]')
    figax.set_ylabel('z [m]')
    if 'focusz' in kwargs: figax.set_ylim(kwargs['focusz'])
    if 'hubheight' in kwargs: figax.hlines(kwargs['hubheight'], min(alpha), max(alpha), linestyles='dashed', linewidth=0.5)
    return

def plotTIprofile(data, figax, tlims=[], **kwargs):
    if len(tlims)>0:
        t1 = tlims[0]
        t2 = tlims[1]
    else:
        t1 = float(t1entry.get())
        t2 = float(t2entry.get())
    z  = data.heights
    u = data.time_average(field='velocity', index=0, times=[t1, t2])
    v = data.time_average(field='velocity', index=1, times=[t1, t2])
    u_mag = np.sqrt(u**2 + v**2)
    # TKE/TI
    uu = data.time_average(field='resolved_stress', index=0, times=[t1, t2])
    vv = data.time_average(field='resolved_stress', index=3, times=[t1, t2])
    ww = data.time_average(field='resolved_stress', index=5, times=[t1, t2])
    tke = 0.5*(uu+vv+ww)
    TI = sqrt(2.0/3.0*tke)/u_mag
    figax.plot(TI, z, '-o', label='TKE')
    figax.legend(loc='best')
    figax.set_xlabel("TI [-]")
    figax.set_ylabel('z [m]')
    if 'focusz' in kwargs: figax.set_ylim(kwargs['focusz'])
    if 'hubheight' in kwargs: figax.hlines(kwargs['hubheight'], min(TI), max(TI), linestyles='dashed', linewidth=0.5)
    return

def reportABLstats(data, heights=[], tlims=[]):
    outdata=[]
    if len(tlims)>0:
        t1 = tlims[0]
        t2 = tlims[1]
    else:
        t1 = float(t1entry.get())
        t2 = float(t2entry.get())
    z  = data.heights
    u = data.time_average(field='velocity', index=0, times=[t1, t2])
    v = data.time_average(field='velocity', index=1, times=[t1, t2])
    u_mag = np.sqrt(u**2 + v**2)
    # TKE/TI
    uu = data.time_average(field='resolved_stress', index=0, times=[t1, t2])
    vv = data.time_average(field='resolved_stress', index=3, times=[t1, t2])
    ww = data.time_average(field='resolved_stress', index=5, times=[t1, t2])
    tke = 0.5*(uu+vv+ww)
    TI = sqrt(2.0/3.0*tke)/u_mag
    # Shear
    dudz = (u_mag[1:]-u_mag[0:-1])/(z[1:]-z[0:-1])
    dudz=np.append(dudz, dudz[-1])
    alpha=z/u_mag*dudz
    veer = 270-np.arctan2(v, u)*180.0/math.pi

    if (len(heights)>0):
        reportheights=heights
    else:
        reportheights = [float(x) for x in hhentry.get().split(',')]

    u_magf = interpolate.interp1d(z, u_mag)
    TIf    = interpolate.interp1d(z, TI)        
    veerf  = interpolate.interp1d(z, veer)
    alphaf = interpolate.interp1d(z, alpha)
    print("")
    print("%9s %12s %12s %12s %12s"%("z", "u_mag", "TI", "alpha", "Wdir"))
    print("%9s %12s %12s %12s %12s"%("===", "===", "===", "===", "==="))
    for h in reportheights:
        print("%9.2f %e %e %e %e"%(h, u_magf(h), TIf(h), alphaf(h), veerf(h)))
        outdata.append([u_magf(h), TIf(h), alphaf(h), veerf(h)])
    return array(outdata)

# All of the possible functions to plot
allplotfunctions=[["Velocity time trace", plotvelocityhistory, "Vtrace"],
                  ["Velocity Profile",    plotvelocityprofile, "Vprof"],
                  ["Veer Profile",        plotveerprofile,     "Veerprof"],
                  ["Temperature Profile", plottemperatureprofile, "Tprof"],
                  ["TKE Profile",         plottkeprofile,      "TKEprof"],
                  ["TI Profile",          plotTIprofile,       "TIprof"],
                  ["Utau history",        plotutauhistory,     "Utauprof"],
                  ["Shear exp. Profile",  plotShearAlpha,      "Alphaprof"]]

# Plots all of the data
def _reportABL():
    global data
    reportABLstats(data)
    return
              
# Plots all of the data
def _plotdata():
    global allplotfunctions, data
    fig.clf()
    ax=fig.add_subplot(111)
    ax.clear()
    # Load the file to plot
    plotfunc=allplotfunctions[plotfile.state()]

    # Call the function to plot
    plotfunc[1](data, ax)
    ax.set_title(plotfunc[0])
    canvas.draw()
    toolbar.update()
    fig.tight_layout()
    canvas.show()

# Plots all of the data
def _saveallfigs():
    global allplotfunctions, data
    for plotfunc in allplotfunctions: 
        fig.clf()
        ax=fig.add_subplot(111)
        ax.clear()
        # Call the function to plot
        print("Saving "+plotfunc[0])
        plotfunc[1](data, ax)
        ax.set_title(plotfunc[0])
        canvas.draw()
        toolbar.update()
        fig.tight_layout()
        savename=plotfunc[2]+".png"
        fig.savefig(savename)
        canvas.show()
    return

# Plots all of the data
def _reloaddata():
    global allplotfunctions, data
    data = ABLStatsFileClass(stats_file=filelist[0])
    print("Reloaded data.  Max t = ",max(data.time))
    return

# Plots all of the data
def jupyter_plotall(data, plotfuncs=allplotfunctions, tlims=[], **kwargs):
    if 'figsize' in kwargs:  figsize=kwargs['figsize']
    else:                    figsize=(6,6)
    ylims=[]
    for key in kwargs:
        if key=='ylims': ylims=kwargs[key]
        if key=='figsize': figsize=kwargs[key]
    # Loop through and plot everything
    for plotfunc in plotfuncs:
        fig=plt.figure(figsize=figsize)
        ax=fig.add_subplot(111)
        plotfunc[1](data, ax, tlims=tlims, **kwargs)
        ax.set_title(plotfunc[0])
        

# Run all of the gui elements
def doGUI():
    global fig, canvas, toolbar, plotfile, center
    global t1entry, t2entry, hhentry
    global allplotfunctions, data

    # GUI stuff
    top  = Tk.Tk()
    #top.geometry("800x400")
    top.wm_title("ABL stats")

    center = Tk.Frame(top)
    center.pack(side=Tk.RIGHT)

    leftframe=Tk.Frame(top)
    leftframe.pack(side=Tk.LEFT)

    # Set up the main plot
    fig=Figure(figsize=(8,8), facecolor='white') 
    canvas=FigureCanvasTkAgg(fig,master=center)
    toolbar = NavigationToolbar2TkAgg(canvas, center)
    toolbar.update()
    canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
    canvas.show()
    canvas.mpl_connect('key_press_event', on_key_event)

    # -- Set up radio bars --
    plotlist = [x[0] for x in allplotfunctions]
    allfiles_pane = ScrollableFrame(leftframe, bg='#444444')
    allfiles_pane.pack(expand="true", fill="both")
    plotfile = RadioBbar(allfiles_pane.interior, plotlist, "ABL stats")
    plotfile.pack(side=Tk.TOP)   

    # -- Set up some input boxes --
    # Averaging times
    t1label = Tk.Label(master=leftframe, text="Averaging t1")
    t1label.pack()
    t1entry = Tk.Entry(master=leftframe)
    t1entry.insert(0, repr(min(data.time)))
    t1entry.pack()

    t2label = Tk.Label(master=leftframe, text="Averaging t2")
    t2label.pack()
    t2entry = Tk.Entry(master=leftframe)
    t2entry.insert(0, repr(max(data.time)))
    t2entry.pack()
    # Plot heights
    defaultheights = repr(min(data.heights))+', '+repr(max(data.heights))

    hhlabel = Tk.Label(master=leftframe, text="Plot heights (comma sep)")
    hhlabel.pack()
    hhentry = Tk.Entry(master=leftframe)
    hhentry.insert(0, defaultheights)
    hhentry.pack()

    # Add buttons
    quitbutton  = Tk.Button(master=leftframe, text='Quit', command=_quit)
    quitbutton.pack(side=Tk.BOTTOM)
    reloadbutton=Tk.Button(master=leftframe, text="Reload Data", command=_reloaddata)
    reloadbutton.pack(side=Tk.TOP)
    plotbutton=Tk.Button(master=leftframe, text="Plot", command=_plotdata)
    plotbutton.pack(side=Tk.TOP)
    reportbutton=Tk.Button(master=leftframe, text="Print report", command=_reportABL)
    reportbutton.pack(side=Tk.TOP)

    saveallbutton=Tk.Button(master=leftframe, text="Save all", command=_saveallfigs)
    saveallbutton.pack(side=Tk.TOP)

    # Start the main loop
    Tk.mainloop()

def main():
    global allplotfunctions, data, filelist, nogui

    # Handle arguments
    parser = argparse.ArgumentParser(description='Plot sample mesh')
    parser.add_argument('ABLSTATSFILE', nargs='*',  help="Load data from this abl file")
    parser.add_argument('--nogui',    action='store_true', 
                        help="Use command line only [default=False]")
    parser.set_defaults(nogui=False)
    args=parser.parse_args()

    # Get the default and user arguments
    filelist  = args.ABLSTATSFILE
    nogui     = args.nogui

    # Load the data
    data = ABLStatsFileClass(stats_file=filelist[0])
    print("min time: %f"%min(data.time))
    print("max time: %f"%max(data.time))

    # Need at least one input
    if (len(filelist)<1):
        print("ERROR: At least one argument expected")
        print("")
        parser.print_help(sys.stderr)
        sys.exit(1)

    # Choose gui option or not
    if nogui:
        print("Nothing here")
    else:
        #dat, time, headers=loadplanefile(filelist[0])
        doGUI()

if __name__ == "__main__":
    main()
