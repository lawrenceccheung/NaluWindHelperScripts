#!/usr/bin/env python

# Following some previous people's work in 
# https://www.javatpoint.com/python-tkinter-frame
# https://www.python-course.eu/tkinter_checkboxes.php
# https://stackoverflow.com/questions/30774281/update-matplotlib-plot-in-tkinter-gui

from numpy import *
import matplotlib
matplotlib.use('TkAgg')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg #, NavigationToolbar2TkAgg
# implement the default mpl key bindings
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from itertools import cycle

import sys
if sys.version_info[0] < 3:
    import Tkinter as Tk
else:
    import tkinter as Tk

# Load NavigationToolbar2TkAgg
try:
    # For newer matplotlibs
    from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk as NavigationToolbar2TkAgg
except:
    # For older matplotlibs
    from matplotlib.backends.backend_tkagg import NavigationToolbar2TkAgg

##################
def loadoutfile(filename):
    # load the data file
    dat=loadtxt(filename, skiprows=8)
    # get the headers and units
    with open(filename) as fp:
        fp.readline() # blank
        fp.readline() # When FAST was run 
        fp.readline() # linked with...
        fp.readline() # blank
        fp.readline() # Description of FAST input file
        fp.readline() # blank
        varsline=fp.readline()
        unitline=fp.readline()
        headers=varsline.strip().split()
        units  =unitline.strip().split()
    return dat, headers, units

def loadalldata(allfiles):
    adat=[]
    header0=[]
    units0=[]
    names=[]
    for ifile, file in enumerate(allfiles):
        names.append(file)
        print("Loading file "+file)
        dat, headers, units = loadoutfile(file)
        adat.append(dat)
        if ifile==0:
            header0 = headers
            units0   = units
        else:
            if ((len(header0) != len(headers)) or (len(units0)!=len(units))):
                print("Data sizes doesn't match")
                sys.exit(1)
    return adat, header0, units0, names

class ScrollableFrame(Tk.Frame):
    def __init__(self, master, **kwargs):
        Tk.Frame.__init__(self, master, **kwargs)

        # create a canvas object and a vertical scrollbar for scrolling it
        self.vscrollbar = Tk.Scrollbar(self, orient=Tk.VERTICAL)
        self.vscrollbar.pack(side='right', fill="y",  expand="false")
        self.canvas = Tk.Canvas(self,
                                bg='#444444', bd=0,
                                width=150, height=500,
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

class Checkbar(Tk.Frame):
   def __init__(self, parent=None, picks=[], side=Tk.LEFT, anchor=Tk.W):
      Tk.Frame.__init__(self, parent)
      self.vars = []
      for pick in picks:
         var = Tk.IntVar()
         chk = Tk.Checkbutton(self, text=pick, variable=var)
         chk.pack(side=Tk.TOP, anchor=anchor, expand=Tk.YES)
         self.vars.append(var)
   def state(self):
      return map((lambda var: var.get()), self.vars)

def on_key_event(event):
    key_press_handler(event, canvas, toolbar)
    if (event.key.upper()=='R'):
        print("Reloading data")
        _reloaddata()
    if (event.key.upper()=='P'):
        print("Plotting data")
        _plotdata()

# Plots all of the data
def _plotdata():
    global alldat
    lstyles=['-','-.','--','.']
    ax.clear()         # clear axes from previous plot
    plotlist=list(teststuff.state())
    ylabel=""
    for i,ploti in enumerate(plotlist[:]):
        if ploti==1: 
            color=next(colorcycle)
            for idat, dat in enumerate(alldat):
                print("plotting "+headers[i+1]+" ["+names[idat]+"]" )
                #print("data length: %i"%len(dat))
                ax.plot(dat[:,0], dat[:,i+1], linestyle=lstyles[idat],
                        color=color,
                        label=headers[i+1]+" "+units[i+1]+" ["+names[idat]+"]")
                canvas.draw()
    ax.set_xlabel(headers[0]+" "+units[0])
    ax.legend(prop={'size': 10})
    canvas.draw()
    toolbar.update()
    #canvas.show()

def _quit():
    center.quit()     # stops mainloop
    center.destroy()  # this is necessary on Windows to prevent
                      # Fatal Python Error: PyEval_RestoreThread: NULL tstate
    

# Check to make sure that there are enough arguments
if len(sys.argv)<2:
    print("Input files required")
    print("Usage: ")
    print(" "+sys.argv[0]+" FASTFILE1 [FASTFILE2 ... ]")
    sys.exit(1)

try:
    colorcycle=cycle(plt.rcParams['axes.color_cycle'])
except:
    colorcycle=cycle(plt.rcParams['axes.prop_cycle'].by_key()['color'])

# Load the data
alldat, headers, units, names=loadalldata(sys.argv[1:])
print(len(alldat[0]))

# Reloads the data from the file
def _reloaddata():
    global alldat
    alldat, headers, units, names=loadalldata(sys.argv[1:])

top  = Tk.Tk()
#top.geometry("800x400")
top.wm_title("FAST output")

center = Tk.Frame(top)
center.pack(side=Tk.RIGHT)

leftframe=Tk.Frame(top)
leftframe.pack(side=Tk.LEFT)

# Set up the main plot
fig=Figure(figsize=(8,8), facecolor='white')
ax=fig.add_axes([0.1,0.1,0.85,0.85])
canvas=FigureCanvasTkAgg(fig,master=center)
##canvas.get_tk_widget().grid(row=0,column=1)
toolbar = NavigationToolbar2TkAgg(canvas, center)
toolbar.update()
canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
#canvas.show()
canvas.draw()
canvas.mpl_connect('key_press_event', on_key_event)

# Get the scrollable checkbox frame
checkbox_pane = ScrollableFrame(leftframe, bg='#444444')
checkbox_pane.pack(expand="true", fill="both")
teststuff = Checkbar(checkbox_pane.interior, headers[1:])
teststuff.pack(side=Tk.TOP)

# Add buttons
plotbutton=Tk.Button(master=leftframe, text="Plot", command=_plotdata)
plotbutton.pack(side=Tk.TOP)

reloadbutton=Tk.Button(master=leftframe, text="Reload data",command=_reloaddata)
reloadbutton.pack(side=Tk.TOP)

quitbutton  = Tk.Button(master=leftframe, text='Quit', command=_quit)
quitbutton.pack(side=Tk.BOTTOM)

Tk.mainloop()
# If you put center.destroy() here, it will cause an error if
# the window is closed with the window manager.
