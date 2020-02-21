# Experiment Folder Structure GUI
This is a GUI built in python using tkinter to automate building a file folder struture.
Creating a new folder structure every time a new experiment is started is a process that can easily be automated. This is a perfect Python automation problem to solve. This project will be used to create a new folder structure for any new experiment. 
The experiment top level folder will have the name:

\<date_created\> - \<descriptive_experiment_name_Mark_XX\>.
 
The children folders can be:
 1. data - Raw data files are kept and referenced from. Cleaned data files can be kept here as well.
 2. images - Images, schematics, photos relevant to the experiment go here. Sub folders are:
      * PNG
      * JPG
      * SVG
      * NEF
 3. notebook - This is where the JupyterLab notbook will go
 4. plots - Relevant plots from data munging are saved to this folder
 5. videos - this is where video data will go
 
 What folders get generated, depends on selection from the folder tab of GUI.

## Getting Started
you will need the following:
1. python 3.7.x or later
2. 