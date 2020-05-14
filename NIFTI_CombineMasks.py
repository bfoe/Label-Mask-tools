#!/usr/local/fsl/fslpython/bin/python3
#
# reads N mask NIFTI files (should contain only 0 and 1)
# and combines these to one Mask file containing ( also containing only 0 and 1)
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
#    - scipy
#    - nibabel
#


from __future__ import print_function
try: import win32gui, win32console
except: pass #silent
from math import floor
import sys
import os
import numpy as np
from scipy.ndimage import binary_closing
import nibabel as nib


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
    
    
#general initialization stuff  
space=' '; slash='/'; 
if sys.platform=="win32": slash='\\' # not really needed, but looks nicer ;)
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
    
#intercatively choose input FID files
nfiles=0
answer="dummy"
FIDfile=np.array([])
while answer!="":
   answer = askopenfilename(title="Choose NIFTI MASK file "+str(nfiles+1)+" (press cancel to end)", filetypes=[("NIFTI files",('*.nii','*.nii.gz'))])
   if answer!="":
        answer = os.path.abspath(answer)
        FIDfile = np.append(FIDfile, answer)
        nfiles+=1
if nfiles==0: print ('ERROR: No input file specified'); sys.exit(2)
if nfiles==1: print ('ERROR: Need at least 2 files'); sys.exit(2)
TKwindows.update()
try: win32gui.SetForegroundWindow(win32console.GetConsoleWindow())
except: pass #silent

new_dirname = os.path.abspath(os.path.dirname(FIDfile[0]))
new_filename = 'Combined.nii'
logfile = open(new_dirname+slash+'Combined.log', "w")
logfile.write('List of combined mask files:\n')
logfile.write("1) "+FIDfile[0]+'\n')

print ('Reading file 1')
img0 = nib.load(FIDfile[0])
data0 = np.asanyarray(img0.dataobj).astype(np.float32)
#sanity check data0
if not np.array_equal(np.unique(data0), np.asarray([0,1])):
   if np.unique(data0).shape[0]!=2: # more than two values present
      print ("Error: Mask contains more then two different values")
      sys.exit(2)
   else:   
      print ("Warning: Mask contains values!=[0,1], trying to fix")
      logfile.write("Warning: Mask contains values!=[0,1], trying to fix\n")
      data0[data0==np.min(np.unique(data0))]=0; data0[data0==np.max(np.unique(data0))]=1
#go
for i in range (1,nfiles):
    logfile.write(str(i+1)+") "+FIDfile[i]+'\n')
    print ('Reading file',i+1)
    img = nib.load(FIDfile[i])
    if img.shape != img0.shape: print ('ERROR: incompatible file dimensions'); sys.exit(2)
    data = np.asanyarray(img.dataobj).astype(np.float32)
    #verify if dimensions are equal
    if data.shape != data0.shape:
       print ("ERROR: Mask file has different dimensions, aborting")
       logfile.write("ERROR: Mask file has different dimensions, aborting\n")
       sys.exit(2)      
    #sanity check data   
    if not np.array_equal(np.unique(data), np.asarray([0,1])):
       if np.unique(data).shape[0]!=2: # more than two values present
          print ("Error: Mask contains more then two different values")
          sys.exit(2)
       else:   
          print ("Warning: Mask contains values!=[0,1], trying to fix")
          logfile.write("Warning: Mask contains values!=[0,1], trying to fix\n")
          data[data==np.min(np.unique(data))]=0; data[data==np.max(np.unique(data))]=1
    nonzero  = np.nonzero(data)
    #check for overlaping masks
    if not np.array_equal(np.unique(data0[nonzero]), np.asarray([0])):
       print ("Warning: Mask overlap detected, overwriting previous values") 
       logfile.write("Warning: Mask overlap detected, overwriting previous values\n")        
    data0[nonzero] = 1
#filter mask (closing filter)
print ("Applying closing filter, ", end="")
logfile.write("Applying closing filter\n")
data0 = binary_closing(data0).astype(np.int16)    
#sanity check result
expected = np.asarray([0,1])
if not np.array_equal(np.unique(data0), expected):
    print ("Warning: Resulting file Label.nii contains unexpected values, please check carefully") 
    logfile.write("Warning: Mask overlap detected, overwriting previous values\n")
data0 = data0.astype(np.int16)

print ("Saving results")
affine = img0.affine
sform = int(img0.header['sform_code'])
qform = int(img0.header['qform_code'])
unit_xyz, unit_t = img0.header.get_xyzt_units()
if unit_xyz == 'unknown': unit_xyz=0
if unit_t   == 'unknown': unit_t=0
img_SoS = nib.Nifti1Image(data0, affine)
img_SoS.header.set_xyzt_units(unit_xyz, unit_t)
img_SoS.set_sform(affine, code=sform)
img_SoS.set_qform(affine, code=qform)
img_SoS.header.set_slope_inter(1,0)
#duno if this is needed
img_SoS.header['cal_max']=np.max(data0)
img_SoS.header['extents']=np.min(data0)
img_SoS.header['regular']=img0.header['regular']
img_SoS.header['scl_slope']=1
img_SoS.header['scl_inter']=0
img_SoS.header['glmax']=np.max(data0)
img_SoS.header['glmin']=np.min(data0)
nib.save(img_SoS, new_dirname+slash+new_filename)   
logfile.close()
print ("done\n")  
     
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
