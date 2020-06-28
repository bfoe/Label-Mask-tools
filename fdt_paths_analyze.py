#!/usr/local/fsl/fslpython/bin/python3
#
# calculates statistics on the "fdt_paths" output from FSL probtack 
# and tries to automaticaly determina a threshold to divide theis file
# on containing only the lower values, 
# the other with high values (which are the more important ones)
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
from InputFloat import InputFloat
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


#intercatively choose second input file
FIDfile = askopenfilename(title='Choose probtack output file (normally called "fdt_paths.nii.gz")', filetypes=[("NIFTI files",('*.nii','*.nii.gz'))])
if FIDfile=="": print ('ERROR: No input file specified'); sys.exit(2)
FIDfile = os.path.abspath(FIDfile)
img1 = nib.load(FIDfile)
data1 = np.asanyarray(img1.dataobj)
if len(data1.shape) != 3:print ('ERROR: Input is not a 3D NIFTI file'); sys.exit(2) 
   
TKwindows.update()
try: win32gui.SetForegroundWindow(win32console.GetConsoleWindow())
except: pass #silent

#names based on first file
dirname  = os.path.dirname(FIDfile)
basename = os.path.splitext(os.path.basename(FIDfile))[0]; basename = os.path.splitext(basename)[0]

#copy data for later use
data1_low = data1.copy()
data1_high = data1.copy()

print ("Tract Statistics")
min_tract_per_voxel = int(round(np.min(data1),0))
avg_tract_per_voxel = round(np.average(data1[data1>0]),2)
median_tract_per_voxel = round(np.median(data1[data1>0]),2)
max_tract_per_voxel = int(round(np.max(data1),0))
print ("  Minimum number of tracts per voxel = ", min_tract_per_voxel)
print ("  Average number of tracts per voxel = ", avg_tract_per_voxel)
print ("  Median  number of tracts per voxel = ", median_tract_per_voxel)
print ("  Maximum number of tracts per voxel = ", max_tract_per_voxel)

#calculate histogram
steps = int(np.sqrt(np.prod(data1.shape))) 
start = np.min(data1[np.nonzero(data1)])
fin   = np.max(data1)
#xbins =  np.linspace(start,fin,steps)
xbins =  np.unique(np.logspace(np.log10(start),np.log10(fin),steps).astype(int))
ybins, binedges = np.histogram(data1, bins=xbins)
ybins = np.resize (ybins,len(xbins)); ybins[len(ybins)-1]=0

#write histogram results
with open(os.path.join(dirname,basename+'_Histogram.csv'), "w") as csv_file:    
    for i in range(0,xbins.shape[0]-2):     
        csv_file.write("%e,%e\n" % (xbins[i], ybins[i]))
    csv_file.write("\n")  
    
#find histogram threshold
ln_ybins = smooth(np.log(ybins),11)
diff1_ln_ybins = np.abs(smooth(np.diff(ln_ybins, n=1),11))
i=0;minx=0;miny=diff1_ln_ybins[0]
while i<len(diff1_ln_ybins):
    i+=1
    if diff1_ln_ybins[i]<=miny: miny=diff1_ln_ybins[i]; minx=i; 
    else: i=len(diff1_ln_ybins);
threshold=xbins[minx]  
threshold = InputFloat('  Found threshold at', threshold, 10) 
  
'''
print ("")
data1 = data1[data1>threshold]
print ("Reevaluating Tract Statistics")
min_tract_per_voxel = int(round(np.min(data1),0))
avg_tract_per_voxel = round(np.average(data1[data1>0]),2)
median_tract_per_voxel = round(np.median(data1[data1>0]),2)
max_tract_per_voxel = int(round(np.max(data1),0))
print ("  Minimum number of tracts per voxel = ", min_tract_per_voxel)
print ("  Average number of tracts per voxel = ", avg_tract_per_voxel)
print ("  Median  number of tracts per voxel = ", median_tract_per_voxel)
print ("  Maximum number of tracts per voxel = ", max_tract_per_voxel)
'''

#apply treshold
data1_low[data1_low>threshold]=0
data1_high[data1_high<=threshold]=0


#save files
affine = img1.affine
sform = int(img1.header['sform_code'])
qform = int(img1.header['qform_code'])
unit_xyz, unit_t = img1.header.get_xyzt_units()
if unit_xyz == 'unknown': unit_xyz=0
if unit_t   == 'unknown': unit_t=0
print ("Saving File "+basename+"_low.nii.gz")
img_SoS = nib.Nifti1Image(data1_low, affine)
img_SoS.header.set_xyzt_units(unit_xyz, unit_t)
img_SoS.set_sform(affine, code=sform)
img_SoS.set_qform(affine, code=qform)
img_SoS.header.set_slope_inter(1,0)
img_SoS.header['cal_max']=np.max(data1_low)
img_SoS.header['extents']=np.min(data1_low)
img_SoS.header['regular']=img1.header['regular']
img_SoS.header['scl_slope']=1
img_SoS.header['scl_inter']=0
img_SoS.header['glmax']=np.max(data1_low)
img_SoS.header['glmin']=np.min(data1_low)
nib.save(img_SoS, os.path.join(dirname,basename+"_low.nii.gz"))
print ("Saving File "+basename+"_high.nii.gz")
img_SoS = nib.Nifti1Image(data1_high, affine)
img_SoS.header.set_xyzt_units(unit_xyz, unit_t)
img_SoS.set_sform(affine, code=sform)
img_SoS.set_qform(affine, code=qform)
img_SoS.header.set_slope_inter(1,0)
img_SoS.header['cal_max']=np.max(data1_high)
img_SoS.header['extents']=np.min(data1_high)
img_SoS.header['regular']=img1.header['regular']
img_SoS.header['scl_slope']=1
img_SoS.header['scl_inter']=0
img_SoS.header['glmax']=np.max(data1_high)
img_SoS.header['glmin']=np.min(data1_high)
nib.save(img_SoS, os.path.join(dirname,basename+"_high.nii.gz"))
     
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
