# Label-Mask-tools

Definitions:
  Masks contain one region represented by pixel values of 1 and 0 backgroud
  Label contain N>1 regions represented by pixel values ranging from 1 to N on 0 background

Tools:
  NIFTI_Label2Masks:  converts a Label file to several Masks files
  NIFTI_CombineMasks: combines several Mask files into a single Mask file
  NIFTI_Masks2Label:  converts several Mask files to a Label file

You may test these tools with the data kindly provided by the 
Laboratory for Rehabilitation Neuroscience at the University of Florida 
available at http://lrnlab.org/

This software is intended to be used in FSL (https://fsl.fmrib.ox.ac.uk/fsl/fslwiki).
In order to be able to execute the tools in the Python environment provided by FSL 
please install the NumPy, SciPy and NiBabel libaries with the command 
"sudo /usr/local/fsl/fslpython/bin/pip install numpy scipy nibabel"
inside the FSL Virtual machine (tested on FSL 6.0.3)

If you have installed FSL in a non default home directory, 
or intend to use these tools in a different python environment,
please edit the first line of the Python files to reflect the correct
location of your Python interpreter
  
  
