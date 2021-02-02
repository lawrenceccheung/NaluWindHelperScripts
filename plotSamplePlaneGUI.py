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
import gzip

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
# --- need to fix checkcomma!!! --- 
def loadplanefile(filename, checkcomma=False, coordfile=''):
    hascomma=False
    if checkcomma:
        with open(filename) as f:
            if ',' in f.read(): hascomma=True
        f.close()
    # Load the file
    if hascomma:
        with open(filename) as infile:
            temp=infile.read().replace(",","")
        infile.close()
        dat2=[map(float, y.split()) for y in temp.split("\n")[2:]]
        mdat=array(filter(None, dat2))
    else:
        mdat=loadtxt(filename, skiprows=2)
    # Load coordinate data file
    if len(coordfile)>0:
        cdat=loadtxt(coordfile, skiprows=2)
        dat = hstack((cdat, mdat))
    else:
        dat = mdat
    # Get the maximum indices
    numplanes = int(max(dat[:,0]))
    Numj      = int(max(dat[:,1]))
    Numi      = int(max(dat[:,2]))
    #print numplanes, Numi, Numj
    fname, fext = os.path.splitext(filename)
    headers=[]
    # Load the headers from the coordfile
    if len(coordfile)>0:
        if ((fext == '.gz') or (fext == '.GZ')):
            with gzip.open(coordfile) as fp:
                junk = fp.readline().strip().split()[1]
                headers.extend(fp.readline().strip().split()[1:])
        else:
            with open(coordfile) as fp:
                junk = fp.readline().strip().split()[1]
                headers.extend(fp.readline().strip().split()[1:])        
    # Else just use the one file headers
    if ((fext == '.gz') or (fext == '.GZ')):
        with gzip.open(filename) as fp:
            timestring = fp.readline().strip().split()[1]
            headers.extend(fp.readline().strip().split()[1:])
    else:
        with open(filename) as fp:
            timestring = fp.readline().strip().split()[1]
            headers.extend(fp.readline().strip().split()[1:])
    time=float(timestring.replace(",",""))
    #print time, headers
    fp.close()
    return dat, time, headers

def evalexpr(expr, data, varnames):
    answer=expr
    for ivar, var in enumerate(varnames):
        answer=answer.replace(var, repr(data[ivar]))
    return eval(answer)
    
def getplotplane(dat, planenum, col, expr='',headers=[]):
    Numj      = int(max(dat[:,1]))+1
    Numi      = int(max(dat[:,2]))+1

    planedat=dat[dat[:,0]==planenum,:]
    plotplane=planedat[:,[1,2,col]]

    if len(expr)>0:
        if len(headers)==0: 
            print('need headers in getplotplane')
            sys.exit(1)
        for irow in range(len(plotplane)):
            planerow = planedat[irow, :]
            plotplane[irow, 2] = evalexpr(expr, planerow, headers)

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
    global fig, canvas, plotvar, planen, toolbar, plotfile, colormap, icoordfile
    global expr
    nlevels=20
    fig.clf()
    ax=fig.add_subplot(111)
    ax.clear()
    # Load the file to plot
    filename=filelist[plotfile.state()]
    dat, time, headers=loadplanefile(filename, coordfile=icoordfile)
    
    # Select the options to plot
    plotcol=plotvar.state()
    if plotcol==len(headers):
        plotcol=0
        plotexpr=expr
        plottitle=expr
    else:
        plotexpr=''
        plottitle=headers[plotcol]
    planenum=planen.state()
    X,Y,Z=getplotplane(dat, planenum, plotcol, expr=plotexpr, headers=headers)
    im=ax.contourf(X, Y, Z, nlevels, cmap=colormap)
    im.autoscale()
    cb=fig.colorbar(im, ax=ax)
    ax.axis('equal')
    #ax.set(ylim=(min(Y[:,0]), max(Y[:,0])))
    ax.set(xlim=(min(X[0,:]), max(X[0,:])))
    ax.set_title('Time = %.3f %s'%(time, plottitle))
    canvas.draw()
    toolbar.update()
    fig.tight_layout()
    canvas.show()

# Run all of the gui elements
def doGUI():
    global fig, canvas, plotvar, planen, toolbar, plotfile, center
    global expr
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
    plotoptions=headers[3:]
    if len(expr)>0: plotoptions.append(expr)
    plotvar = RadioBbar(allvars_pane.interior, plotoptions, "Plot variables", 3)
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
    global filelist, planenum, plotcol, colormap, icoordfile
    global dat, time, headers, expr

    # Handle arguments
    parser = argparse.ArgumentParser(description='Plot sample mesh')
    parser.add_argument('PLANEFILE',  nargs='*',  help="Plot these sample plane(s)")
    parser.add_argument('--nogui',    action='store_true', 
                        help="Use command line only [default=False]")
    parser.set_defaults(nogui=False)
    parser.add_argument('--planenum', default=0,   help="Plot this plane number")
    parser.add_argument('--varnum',   default=6,   help="Plot this variable number")
    parser.add_argument('--expr',     default='',  help="Plot this expression")
    parser.add_argument('--cmap',     default='coolwarm',  help="Specify colormap to use")
    parser.add_argument('--figsetup', default='',  help="execute FIGSETUP string before plotting")
    parser.add_argument('--vmax',     default=None,help="Specify maximum color range")
    parser.add_argument('--vmin',     default=None,help="Specify minimum color range")
    parser.add_argument('--coordfile',default='',  help="Specify coordinate file")
    parser.add_argument('--savefile', default='',  help="Save plot to this file")
    parser.add_argument('--batchmode',action='store_true', 
                        help="Use batch mode [default=False]")
    parser.set_defaults(batchmode=False)
    
    args=parser.parse_args()

    # Get the default and user arguments
    filelist  = args.PLANEFILE
    nogui     = args.nogui
    planenum  = int(args.planenum)
    plotcol   = int(args.varnum)
    expr      = args.expr
    colormap  = args.cmap
    figsetup  = args.figsetup
    vmax      = args.vmax
    vmin      = args.vmin
    icoordfile= args.coordfile
    savefile  = args.savefile
    batchmode = args.batchmode

    # Need at least one input
    if (len(filelist)<1):
        print("ERROR: At least one argument expected")
        print("")
        parser.print_help(sys.stderr)
        sys.exit(1)

    # Choose gui option or not
    if nogui:
        if (len(filelist)>=1):
            planefile = filelist[0]
        else:
            sys.exit('One PLANEFILE required in command line mode')
        dat, time, headers=loadplanefile(planefile, coordfile=icoordfile, checkcomma=False)
        if len(figsetup)>0: exec(figsetup)
        X,Y,Z=getplotplane(dat, planenum, plotcol, expr=expr, headers=headers)
        nlevels=21
        cmax = amax(Z) if vmax is None else float(vmax)
        cmin = amin(Z) if vmin is None else float(vmin)
        clevels=linspace(cmin, cmax,nlevels)
        plt.contourf(X, Y, Z, clevels, cmap=colormap)
        plt.colorbar()
        plt.axis('equal')
        if len(expr)>0:
            plt.title('Time = %.3f %s'%(time, expr))
        else:
            plt.title('Time = %.3f %s'%(time, headers[plotcol]))
        if len(savefile)>0: plt.savefig(savefile)
        if not batchmode:   plt.show()
    else:
        dat, time, headers=loadplanefile(filelist[0], coordfile=icoordfile)
        print(headers)
        doGUI()

if __name__ == "__main__":
    main()
