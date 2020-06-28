#!/usr/local/fsl/fslpython/bin/python3
#
# calculates the average based on the first NIFTI input image
# using the second NIFTI input image as weights
#
# ----- VERSION HISTORY -----
#
# Version 0.1 - 08, May 2020
#       - 1st public github Release
#
# ----- LICENSE -----                 
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#    For more detail see the GNU General Public License.
#    <http://www.gnu.org/licenses/>.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#    THE SOFTWARE.
#
# ----- REQUIREMENTS ----- 
#
#    This program was developed under Python Version 3.7
#    with the following additional libraries: 
#    - numpy
#    - nibabel
#


from __future__ import print_function
try: import win32gui, win32console
except: pass #silent
import sys
import os
import numpy as np
import nibabel as nib
import warnings 
warnings.filterwarnings("ignore") # disable numpy runtime warnings

TK_installed=True
try: from tkFileDialog import askopenfilename # Python 2
except: 
    try: from tkinter.filedialog import askopenfilename; # Python3
    except: TK_installed=False
try: import Tkinter as tk; # Python2
except: 
    try: import tkinter as tk; # Python3
    except: TK_installed=False
if not TK_installed:
    print ('ERROR: tkinter not installed')
    print ('       on Linux try "yum install tkinter"')
    print ('       on MacOS install ActiveTcl from:')
    print ('       http://www.activestate.com/activetcl/downloads')
    sys.exit(2)

def smooth(x,window_len):
    w=np.hanning(window_len)
    s=np.r_[2*x[0]-x[window_len-1::-1],x,2*x[-1]-x[-1:-window_len:-1]]
    w=np.hanning(window_len)
    y=np.convolve(w/w.sum(),s,mode='same')
    return y[window_len:-window_len+1]    
    
#general initialization stuff  
Program_name = os.path.basename(sys.argv[0]); 
if Program_name.find('.')>0: Program_name = Program_name[:Program_name.find('.')]
python_version=str(sys.version_info[0])+'.'+str(sys.version_info[1])+'.'+str(sys.version_info[2])
# sys.platform = [linux2, win32, cygwin, darwin, os2, os2emx, riscos, atheos, freebsd7, freebsd8]
if sys.platform=="win32": os.system("title "+Program_name)
    
#TK initialization       
TKwindows = tk.Tk(); TKwindows.withdraw() #hiding tkinter window
TKwindows.update()
# the following tries to disable showing hidden files/folders under linux
try: TKwindows.tk.call('tk_getOpenFile', '-foobarz')
except: pass
try: TKwindows.tk.call('namespace', 'import', '::tk::dialog::file::')
except: pass
try: TKwindows.tk.call('set', '::tk::dialog::file::showHiddenBtn', '1')
except: pass
try: TKwindows.tk.call('set', '::tk::dialog::file::showHiddenVar', '0')
except: pass
TKwindows.update()
    
#intercatively choose first input file
FIDfile0 = askopenfilename(title="Choose first NIFTI file (e.g. FA)", filetypes=[("NIFTI files",('*.nii','*.nii.gz'))])
if FIDfile0=="": print ('ERROR: No input file specified'); sys.exit(2)
FIDfile = os.path.abspath(FIDfile0)
img0 = nib.load(FIDfile0)
data0 = np.asanyarray(img0.dataobj)
if len(data0.shape) != 3:print ('ERROR: Input is not a 3D NIFTI file'); sys.exit(2) 
if np.max(data0)>10: print ('ERROR: Input file does not look like a Diffusion Image'); sys.exit(2)

#intercatively choose second input file
FIDfile1 = askopenfilename(title="Choose second NIFTI file (for weighting)", filetypes=[("NIFTI files",('*.nii','*.nii.gz'))])
if FIDfile1=="": print ('ERROR: No input file specified'); sys.exit(2)
FIDfile1 = os.path.abspath(FIDfile1)
img1 = nib.load(FIDfile1)
data1 = np.asanyarray(img1.dataobj)
if len(data1.shape) != 3:print ('ERROR: Input is not a 3D NIFTI file'); sys.exit(2) 
   
TKwindows.update()
try: win32gui.SetForegroundWindow(win32console.GetConsoleWindow())
except: pass #silent

#names based on first file
dirname  = os.path.dirname(FIDfile0)
basename0 = os.path.splitext(os.path.basename(FIDfile0))[0]; basename0 = os.path.splitext(basename0)[0]
basename1 = os.path.splitext(os.path.basename(FIDfile1))[0]; basename1 = os.path.splitext(basename1)[0]

#dimension verification
if data0.shape != data1.shape: print ("ERROR: Images must have same dimensions"); sys.exit(1)

