# RapID-cell-counter
PyQT graphical interface for high-throughput cell counting for research

## New for PyQt5 version

### Installing instruction

1. **Download Anaconda and RapID source code**
    1. [Dowload Ananconda](https://www.anaconda.com/products/individual) if not done before
    2. Dowload and unzip the RapID-cell-counter manually: click the green button writen `code` (at the top center of this page) and then click `download zip` in the dropdown options (or use git clone if experienced)
2. **Open terminal**
    1. **In Windows** open Ananconda Navigator desktop app then click on CMD.exe Prompt
<details>
<summary>screenshot  </summary>
![screenshot](https://github.com/sanchestm/RapID-cell-counter/blob/master/images/navigator.png)
</details>

    2. **In Linux** the terminal can be open directly via CRTL+ALT+T
    3. **In Mac:** open terminal by searching `terminal` in Spotlight (or Finder). Open the terminal by clicking the terminal app
3. In the terminal copy-paste and press enter for the following code
    1. `conda create --name RapID -y shapely pandas pyqt scikit-image`

<details>
<summary> screenshot </summary>
![screenshot](https://github.com/sanchestm/RapID-cell-counter/blob/master/images/create_env2.png)
</details>

### Run program

<details>
  <summary>
 <b>
  <big>
   For Windows  
   </big>
   </b>
  </summary>

1. **Open terminal**
2. In the terminal, activate conda environment copy-paste and press enter for the following code
```
conda activate RapID
```
![screenshot](https://github.com/sanchestm/RapID-cell-counter/blob/master/images/activating_conda_environment.png)

3. Once we activated the conda environment (which contains all the necessary packages to run the code) we can locate the file (the directory where we downloaded and unzipped the package) and enter the directory to be able to run the program. As an example if we unzipped our file in the Downloads directory we can open this directory using the `cd` Command. In Linux and Mac, the dashes are `/` while in windows we use `\`
```
cd Downloads\RapID-cell-counter-master
```

<details>
  <summary>Code version for Linux and Mac </summary>

    cd Downloads/RapID-cell-counter-master

</details>


![screenshot](https://github.com/sanchestm/RapID-cell-counter/blob/master/images/opening_folder.png)

4. Start the software by typing the following code into the terminal and pressing enter
```
python mainQT5.py
```

![screenshot](https://github.com/sanchestm/RapID-cell-counter/blob/master/images/running_program.png)

### Rerunning the program

To rerun the program once we closed it, we only have to reopen the terminal. Activate the RapID environment. Use the `cd` to navigate to the directory of the mainQT5.py file and the execute it using `python mainQT5.py`. Or run the following lines if the RapID source code is in Downloads:
```
conda activate RapID
cd Downloads\RapID-cell-counter-master
python mainQT5.py
```


![screenshot](https://github.com/sanchestm/RapID-cell-counter/blob/master/images/rerun.png)

</details>

<details>
  <summary>
 <b>
  <big>
   For Linux and Mac
    </big>
    </b>
  </summary>


1. **Open terminal**
2. In the terminal, activate conda environment copy-paste and press enter for the following code
```
conda activate RapID
```
![screenshot](https://github.com/sanchestm/RapID-cell-counter/blob/master/images/activating_conda_environment.png)

3. Once we activated the conda environment (which contains all the necessary packages to run the code) we can locate the file (the directory where we downloaded and unzipped the package) and enter the directory to be able to run the program. As an example if we unzipped our file in the Downloads directory we can open this directory using the `cd` Command. In Linux and Mac, the dashes are `/` while in windows we use `\`
```
cd Downloads/RapID-cell-counter-master
```

![screenshot](https://github.com/sanchestm/RapID-cell-counter/blob/master/images/opening_folder.png)

4. Start the software by typing the following code into the terminal and pressing enter
```
python mainQT5.py
```

![screenshot](https://github.com/sanchestm/RapID-cell-counter/blob/master/images/running_program.png)

### Rerunning the program

To rerun the program once we closed it, we only have to reopen the terminal. Activate the RapID environment. Use the `cd` to navigate to the directory of the mainQT5.py file and the execute it using `python mainQT5.py`. Or run the following lines if the RapID source code is in Downloads:
```
conda activate RapID
cd Downloads/RapID-cell-counter-master
python mainQT5.py
```

![screenshot](https://github.com/sanchestm/RapID-cell-counter/blob/master/images/rerun.png)
</details>
