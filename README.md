# RapID-cell-counter
PyQT graphical interface for high throuput cell counting for research

## Installing instructions
For this program, first you'll need to have Conda installed in your computer.
this program runs on python 3.5 so we'll create an environment and then install the necessary packages. This will take around 15 min.

### creating a new Python 3.5  environment and activating it
conda create -n celCountPaper python=3.5
conda activate celCountPaper

### install missing packages
conda install matplotlib shapely pandas 
conda install -c anaconda pyqt=4.11 scikit-image 

### run program 
'folder with pictures'/python main.py