#calculate
print ("Voxel Statistics:")
print ("  Simple average = ", np.average(data0[data1>0]))
print ("  Weighted average = ", np.average(data0, weights=data1))
print ("  Median  = ", np.median(data0[data1>0]))
print ("  Minimum = ", np.min(data0[data1>0]))
print ("  Maximum = ", np.max(data0[data1>0]))
print ("  Number of voxels evaluated = ", data0[data1>0].shape[0])
print ("")

'''
print ("Voxel Statistics corrected (0<FA<=1")
data0 = data0[data1>0]
data1 = data1[data1>0]
data1 = data1[data0>0]
data0 = data0[data0>0]
data1 = data1[data0<=1]
data0 = data0[data0<=1]
print ("")
print ("  Simple average = ", np.average(data0[data1>0]))
print ("  Weighted average = ", np.average(data0, weights=data1))
print ("  Median  = ", np.median(data0[data1>0]))
print ("  Minimum = ", np.min(data0[data1>0]))
print ("  Maximum = ", np.max(data0[data1>0]))
print ("  Number of voxels evaluated = ", data1[data1>0].shape[0])
print ("")
'''

#calculate histogram
npoints = np.prod(data0[data1>0].shape)
steps = int(np.sqrt(npoints)) 
start = np.min(data0[data1>0])
fin   = np.max(data0[data1>0])
xbins =  np.linspace(start,fin,steps)
ybins, binedges = np.histogram(data0[data1>0], bins=xbins)
ybins = np.resize (ybins,len(xbins)); ybins[len(ybins)-1]=0

#write histogram results
with open(os.path.join(dirname,basename0.replace("_","")+'_Histogram.csv'), "w") as csv_file:    
    for i in range(0,xbins.shape[0]-2):     
        csv_file.write("%e,%e\n" % (xbins[i], ybins[i]))
    csv_file.write("\n")  


#join arrays
data0 = data0.flatten(); data1 = data1.flatten();
nz = np.nonzero(data1); data0 = data0[nz]; data1 = data1[nz] # remove zeros
data=np.column_stack((data0, data1))

#sort data
data = data[data[:,0].argsort()] # First sort doesn't need to be stable.
data = data[data[:,1].argsort(kind='mergesort')]

#write (1 versus 0) csv (all)
name=basename0.replace("_","")+"_versus_"+basename1.replace("_","")+"_(all).csv"
csv=open(os.path.join(dirname,name), "w")
for i in range (0,data.shape[0]): csv.write (str(data[i,1])+","+str(data[i,0])+"\n")
csv.close()

#remove more zeros
zero_idx = np.where(data[:,0]==0); 
data = np.delete (data,zero_idx, axis=0)

#reduce array size
data_reduced=np.asarray([[0,0],[0,0]]) #initialize with correct shape
un1 = np.unique(data[:,1])
ytarget = 10
xtarget = 20
xreduce = int(un1.shape[0]/xtarget)
for i in range (0,un1.shape[0]):
    temp=data[data[:,1]==un1[i]]
    if i % xreduce == 0 or temp.shape[0]<ytarget:
      if temp.shape[0]>2*ytarget:
        yreduce=int(temp.shape[0]/ytarget)
      else:
        yreduce=1
      new_entry = np.asarray (temp[::yreduce,:])   
      data_reduced = np.append(data_reduced,new_entry,axis=0) 
data_reduced = data_reduced[2:,:] # remove initialize values with correct shape

#further reduce array size randomly
if data_reduced.shape[0]>5000:
  numbers = np.arange(data_reduced.shape[0]); np.random.shuffle(numbers)
  numbers = numbers[0:5000]
  data_reduced = data_reduced[numbers,:]
  #sort data again
  data_reduced = data_reduced[data_reduced[:,0].argsort()] # First sort doesn't need to be stable.
  data_reduced = data_reduced[data_reduced[:,1].argsort(kind='mergesort')]

#write (1 versus 0) csv (reduced)
name=basename0.replace("_","")+"_versus_"+basename1.replace("_","")+"_(reduced).csv"
csv=open(os.path.join(dirname,name), "w")
for i in range (0,data_reduced .shape[0]): csv.write (str(data_reduced [i,1])+","+str(data_reduced [i,0])+"\n")
csv.close()
   
     
#end
if sys.platform=="win32": os.system("pause") # windows
else: 
    #os.system('read -s -n 1 -p "Press any key to continue...\n"')
    import termios
    print("Press any key to continue...")
    fd = sys.stdin.fileno()
    oldterm = termios.tcgetattr(fd)
    newattr = termios.tcgetattr(fd)
    newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
    termios.tcsetattr(fd, termios.TCSANOW, newattr)
    try: result = sys.stdin.read(1)
    except IOError: pass
    finally: termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
