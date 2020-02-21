#!/usr/bin/env python
# coding: utf-8

# Creating a new folder structure every time a new experiment is started is a process that can easily be automated. This is a perfect Python automation problem to solve. This notebook will be used to create a new folder structure for a new experiment. 
# 
# The experiment top level folder will have the name:
# 
# \<date_created\> - \<descriptive_experiment_name_Mark_XX\>.
# 
# The children folders can be:
# 1. data - Raw data files are kept and referenced from. Cleaned data files can be kept here as well.
# 2. images - Images, schematics, photos relevant to the experiment go here. Sub folders are:
#      * PNG
#      * JPG
#      * SVG
#      * NEF
#      
# 3. notebook - This is where the JupyterLab notbook will go
# 4. plots - Relevant plots from data munging are saved to this folder
# 5. videos - this is where video data will go
# 
# What folders get generated, depends on selection from the folder tab of GUI.

# In[ ]:


# import liberaries 
import os
import tkinter as tk
import shutil
import subprocess

from datetime import datetime
from pathlib import Path
from PIL import ImageTk, Image
from tkinter import ttk
from tkcalendar import Calendar, DateEntry
from tkinter.filedialog import askdirectory
from ttkwidgets.frames import Balloon
# from ttkthemes import ThemedTk


#define custom functions
# def save_main_folder():
#     return master_folder.get()

def ask_main_folder():
    '''Function sets main folder path'''
    path = askdirectory(parent=root,
                             initialdir = master_folder.get(),
                             title='Select Plot Folder')
    master_folder.set(path)

def save_date(d):
    ''' formats and updates the selected date as a string. '''
    ''' d is place holder for auto update code to work. '''
    date_string.set(cal.get_date().strftime("%Y-%m-%d"))
    kernal_name.set(''.join([date_string.get(), ' - ', experiment_name.get().replace(' ', '_')]))

def save_exp_name(n):
    ''' formats and updates the selected name as a string. '''
    ''' n is place holder for auto update code to work. '''
    experiment_name.set(experiment_name.get().replace(' ', '_'))
    kernal_name.set(''.join([date_string.get(), ' - ', experiment_name.get().replace(' ', '_')]))

def create_folders():
    ''' function to create folder structure'''
    path_master = Path(master_folder.get())
    exp_kernal = ''.join([date_string.get(), ' - ', experiment_name.get().replace(' ', '_')])
    folder = Path.joinpath(path_master,exp_kernal)
    try:
        Path.mkdir(Path.joinpath(path_master,exp_kernal))
        subprocess.Popen(f'explorer /select,{folder}\\')
    except FileExistsError: 
        print(f'Folder exists. Showing location...')
        subprocess.Popen(f'explorer /select,{folder}\\')
    except:
        print('Something went wrong.')
    
    make_folder_lists()
    
    for folder in list_folder_main:
        try:
            Path.mkdir(Path.joinpath(path_master,exp_kernal,folder))
        except FileExistsError: 
            print(f'Folder exists.')
        except:
            print('Something went wrong.')
        
    for folder in list_folder_image_fmt:
        try:
            Path.mkdir(Path.joinpath(path_master,exp_kernal,'images',folder))
        except FileExistsError: 
            print(f'Folder exists.')
        except:
            print('Something went wrong.')
    # make note files as appropriate
    if CV_file_note.get() == 1:
        create_note_file()
    if CV_file_video.get() ==1:
        copy_file_to_folder('video_scripts.txt', 'videos')
    if CV_file_notebook.get() ==1:
        copy_file_to_folder('_notebook.ipynb', 'notebooks')
        rename_file('_notebook.ipynb', 'notebooks')
    if CV_file_python.get() ==1:
        copy_file_to_folder('_py_script.py', 'notebooks')
        rename_file('_py_script.py', 'notebooks')
    if CV_file_contact_angle.get() ==1:
        copy_file_to_folder('optical_contact_angle_template.xlsx', 'notebooks')
    if CV_file_pressure_transducer.get() ==1:
        copy_file_to_folder('pressure_transducer_unit_conversion.xlsx', 'notebooks')    
    if CV_file_exp_setup.get() ==1:
        copy_file_to_folder('_exp_setup.svg', 'images/SVG')
        rename_file('_exp_setup.svg', 'images/SVG')    
    if CV_file_video.get() ==1:
        copy_file_to_folder('concatenate.bat', 'videos')      
    
