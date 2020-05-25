#!/usr/local/fsl/fslpython/bin/python3
#
# reads a NIFTI Label file containing integer values 0..N
# and writes N separate mask files (each one with values 0 and 1)
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
from scipy.ndimage import label
from scipy.ndimage import binary_opening
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
    
#intercatively choose input FID file and read data
FIDfile = askopenfilename(title="Choose NIFTI MASK file (press cancel to end)", filetypes=[("NIFTI files",('*.nii','*.nii.gz'))])
if FIDfile=="": print ('ERROR: No input file specified'); sys.exit(2)
FIDfile = os.path.abspath(FIDfile)
img0 = nib.load(FIDfile)
data0 = np.asanyarray(img0.dataobj)
if len(data0.shape) != 3:print ('ERROR: Input is not a 3D NIFTI file'); sys.exit(2) 
if not (type(data0[0,0,0])==np.int16 or type(data0[0,0,0])==np.int8 or type(data0[0,0,0])==np.uint16 or type(data0[0,0,0])==np.uint8):
   print ('Warning: Input file is not Integer, converting, please check results carefully')
   data0 = data0.astype(np.int16) 
dirname  = os.path.dirname(FIDfile)
basename = os.path.splitext(os.path.basename(FIDfile))[0]
   
TKwindows.update()
try: win32gui.SetForegroundWindow(win32console.GetConsoleWindow())
except: pass #silent

labels = np.unique(data0)
nfiles = labels.shape[0]
j=0
for i in range (0,nfiles):
   if labels[i]!=0:
      data = data0.copy()
      data[data>labels[i]]=0
      data[data<labels[i]]=0
      data[data==labels[i]]=1
      j+=1
      print ("Creating Mask "+str(j)+" with value "+str(labels[i])+", ", end="")
      labeled_data, num_clusters = label(data)
      unique, counts = np.unique(labeled_data, return_counts=True)
      if (unique.shape[0])>2: #filtering required
         # remove isolated clusters
         print ("removing isolated, ", end="")
         max_count=0
         for k in range(0,unique.shape[0]): # find the largest nonzero count
            if counts[k]>max_count and unique[k]!=0: max_count=counts[k]
         remove_labels = unique[np.where(counts<max_count)] # leave only the largest cluster of connected points
         remove_indices = np.where(np.isin(labeled_data,remove_labels))
         data[remove_indices] = 0
         #filter mask (opening filter)
         print ("opening filter, ", end="")
         data = binary_opening(data, iterations=2).astype(np.int16)
      if np.max(data)==0:
          print ("zero result")
      elif data[data>0].flatten().shape[0]<4:
          print ("too few points: ", data[data>0].flatten().shape[0])            
      else:            
          print ("saving")
          affine = img0.affine
          sform = int(img0.header['sform_code'])
          qform = int(img0.header['qform_code'])
          unit_xyz, unit_t = img0.header.get_xyzt_units()
          if unit_xyz == 'unknown': unit_xyz=0
          if unit_t   == 'unknown': unit_t=0
          img_SoS = nib.Nifti1Image(data, affine)
          img_SoS.header.set_xyzt_units(unit_xyz, unit_t)
          img_SoS.set_sform(affine, code=sform)
          img_SoS.set_qform(affine, code=qform)
          img_SoS.header.set_slope_inter(1,0)
          #duno if this is needed
          img_SoS.header['cal_max']=np.max(data)
          img_SoS.header['extents']=np.min(data)
          img_SoS.header['regular']=img0.header['regular']
          img_SoS.header['scl_slope']=1
          img_SoS.header['scl_inter']=0
          img_SoS.header['glmax']=np.max(data)
          img_SoS.header['glmin']=np.min(data)
          nib.save(img_SoS, os.path.join(dirname,basename+"_MASK_"+str(labels[i])))   
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
