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
import logging

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

    
def ReadNIFTI(NIFTIfile,logfilename,error_handling): #error_handling = "abort", "warn", "ignore"
  if error_handling == "ignore": logging.basicConfig(filename=os.devnull)
  else: logging.basicConfig(filename=logfilename)
  if error_handling == "abort": # -----> abort on warning/error write msg to screen/logfile
    nib.imageglobals.error_level = 30  #rise an error
    try:   
      with nib.imageglobals.LoggingOutputSuppressor(): # supresss onscreen message
        return nib.load(NIFTIfile)
    except Exception as err: 
      print ("Error reading NIFTI file: "+str(err)) # custom handle error message
      log.write ("Operation aborted\n"); log.flush() 
      sys.exit(2)
  elif error_handling == "warn": # -----> continue on warning/error write msg to screen/logfile
    try: return nib.load(NIFTIfile)
    except Exception as err: 
      print ("Error reading NIFTI file:", err);
      sys.exit(2)
  elif error_handling == "ignore": # -----> continue silently
      with nib.imageglobals.LoggingOutputSuppressor(): # supresss onscreen message
        return nib.load(NIFTIfile)
  else: print ("Unknown error handling mode", error_handling); sys.exit(0) 
  
  
#sanity check/correct Mask data
def SantitizeMask (data):
   if not np.array_equal(np.unique(data), np.asarray([0,1])):
      if np.unique(data).shape[0]!=2: # more than two values present
         data[data<0] = 0
         thresh = np.average (data[data>0])        
         print ("Warning: Mask contains more then two different values, trying to fix")
         log.write("Warning: Mask contains more then two different values, trying to fix\n"); log.flush()
         data[data<=thresh]=0; data[data>thresh]=1          
      else: # only two values present, easily corrected  
         print ("Warning: Mask contains values!=[0,1], trying to fix")
         log.write("Warning: Mask contains values!=[0,1], trying to fix\n"); log.flush()
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
logfilename = os.path.join(new_dirname,'Combined.log')
try: os.remove(logfilename)
except: pass
log = open(logfilename, "a")

# start doing something
log.write('Label file created from mask files:\n'); log.flush()
log.write("1) "+FIDfile[0]+'\n'); log.flush()
print ('Reading file 1: '+str(os.path.basename(FIDfile[0])))
img0 = ReadNIFTI(FIDfile[0], logfilename, "warn")
data0 = np.asanyarray(img0.dataobj).astype(np.float32)
data0 = SantitizeMask (data0)
#go
for i in range (1,nfiles):
    log.write(str(i+1)+") "+FIDfile[i]+'\n'); log.flush()
    print ('Reading file '+str(i+1)+": "+str(os.path.basename(FIDfile[i])))
    img = ReadNIFTI(FIDfile[i], logfilename, "warn")
    data = np.asanyarray(img.dataobj).astype(np.float32)
    #verify if dimensions are equal
    if data.shape != data0.shape:
       print ("ERROR: Mask file has different dimensions, aborting")
       log.write("ERROR: Mask file has different dimensions, aborting\n"); log.flush()
       sys.exit(2)      
    data = SantitizeMask (data)
    #check for overlaping masks    
    nonzero  = np.nonzero(data)
    if not np.array_equal(np.unique(data0[nonzero]), np.asarray([0])):
       print ("Warning: Mask overlap detected, overwriting previous values") 
       log.write("Warning: Mask overlap detected, overwriting previous values\n"); log.flush()       
    data0[nonzero] = 1
#sanity check result
expected = np.asarray([0,1])
if not np.array_equal(np.unique(data0), expected):
    print ("Warning: Resulting file Label.nii contains unexpected values, please check carefully") 
    log.write("Warning: Resulting file Label.nii contains unexpected values, please check carefully\n"); log.flush()
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
nib.save(img_SoS, os.path.join(new_dirname,new_filename))   
log.close()
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