def make_folder_lists():
    '''function returns lists of folders to create based on checkboxes'''
    # initialize lists
    global list_folder_main
    global list_folder_image_fmt
    list_folder_main = [ ]
    list_folder_image_fmt = [ ]
    
    # main folders
    if CV_data.get() == 1:
        list_folder_main.append('data')
    if CV_images.get() == 1:
        list_folder_main.append('images')
    if CV_notebooks.get() == 1:
        list_folder_main.append('notebooks')
    if CV_plots.get() == 1:
        list_folder_main.append('plots')
    if CV_videos.get() == 1:
        list_folder_main.append('videos')
    if CV_custom0.get() ==1:
        list_folder_main.append(name_folder_custom_0.get())
    if CV_custom1.get() ==1:
        list_folder_main.append(name_folder_custom_1.get())
    if CV_custom2.get() ==1:
        list_folder_main.append(name_folder_custom_2.get())

    # image format folders
    if CV_images.get() == 1:
        if CV_JPG.get() == 1:
            list_folder_image_fmt.append('JPG')
        if CV_NEF.get() == 1:
            list_folder_image_fmt.append('NEF')
        if CV_PNG.get() == 1:
            list_folder_image_fmt.append('PNG')
        if CV_SVG.get() == 1:
            list_folder_image_fmt.append('SVG')      
        
def create_note_file():
    path_master = Path(master_folder.get())
    exp_kernal = ''.join([date_string.get(), ' - ', experiment_name.get().replace(' ', '_')])
    file_folder = Path.joinpath(path_master,exp_kernal)
    file_ext = '.txt'
    file_name = ''.join([str(file_folder), '\\', exp_kernal, '_notes', file_ext])
    file = open(f'{file_name}', 'w')
    file.write(f'This is a note file for {exp_kernal}\nDate\t\tTime\t\tNotes\n{date_string.get()}\t\t\tFile Created')
    file.close()
    
def copy_file_to_folder(file, folder):
    local_file_name = file

    local_file_location = Path(r'.\files')
    local_file = Path.joinpath(local_file_location, local_file_name)

    path_master = Path(master_folder.get())
    exp_kernal = ''.join([date_string.get(), ' - ', experiment_name.get().replace(' ', '_')])
    file_folder = Path.joinpath(path_master,exp_kernal, folder)
    shutil.copy2(local_file, file_folder)

def rename_file(file, folder):
    og_file_name = file
    path_master = Path(master_folder.get())
    exp_kernal = ''.join([date_string.get(), ' - ', experiment_name.get().replace(' ', '_')])
    new_file_name = ''.join([exp_kernal, og_file_name])
    file_folder = Path.joinpath(path_master,exp_kernal, folder)
    og_file = Path.joinpath(file_folder, og_file_name)
    new_file = Path.joinpath(file_folder, new_file_name)
    os.rename(og_file, new_file)    

# define constants
HEIGHT = 420
WIDTH = 520
LOCX = 100
LOCY = 50

# start GUI definition

root = tk.Tk()

# style the GUI
s = ttk.Style(root)
s.theme_use('xpnative')
s.theme_settings("xpnative", {"TNotebook.Tab": {"configure": {"padding": [3, 3]}}})

# title the GUI window
root.title('    Build Experiment Folder Structure')
# change the icon for the GUI window
root.iconbitmap(r'./images/icon_Accion_A_BLK.ico')
root.geometry(f'{WIDTH}x{HEIGHT}+{LOCX}+{LOCY}') # width x height
root.resizable(False, False)

