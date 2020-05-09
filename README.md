# Label-Mask-tools

### Definitions:  
* __Masks__ contain one region represented by pixel values of 1 and 0 backgroud  
* __Label__ contain N>1 regions represented by pixel values ranging from 1 to N on 0 background  

### Tools:  
* __NIFTI_Label2Masks__:  converts a Label file to several Masks files  
* __NIFTI_CombineMasks__: combines several Mask files into a single Mask file  
* __NIFTI_Masks2Label__:  converts several Mask files to a Label file  
<br/>

You may test these tools with the data kindly provided by the  
Laboratory for Rehabilitation Neuroscience at the University of Florida  
available at http://lrnlab.org/  
<br/>
    
These tools are intended to be used in __FSL__ (https://fsl.fmrib.ox.ac.uk/fsl/fslwiki).  
In order to be able to execute the tools in the Python environment provided by FSL  
__please install__ the NumPy, SciPy and NiBabel libaries with the command  
__sudo /usr/local/fsl/fslpython/bin/pip install numpy scipy nibabel__  
inside the FSL Virtual machine (tested on FSL 6.0.3)   
<br/>

If you have installed FSL in a non default home directory,  
or intend to use these tools in a different python environment,  
please edit the first line in the Python files to reflect the correct  
location of your Python interpreter  
  
  
