# RapID-cell-counter
PyQT graphical interface for high-throughput cell counting for research

## New for PyQt5 version

### Installing instruction

#### Dowload Ananconda if not done before
#### Dowload and unzip the RapID-cell-counter manually or use git clone

Open Conda terminal (via Anaconda Navigator -> CMD.exe Prompt or via Command Prompt or via Ctrl+alt+t (linux))
```
conda create --name RapID shapely pandas pyqt scikit-image
conda activate RapID
```

![screenshot](https://github.com/sanchestm/mitotic-index-calc/blob/master/images/activating_conda_environment.png)

Once we activated the conda environment (which contains all the necessary packages to run the code) we can locate the file (the directory where we downloaded and unzipped the package) and enter the directory to be able to run the program.

As an example if we unzipped our file in the Dowloads directory we can open this directory using the 'cd' Command.

```
cd Downloads\RapID-cell-counter-master
```

In Linux and Mac, the dashes are `/` while in windows we use `\`

![screenshot](https://github.com/sanchestm/mitotic-index-calc/blob/master/images/opening_folder.png)

### Run program
#### Fist check if the right conda environment is open, in parenthesis in the terminal and that you're in the right directory (check it in your file system)

```
python mainQT5.py
```

![screenshot](https://github.com/sanchestm/mitotic-index-calc/blob/master/images/running_program.png)

### Rerunning the program

To rerun the program once we closed it, we only have to reopen the Conda terminal. Activate the RapID environment. Use the `cd` to navigate to the directory of the mainQT5.py file and the execute it using `python mainQT5.py`


## For PyQt4 version
### Installing instructions
For this program, first you'll need to have Conda installed in your computer.
this program runs on python 3.5 so we'll create an environment and then install the necessary packages. This will take around 15 min.


#### creating a new Python 3.5  environment and activating it
```
conda create -n celCountPaper python=3.5
conda activate celCountPaper
```

#### install missing packages
```
conda install matplotlib shapely pandas
conda install -c anaconda pyqt=4.11 scikit-image
```
### run program
```
Dowloads/RapID-cell-counter-master/python main.py
```

### features can be seen on video_tutorial.mov