# Declaration of Tkinter variables

# name tab variables
master_folder = tk.StringVar()
date_string = tk.StringVar()
experiment_name = tk.StringVar()
kernal_name = tk.StringVar()

# folder tab variables

# experiment layer folder variables
CV_data = tk.IntVar()
CV_images = tk.IntVar()
CV_notebooks = tk.IntVar()
CV_plots = tk.IntVar()
CV_videos = tk.IntVar()

# image layer folder  variables
CV_JPG = tk.IntVar()
CV_NEF = tk.IntVar()
CV_PNG = tk.IntVar()
CV_SVG = tk.IntVar()

# experiment layer custom folder variables
CV_custom0 = tk.IntVar()
CV_custom1 = tk.IntVar()
CV_custom2 = tk.IntVar()
name_folder_custom_0 = tk.StringVar()
name_folder_custom_1 = tk.StringVar()
name_folder_custom_2 = tk.StringVar()

# files tab variables
CV_file_note = tk.IntVar()
CV_file_video = tk.IntVar()
CV_file_notebook = tk.IntVar()
CV_file_python = tk.IntVar()
CV_file_contact_angle = tk.IntVar()
CV_file_pressure_transducer = tk.IntVar()
CV_file_exp_setup = tk.IntVar()
CV_file_concat_video = tk.IntVar()




# Initialization of Tkinter variables 
master_folder.set(r''.join([os.environ['USERPROFILE'],r'\Documents\01 - Local Work\00 - Titan\experiments']))
date_string.set(datetime.today().strftime('%Y-%m-%d'))
experiment_name.set('Enter name')
kernal_name.set(''.join([date_string.get(), ' - ', experiment_name.get().replace(' ', '_')]))

name_folder_custom_0.set('literature')
name_folder_custom_1.set('misc')
name_folder_custom_2.set('zzz_obsolete')

# tool tip text
tip_text_change_folder = 'Click to open file explorer box to select parent folder.'
tip_text_create_structure = 'Click to create the experiment folder structure. Selected folders in the Folders tab will be created. Selected files in the Files tab will be created.'
tip_text_exit = 'Click to exit GUI.'
tip_text_date_select = 'Click to open calander to select experiment date.'
tip_text_name_enter = 'Please enter a descriptive experiment name. Spaces will be replaced with \'_\'.'
tip_text_header = 'Hidden Guidance'

# create a containter for notebook
frame1 = ttk.Frame(root)
frame1.place(relx=0.03, rely=0.05, relwidth=0.9, relheight=0.7)

# create a containter for buttons
frame2 = ttk.Frame(root)
frame2.place(relx=0.03, rely=0.8, relwidth=0.9, relheight=0.2)

# create a notebook with a few tabs
# nb = ttk.Notebook(frame1, width=WIDTH, height=HEIGHT)
nb = ttk.Notebook(frame1)


# the first tab is for kernal name creating
tab_name = ttk.Frame(nb)
nb.add(tab_name, text='Name')

# the advanced tab is for customizing the folders
tab_folders = ttk.Frame(nb)
nb.add(tab_folders, text='Folders')

# the files tab is for customizing the files
tab_files = ttk.Frame(nb)
nb.add(tab_files, text='Files')

# put notebook on screen
nb.pack(expand=True, fill=tk.BOTH)

#
########################################################################
# Name Tab
########################################################################
#
frame_parent_folder = ttk.Frame(tab_name)
frame_parent_folder.place(relx=0, rely=0.0, relwidth=1.0, relheight=0.43)
#
frame_kernal_name = ttk.Frame(tab_name)
frame_kernal_name.place(relx=0.0, rely=0.43, relwidth=1.0, relheight=0.58)
#
#  top frame
#
# create and place tab description
label_tab_loc_text = 'Experiment files and folders will be created under the following parrent directory:'
label_tab_loc = tk.Message(frame_parent_folder, text=label_tab_loc_text, width=400)
label_tab_loc.grid(row=0, column=0, padx=5, pady=5, sticky='W', columnspan=100) 

