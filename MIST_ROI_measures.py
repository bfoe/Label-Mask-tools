#!/usr/local/fsl/fslpython/bin/python3
#
# reads mist*mask.nii.gz files (should contain only 0 and 1) from a specified MIST output foled
# calulates the volumes of the ROI's and outputs a CSV file
#
# ----- VERSION HISTORY -----
#
# Version 0.1 - 08, October 2020
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
from math import floor
import sys
import os
import numpy as np
import nibabel as nib
import fnmatch

TK_installed=True
try: from tkFileDialog import askopenfilename # Python 2
except: 
    try: from tkinter.filedialog import askopenfilename; # Python3
    except: TK_installed=False
try: from tkFileDialog import askdirectory # Python 2
except: 
    try: from tkinter.filedialog import askdirectory; # Python3
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


#sanity check/correct Mask data
def SantitizeMask (data):
   if not np.array_equal(np.unique(data), np.asarray([0,1])):
      if np.unique(data).shape[0]!=2: # more than two values present
         data[data<0] = 0
         thresh = np.average (data[data>0])        
         print ("Warning: Mask contains more then two different values, trying to fix")
         data[data<=thresh]=0; data[data>thresh]=1          
      else: # only two values present, easily corrected  
         print ("Warning: Mask contains values!=[0,1], trying to fix")
         data[data==np.min(np.unique(data))]=0; data[data==np.max(np.unique(data))]=1 
   return data

   
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
    
#intercatively choose input folder
folder = askdirectory(title="Select MIST subject folder ")
TKwindows.update()
try: win32gui.SetForegroundWindow(win32console.GetConsoleWindow())
except: pass #silent

#get files matching "mist_*_mask.nii.gz"
files = os.listdir(folder)
filenames = []
for name in files: 
  if fnmatch.fnmatch(name, "mist_*_mask.nii.gz"):
     filenames.append(name)
filenames.sort()
nfiles=len(filenames)
if nfiles<1: print ('No matching files found'); sys.exit(2)

# start doing something
out = open(os.path.join(folder,'MIST_ROI_measures.csv'), "w")
out.write ('Structure name\tVoxel count\tVolume[ml]\n')
for i in range (0,nfiles):
    img = nib.load(os.path.join(folder,filenames[i]))
    data = np.asanyarray(img.dataobj).astype(np.float32)
    data = SantitizeMask (data)
    nvoxels = data[data>0].shape[0]
    SpatResol = np.asarray(img.header.get_zooms())    
    volume = nvoxels * np.prod(SpatResol) /1000 # in mm^3   
    structure_name = filenames[i][5:].replace("_mask.nii.gz"," ").replace("_"," ").title()
    print (structure_name, "-", nvoxels, "voxels", "=", volume, "ml")
    out.write (structure_name+'\t'+str(nvoxels)+'\t'+str(volume)+'\n')
out.close()

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
