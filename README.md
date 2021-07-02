# RapID-cell-counter
PyQT graphical interface for high-throughput cell counting for research

## New for PyQt5 version

### Installing instruction

#### [Dowload Ananconda](https://www.anaconda.com/products/individual) if not done before
#### Dowload and unzip the RapID-cell-counter manually: click the green button writen `code` and then click `download zip` in the dropdown options (or use git clone if experienced)

#### Open terminal (via Anaconda Navigator -> CMD.exe Prompt or via Command Prompt)
##### In Windows press the windows key and type Ananconda Navigator to and click on the Anaconda Navigator desktop app
##### In Linux the terminal can be open directly via CRTL+ALT+T
##### In Mac to open the terminal directly click the Launchpad icon in the Dock, type Terminal in the search field, then click Terminal. Otherwise, click the Launchpad icon in the Dock, type Anaconda Navigator in the search field, then click then click Anaconda Navigator to open the desktop app if prefered.

![screenshot](https://github.com/sanchestm/RapID-cell-counter/blob/master/images/navigator.png)

#### In the terminal copy-paste and press enter for the following code (one line at a time)

```
conda create --name RapID shapely pandas pyqt scikit-image
conda activate RapID
```

![screenshot](https://github.com/sanchestm/RapID-cell-counter/blob/master/images/create_env2.png)
![screenshot](https://github.com/sanchestm/RapID-cell-counter/blob/master/images/activating_conda_environment.png)

Once we activated the conda environment (which contains all the necessary packages to run the code) we can locate the file (the directory where we downloaded and unzipped the package) and enter the directory to be able to run the program.

As an example if we unzipped our file in the Downloads directory we can open this directory using the `cd` Command.

```
cd Downloads\RapID-cell-counter-master
```

In Linux and Mac, the dashes are `/` while in windows we use `\`

![screenshot](https://github.com/sanchestm/RapID-cell-counter/blob/master/images/opening_folder.png)

### Run program
#### Fist check if the right conda environment is open, in parenthesis in the terminal and that you're in the right directory (check it in your file system)

```
python mainQT5.py
```

![screenshot](https://github.com/sanchestm/RapID-cell-counter/blob/master/images/running_program.png)

### Rerunning the program

To rerun the program once we closed it, we only have to reopen the Conda terminal. Activate the RapID environment. Use the `cd` to navigate to the directory of the mainQT5.py file and the execute it using `python mainQT5.py`

![screenshot](https://github.com/sanchestm/RapID-cell-counter/blob/master/images/rerun.png)

## For PyQt4 version
### Installing instructions
For this program, first you'll need to have Conda installed in your computer.
this program runs on python 3.5 so we'll create an environment and then install the necessary packages. This will take around 15 min.