label_folder = ttk.Label(frame_parent_folder, text='Parent folder:')
label_folder.grid(row=1, column=1, padx=5, pady=5, sticky='WN')               

# create and place current folder
label_folder_current = tk.Message(frame_parent_folder, textvariable=master_folder, width=260)
label_folder_current.grid(row=1, column=2, padx=5, pady=5)                 

# create and place change folder button
button_change_folder = ttk.Button(frame_parent_folder, text='Change folder', command=ask_main_folder)
button_change_folder.grid(row=1, column=3, padx=5, pady=5, sticky='NE') 
# add tool tip for button
Balloon(button_change_folder, headertext=tip_text_header, text=tip_text_change_folder, background=None, image=None)

# horizontal line separator for looks only
ttk.Separator(frame_kernal_name, orient='horizontal').place(relx=0.0, rely=0.0, relwidth=1.0)

#
#  bottom frame
#
# create and place tab description
label_tab_name_text = 'Experiment kernal name is created using the following fields:'
label_tab_name = tk.Message(frame_kernal_name, text=label_tab_name_text, width=400)
label_tab_name.grid(row=3, column=0, padx=5, pady=5, sticky='NW', columnspan=100) 

# create and place date label
# label_space.grid(row=4, column=0, sticky='W')
label_date = ttk.Label(frame_kernal_name, text='Experiment date:')
label_date.grid(row=4, column=1, padx=10, pady=10, sticky='E')

# create, place, and update date selector
cal = DateEntry(frame_kernal_name, date_pattern='y-mm-dd', width=12, borderwidth=2)
cal.grid(row=4, column=2, padx=5, pady=5, sticky='W')
cal.bind("<<DateEntrySelected>>", save_date)  # update date everytime a day is selected on calendar.
# add tool tip for button
Balloon(cal, headertext=tip_text_header, text=tip_text_create_structure, background=None, image=None)

# create and place name label
# label_space.grid(row=5, column=0, sticky='W')
label_name = ttk.Label(frame_kernal_name, text='Experiment name:')
label_name.grid(row=5, column=1, padx=10, pady=10, sticky='E')

# create and place name entry widget
exp_name_entry = ttk.Entry(frame_kernal_name, textvariable=experiment_name, width=40)
exp_name_entry.grid(row=5, column=2, padx=5, pady=5, sticky='W')
# update the name when Retrun is pressed
exp_name_entry.bind("<KeyPress-Return>", save_exp_name)
# add tool tip for button
Balloon(exp_name_entry, headertext=tip_text_header, text=tip_text_name_enter, background=None, image=None)

# create and place name label
# label_space.grid(row=6, column=0, sticky='W')
label_kernal1 = ttk.Label(frame_kernal_name, text='Kernal name:')
label_kernal1.grid(row=6, column=1, padx=10, pady=10, sticky='E')
# This label will update when the kernal name changes
label_kernal2 = ttk.Label(frame_kernal_name, textvariable=kernal_name)
label_kernal2.grid(row=6, column=2, padx=5, pady=5, sticky='W', columnspan=100)

#
#
########################################################################
# Folders Tab
########################################################################
#
# Divide tab into two columns using frames
frame_folders_title = tk.Frame(tab_folders)
frame_folders_title.place(relx=0, rely=0, relwidth=1.0, relheight=0.1)
#
frame_folders_main = tk.Frame(tab_folders)
frame_folders_main.place(relx=0, rely=0.1, relwidth=0.5, relheight=1.0)
#
frame_folders_custom = tk.Frame(tab_folders)
frame_folders_custom.place(relx=0.5, rely=0.1, relwidth=0.5, relheight=1.0)

