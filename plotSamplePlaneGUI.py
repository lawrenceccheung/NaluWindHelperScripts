#!/usr/bin/env python

# Following some previous people's work in 
# https://www.javatpoint.com/python-tkinter-frame
# https://www.python-course.eu/tkinter_checkboxes.php
# https://stackoverflow.com/questions/30774281/update-matplotlib-plot-in-tkinter-gui

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


# Load all of the information needed from the file
def loadplanefile(filename):
    dat=loadtxt(filename, skiprows=2)
    # Get the maximum indices
    numplanes = int(max(dat[:,0]))
    Numj      = int(max(dat[:,1]))
    Numi      = int(max(dat[:,2]))
    #print numplanes, Numi, Numj
    with open(filename) as fp:
        timestring = fp.readline().strip().split()[1]
        headers    = fp.readline().strip().split()[1:]
    time=float(timestring)
    #print time, headers
    fp.close()
    return dat, time, headers
    
def getplotplane(dat, planenum, col):
    Numj      = int(max(dat[:,1]))+1
    Numi      = int(max(dat[:,2]))+1

    planedat=dat[dat[:,0]==planenum,:]
    plotplane=planedat[:,[1,2,col]]

    # Get the corner point
    cornerrow =planedat[(planedat[:,1]==0)&(planedat[:,2]==0),:][0][3:6]
    dxrow     =planedat[(planedat[:,1]==0)&(planedat[:,2]==1),:][0][3:6]
    dyrow     =planedat[(planedat[:,1]==1)&(planedat[:,2]==0),:][0][3:6]

    dX=linalg.norm(array(dxrow)-array(cornerrow))
    dY=linalg.norm(array(dyrow)-array(cornerrow))

    # Get the X, Y, Z arrays
    Y=reshape(plotplane[:,0], (Numj, Numi))*dY
    X=reshape(plotplane[:,1], (Numj, Numi))*dX
    Z=reshape(plotplane[:,2], (Numj, Numi))
    return X, Y, Z

# Plots all of the data
def _plotdata():
    global fig, canvas, plotvar, planen, toolbar, plotfile
    fig.clf()
    ax=fig.add_subplot(111)
    ax.clear()
    # Load the file to plot
    filename=filelist[plotfile.state()]
    dat, time, headers=loadplanefile(filename)
    
    # Select the options to plot
    plotcol=plotvar.state()
    planenum=planen.state()
    X,Y,Z=getplotplane(dat, planenum, plotcol)
    im=ax.contourf(X, Y, Z)
    im.autoscale()
    cb=fig.colorbar(im, ax=ax)
    ax.axis('equal')
    ax.set_title('Time = %.3f %s'%(time, headers[plotcol]))
    canvas.draw()
    toolbar.update()
    fig.tight_layout()
    canvas.show()

# Run all of the gui elements
def doGUI():
    global fig, canvas, plotvar, planen, toolbar, plotfile, center
    # GUI stuff
    top  = Tk.Tk()
    #top.geometry("800x400")
    top.wm_title("Sample Plane Visualization")

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
    filelist2 = [os.path.basename(x) for x in filelist]
    allfiles_pane = ScrollableFrame(leftframe, bg='#444444')
    allfiles_pane.pack(expand="true", fill="both")
    plotfile = RadioBbar(allfiles_pane.interior, filelist2, "Plane files")
    plotfile.pack(side=Tk.TOP)
    
    allvars_pane = ScrollableFrame(leftframe, bg='#444444')
    allvars_pane.pack(expand="true", fill="both")
    plotvar = RadioBbar(allvars_pane.interior, headers[3:], "Plot variables", 3)
    plotvar.v.set(plotcol)
    plotvar.pack(side=Tk.TOP)

    numplanes = int(max(dat[:,0]))
    planen_pane = ScrollableFrame(leftframe, height=100, bg='#444444')
    planen_pane.pack(expand="true", fill="both")
    planen = RadioBbar(planen_pane.interior, arange(numplanes+1), "Plane number")
    planen.v.set(planenum)
    planen.pack(side=Tk.TOP)

    # Add buttons
    quitbutton  = Tk.Button(master=leftframe, text='Quit', command=_quit)
    quitbutton.pack(side=Tk.BOTTOM)
    plotbutton=Tk.Button(master=leftframe, text="Plot", command=_plotdata)
    plotbutton.pack(side=Tk.TOP)
    # Start the main loop
    Tk.mainloop()

def main():
    global filelist, planenum, plotcol
    global dat, time, headers

    # Handle arguments
    parser = argparse.ArgumentParser(description='Plot sample mesh')
    parser.add_argument('PLANEFILE',  nargs='*',  help="Plot these sample plane(s)")
    parser.add_argument('--nogui',    action='store_true', 
                        help="Use command line only [default=False]")
    parser.set_defaults(nogui=False)
    parser.add_argument('--planenum', default=0,   help="Plot this plane number")
    parser.add_argument('--varnum',   default=6,   help="Plot this variable number")
    args=parser.parse_args()

    # Get the default and user arguments
    filelist  = args.PLANEFILE
    nogui     = args.nogui
    planenum  = int(args.planenum)
    plotcol   = int(args.varnum)

    # Need at least one input
    if (len(filelist)<1):
        print("ERROR: At least one argument expected")
        print("")
        parser.print_help(sys.stderr)
        sys.exit(1)

    # Choose gui option or not
    if nogui:
        if (len(filelist)>1):
            planefile = filelist[0]
        else:
            sys.exit('One PLANEFILE required in command line mode')
        dat, time, headers=loadplanefile(planefile)
        X,Y,Z=getplotplane(dat, planenum, plotcol)
        plt.contourf(X, Y, Z)
        plt.colorbar()
        plt.axis('equal')
        plt.title('Time = %.3f %s'%(time, headers[plotcol]))
        plt.show()
    else:
        dat, time, headers=loadplanefile(filelist[0])
        doGUI()

if __name__ == "__main__":
    main()