# create and place tab description
text_label_tab_folder = 'Select folders you want created automaticaly.'
label_tab_folder = ttk.Label(frame_folders_title, text=text_label_tab_folder, width=400)
label_tab_folder.grid(row=0, column=0, padx=5, pady=5, sticky='NW', columnspan=100)

# create and place section description
text_label_tab_folder_main = 'Main Folders'
label_tab_folder_main = ttk.Label(frame_folders_main, text=text_label_tab_folder_main, width=40)
label_tab_folder_main.grid(row=0, column=0, padx=5, pady=5, sticky='NW', columnspan=3)

# create and place section description
text_label_tab_folder_custom = 'Custom Folders'
label_tab_folder_custom = ttk.Label(frame_folders_custom, text=text_label_tab_folder_custom, width=40)
label_tab_folder_custom.grid(row=0, column=0, padx=5, pady=5, sticky='NW', columnspan=3)

#  create checkboxes
CF01 = tk.Checkbutton(frame_folders_main, text = "data", variable=CV_data)
CF02 = tk.Checkbutton(frame_folders_main, text = "images", variable=CV_images)
CF03 = tk.Checkbutton(frame_folders_main, text = "JPG", variable=CV_JPG)
CF04 = tk.Checkbutton(frame_folders_main, text = "NEF", variable=CV_NEF)
CF05 = tk.Checkbutton(frame_folders_main, text = "PNG", variable=CV_PNG)
CF06 = tk.Checkbutton(frame_folders_main, text = "SVG", variable=CV_SVG)
CF07 = tk.Checkbutton(frame_folders_main, text = "notebooks", variable=CV_notebooks)
CF08 = tk.Checkbutton(frame_folders_main, text = "plots", variable=CV_plots)
CF09 = tk.Checkbutton(frame_folders_main, text = "videos", variable=CV_videos)

entry_CV_custom0 = ttk.Entry(frame_folders_custom, textvariable=name_folder_custom_0, width=20)
CF10 = tk.Checkbutton(frame_folders_custom, variable=CV_custom0)

entry_CV_custom1 = ttk.Entry(frame_folders_custom, textvariable=name_folder_custom_1, width=20)
CF11 = tk.Checkbutton(frame_folders_custom, variable=CV_custom1)

entry_CV_custom2 = ttk.Entry(frame_folders_custom, textvariable=name_folder_custom_2, width=20)
CF12 = tk.Checkbutton(frame_folders_custom, variable=CV_custom2)

#  set default selection values
CF01.select()
CF02.select()
CF03.select()
CF04.select()
CF05.select()
CF06.select()
CF07.select()
CF08.select()
CF09.select()
CF10.deselect()
CF11.deselect()
CF12.deselect()

# place the check boxes for main folders
CF01.grid(row=1, column=0, sticky='W')
CF02.grid(row=2, column=0, sticky='W')
CF03.grid(row=2, column=1, sticky='W')
CF04.grid(row=3, column=1, sticky='W')
CF05.grid(row=4, column=1, sticky='W')
CF06.grid(row=5, column=1, sticky='W')
CF07.grid(row=6, column=0, sticky='W')
CF08.grid(row=7, column=0, sticky='W')
CF09.grid(row=8, column=0, sticky='W')

# vertical line separator for looks only
ttk.Separator(frame_folders_custom, orient='vertical').place(relx=0.0, rely=0.0, relheight=1.0)

# place the check boxes and entry fields for custom folders
CF10.grid(row=1, column=0, sticky='E')
entry_CV_custom0.grid(row=1, column=1, sticky='W')

CF11.grid(row=2, column=0, sticky='E')
entry_CV_custom1.grid(row=2, column=1, sticky='W')

CF12.grid(row=3, column=0, sticky='E')
entry_CV_custom2.grid(row=3, column=1, sticky='W')
#
########################################################################
# Files Tab
########################################################################
#
# Divide tab into thre columns using frames
frame_files_title = tk.Frame(tab_files)
frame_files_title.place(relx=0, rely=0, relwidth=1.0, relheight=0.13)
#
frame_files_column_0 = tk.Frame(tab_files)
frame_files_column_0.place(relx=0, rely=0.13, relwidth=0.333, relheight=1)
#
frame_files_column_1 = tk.Frame(tab_files)
frame_files_column_1.place(relx=0.333, rely=0.13, relwidth=0.333, relheight=1)
#
frame_files_column_2 = tk.Frame(tab_files)
frame_files_column_2.place(relx=0.666, rely=0.13, relwidth=0.333, relheight=1)
#
# create and place tab description
label_tab_files_text = 'Select files you want created automaticaly.'
label_tab_files = tk.Label(frame_files_title, text=label_tab_files_text)
 
#
label_tab_files_column_0_text = '*.txt note files'
label_tab_files_column_0 = tk.Label(frame_files_column_0, text=label_tab_files_column_0_text)
  
#
label_tab_files_column_1_text = 'Data management files'
label_tab_files_column_1 = tk.Label(frame_files_column_1, text=label_tab_files_column_1_text)

#
label_tab_files_column_2_text = 'Drawing files'
label_tab_files_column_2 = tk.Label(frame_files_column_2, text=label_tab_files_column_2_text)
 

# create checkboxes
C10 = tk.Checkbutton(frame_files_column_0, text = "_notes.txt", variable=CV_file_note)
C11 = tk.Checkbutton(frame_files_column_0, text = "video_scripts.txt", variable=CV_file_video)
C12 = tk.Checkbutton(frame_files_column_1, text = "_nb.ipynb Start", variable=CV_file_notebook)
C13 = tk.Checkbutton(frame_files_column_1, text = "_py.py start", variable=CV_file_python)
C14 = tk.Checkbutton(frame_files_column_1, text = "CA_template.xlsx", variable=CV_file_contact_angle)
C15 = tk.Checkbutton(frame_files_column_1, text = "PT_tempplate.xlsx", variable=CV_file_pressure_transducer)
C16 = tk.Checkbutton(frame_files_column_2, text = "_Exp_Setup.svg", variable=CV_file_exp_setup)
C17 = tk.Checkbutton(frame_files_column_2, text = "concatenate.bat", variable=CV_file_concat_video)

# set default conditions of checkbuttons
C10.select()
C11.select()
C12.select()
C13.deselect()
C14.deselect()
C15.deselect()
C16.select()
C17.select()

# place labels
label_tab_files.grid(row=0, column=0, padx=5, pady=5, sticky='NW') 
label_tab_files_column_0.grid(row=0, column=0, padx=5, pady=5)  
label_tab_files_column_1.grid(row=0, column=0, padx=5, pady=5)  
label_tab_files_column_2.grid(row=0, column=0, padx=5, pady=5) 
# place checkboxes
C10.grid(row=1, column=0, sticky='W')
C11.grid(row=2, column=0, sticky='W')
C12.grid(row=1, column=0, sticky='W')
C13.grid(row=2, column=0, sticky='W')
C14.grid(row=3, column=0, sticky='W')
C15.grid(row=4, column=0, sticky='W')
C16.grid(row=1, column=0, sticky='W')
C17.grid(row=2, column=0, sticky='W')


#
########################################################################
# Buttons
########################################################################
#
# create and place create button
button_create_folders = ttk.Button(frame2, text='Create Structure', command=create_folders)
button_create_folders.grid(row=100, column=0, sticky='W')
# add tool tip for button
Balloon(button_create_folders, headertext=tip_text_header, text=tip_text_create_structure, background=None, image=None)

# create and place a quit button.
button_quit = ttk.Button(frame2, text='Exit', command=root.destroy)
button_quit.grid(row=101, column=0, sticky='W')
# add tool tip for button
Balloon(button_quit, headertext=tip_text_header, text=tip_text_exit, background=None, image=None)

########################################################################
# Run GUI loop
########################################################################
#
root.mainloop()