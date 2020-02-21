import datetime as dt
import gc
import matplotlib.colorbar as cbar
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines

import numpy as np
import os
import pandas as pd
import tkinter as tk
import time

from matplotlib import cm
from nptdms import TdmsFile
from pathlib import Path
from scipy import stats
from scipy.optimize import curve_fit
from scipy.signal import savgol_filter
from tkinter.filedialog import askopenfilename, askdirectory, askopenfilenames

# Define constants
GOLDEN_RATIO = (1 + 5 ** 0.5) / 2

# user defined functions
def get_data_file():
    """Use tkinter to open a file dialog box and allow user selection of """
    """data files. Returns the path of the file."""
    root = tk.Tk()
    file_path = askopenfilename(parent=root,
                                initialdir = r'./', 
                                title = "Select a data file to open ...", 
                                filetypes = (("text files", "*.txt"), ("CSV files", "*.csv"), ("All files", "*.*"))
                                ) # show an "Open" dialog box and return the path to the selected file
    root.quit()
    root.destroy()
    print(''.join([file_path,' selected.']))
    gc.collect()
    return(file_path)

def get_tdms_files():
    """Use tkinter to open a file dialog box and allow user selection of """
    """multiple files. Put files in a list and returns list."""
    root = tk.Tk()
    filez = askopenfilenames(parent=root, 
                             initialdir = r'./', 
#                              filetypes = ('TDMS files', '*.tdms'), 
                             title='Select tdms data files to append to list.'
                            )
    root.quit()
    root.destroy()
    filez = list(filez)
    if len(filez) < 2:
        print(f'The following {len(filez)} file is selected:')
    else:
        print(f'The following {len(filez)} files are selected:')
    for file in filez:
        print(file)
    return(filez) 

def initialize_pressure_transducer(Ilow = 4E-3, Ihigh = 20E-3, Plow = -14.7, Phigh = 45):
    """Initialize the pressure transducer and return values to convert raw data to pressure in psi"""
    """Default values: Ilow = 4E-3, Ihigh = 20E-3, Plow = -14.7, Phigh = 15, R1 = 487.2, R2 = 488.6"""
    # Place ranges into array for easy manipulation for linear model
    Iarray = np.asarray([Ilow, Ihigh])
    Parray = np.asarray([Plow, Phigh])
    # Assume linear fit between the range and calculate the slope and intercept
    LinearModel = stats.linregress(Iarray, Parray)
    slope = LinearModel[0]
    intercept = LinearModel[1]
    print('Pressure transducer initialized:\n        I_lo:\t{0:0.3f} Amps\n        I_hi:\t{1:0.3f} Amps\n        P_lo:\t{2:0.1f} psi\n        P_hi:\t{3:0.1f} psi\n          '.format(Ilow, Ihigh, Plow, Phigh))
    return slope, intercept

                             
def set_plot_folder():
    """
    Function uses tkinter to promt user to set the plot folder. 
    Printes and returns the selected folder as a path.
    """
    root = tk.Tk()
    path = Path(askdirectory(parent=root,
                             initialdir = r'./',
                             title='Select Plot Folder'))
    root.quit()
    root.destroy()
    print('Plot folder: ', path)
    gc.collect()
    return(path)

def psi_to_Pa(pressure):
    """
    Function returns a presure given in psi to Pa. 
    """
    return pressure * 6894.76

def Pa_to_psi(pressure):
    """
    Function returns a presure given in psi to Pa. 
    """
    return pressure / 6894.76

def K_to_C(temp):
    """Returns a temperature in degrees Celcius given in Kelvin"""
    return temp-272.15

def C_to_K(temp):
    """Returns a temperature in Kelvin given in degrees Celcius"""
    return temp + 272.15

def mmmps_to_mlps(flowrate):
    """Returns a flowrate in ml/s given in m^3/s"""
    return flowrate * 1e6

def mmm_to_ml(volume):
    """Returns a volume in mL given in m^3"""
    return volume * 1e6

def ml_to_mmm(volume):
    """Returns a volume in m^3 given in mL"""
    return volume * 1e-6

def mu_temp_fit(x, a, b, c):
    '''The form of the function that fits viscosity vs temperature data.'''
    return(a * x**b + c)
    
def rho_temp_fit(x, a, b):
    '''The form of the function that fits density vs temperature data.'''
    return(a * x  + b)

def sigma_temp_fit(x, a, b):
    '''The form of the function that fits surface tension vs temperature data.'''
    return(a * x  + b)   
    
def viscosity_temp(temp):
    '''Returns the viscosity (kg/m/s) given a temp (K).'''
    mu_popt_F = np.array([ 5.58586277e+32, -1.38434792e+01,  6.56440863e-03]) 
    mu = mu_temp_fit(temp, *mu_popt_F)
    return mu

def density_temp(temp):
    '''Returns the density (kg/m^3) given a temp (K).'''
    rho_popt_F = np.array([-7.92013082e-01,  1.51830091e+03])
    rho = rho_temp_fit(temp, * rho_popt_F)
    return rho

def surface_tension_temp(temp):
    '''Returns the surface tension (kg/s^2) given a temp (K).'''
    sigma_popt_F = np.array([-6.49547701e-05,  7.34300172e-02])
    sigma = sigma_temp_fit(temp, *sigma_popt_F)
    return sigma

def sum_R_h_lines(temp, L_lines, R_lines):
    '''sums the hydraulic resistance of n lines at temp T in K'''
    R_h_lines = []
    mu = viscosity_temp(temp)
    for line in range(len(L_lines)):
        R_h_lines.append( 8 * mu * L_lines[line] / np.pi / R_lines[line]**4)
    return np.array(R_h_lines).sum()

def R_h_model(temp, N_valve, L_lines, R_lines):
    '''sums and returns the hydraulic resistance of lines and N LFN valves'''
    beta = 6.83e-13    # Units: ?
    mu = viscosity_temp(temp)
    R_h_LFN = N_valve * beta * mu
    R_h_lines = sum_R_h_lines(temp, L_lines, R_lines)
    R_h_total = R_h_LFN + R_h_lines
    return R_h_total

def sum_volume_lines(L_lines, R_lines):
    '''sums the volume of n lines'''
    volume_lines = []
    for line in range(len(L_lines)):
        volume_lines.append(L_lines[line] * np.pi * R_lines[line]**2)
    return np.array(volume_lines).sum()


# # Plot folder
# Select a folder to place saved plots. Having them in a central location is convient when pulling them into reports.

# In[2]:


# Defile the Plot Folder location and file type
# plot_folder = set_plot_folder()
plot_folder = Path(r'..\plots')
plot_format = 'png'


# # Temperature Limits
# This is where you set the temperature limits for the operational temperature range and the survivable temperature range. The units for temperature are Kelvin.

# In[3]:


temp_op_low = C_to_K(15)
temp_op_high = C_to_K(49)
temp_survive_low = C_to_K(-40)
temp_survive_high = C_to_K(100)
temp_room = 294.817


# # Fluid Properties
# Critical fluid properties and their dependance on temperature are detailed below. Changes in viscosity impact flow rates the most. The density and surface tension are needed to check Reynolds numbers and Webber numbers.

# ## Viscosity

# In[4]:


mu_data_file = Path(r'../data/MaterialProperties_EMIBF4_Viscosity.csv')
mu_df = pd.read_csv(mu_data_file, sep=',').dropna()

temp_fit = np.arange(temp_survive_low, temp_survive_high, 1)

mu_high = viscosity_temp(temp_op_high)
mu_low = viscosity_temp(temp_op_low)
mu_range = mu_high-mu_low

experiment_id = 'EMIBF4_viscosity_temp_fit_C'
plt.figure(1, figsize = [6, 2*GOLDEN_RATIO], dpi=100)

plt.plot(K_to_C(mu_df['temp_K']), mu_df['mu_kg/m/s'], 'ko', label=r'data')
plt.plot(K_to_C(temp_fit), viscosity_temp(temp_fit), 'k--', label=r'fit')
plt.fill_between([K_to_C(temp_op_low), K_to_C(temp_op_high)],[.2,.2], alpha=0.3, label='operating')
plt.fill_between([K_to_C(temp_survive_low), K_to_C(temp_op_low)],[.2,.2], alpha=0.3, label='survivable', color='orange')
plt.fill_between([K_to_C(temp_op_high), K_to_C(temp_survive_high)],[.2,.2], alpha=0.3, color = 'orange')
plt.annotate("",
            xy=(-15, mu_high), xycoords='data',
            xytext=(-15, mu_low), textcoords='data',
            arrowprops=dict(arrowstyle="<->",
                            ),
            )
plt.text(-20, mu_high-(mu_range/2), f'$\Delta \mu$={mu_range:0.2f} kg/(m s)',
        horizontalalignment='center',
         verticalalignment='center',
         rotation='vertical',
        )

plt.ylabel(r'Viscosity, $\mu$ [$\textrm{kg} /(\textrm{m} \textrm{s})$]')
plt.legend(loc=1)
plt.xlabel('Temperature, $T$ [$^\circ C$]')
plt.ylim(0,.2)

# save plot
plot_path = plot_folder.joinpath(''.join(["Plot_", experiment_id, ".", plot_format]))
# plt.savefig(plot_path, dpi=600, bbox_inches='tight')
# plt.show()


# ## Density

# In[5]:


rho_data_file = Path(r'../data/MaterialProperties_EMIBF4_Density.csv')
rho_df = pd.read_csv(rho_data_file, sep=',').dropna()

rho_high = density_temp(temp_op_high)
rho_low = density_temp(temp_op_low)
rho_range = rho_high-rho_low

experiment_id = 'EMIBF4_density_temp_fit_C'
plt.figure(1, figsize = [6, 2*GOLDEN_RATIO], dpi=100)

plt.plot(K_to_C(rho_df['temp_K']), rho_df['rho_kg/m3'], 'ko', label=r'data')
plt.plot(K_to_C(temp_fit), density_temp(temp_fit), 'k--', label=r'fit')
plt.fill_between([K_to_C(temp_op_low), K_to_C(temp_op_high)],[1500,1500], alpha=0.3, label='operating')
plt.fill_between([K_to_C(temp_survive_low), K_to_C(temp_op_low)],[1500,1500], alpha=0.3, label='survivable', color='orange')
plt.fill_between([K_to_C(temp_op_high), K_to_C(temp_survive_high)],[1500,1500], alpha=0.3, color = 'orange')
plt.annotate("",
            xy=(-15, rho_high), xycoords='data',
            xytext=(-15, rho_low), textcoords='data',
            arrowprops=dict(arrowstyle="<->",
                            ),
            )
plt.text(-20, rho_high-(rho_range/2), f'$\Delta \rho$={rho_range:0.2f} kg/m$^3$',
        horizontalalignment='center',
         verticalalignment='center',
         rotation='vertical',
        )

plt.ylabel(r'Density, $\rho$ [$\textrm{kg} /\textrm{m}^3$]')
plt.legend(loc=1)
plt.xlabel('Temperature, $T$ [$^\circ C$]')
plt.ylim(1220,1330)

# save plot
plot_path = plot_folder.joinpath(''.join(["Plot_", experiment_id, ".", plot_format]))
# plt.savefig(plot_path, dpi=600, bbox_inches='tight')
plt.show()


# ## Surface Tension

# In[6]:


sigma_data_file = Path(r'../data/MaterialProperties_EMIBF4_SurfaceTension.csv')
sigma_df = pd.read_csv(sigma_data_file, sep=',').dropna()

sigma_high = surface_tension_temp(temp_op_high)
sigma_low = surface_tension_temp(temp_op_low)
sigma_range = sigma_high-sigma_low

experiment_id = 'EMIBF4_surface_tension_temp_fit_C'
plt.figure(1, figsize = [6, 2*GOLDEN_RATIO], dpi=100)

plt.plot(K_to_C(sigma_df['temp_K']), sigma_df['sigma_kg/s^2'], 'ko', label=r'data')
plt.plot(K_to_C(temp_fit), surface_tension_temp(temp_fit), 'k--', label=r'fit')
plt.fill_between([K_to_C(temp_op_low), K_to_C(temp_op_high)],[.06, .06], alpha=0.3, label='operating')
plt.fill_between([K_to_C(temp_survive_low), K_to_C(temp_op_low)],[.06, .06], alpha=0.3, label='survivable', color='orange')
plt.fill_between([K_to_C(temp_op_high), K_to_C(temp_survive_high)],[.06, .06], alpha=0.3, color = 'orange')
plt.annotate("",
            xy=(-15, sigma_high), xycoords='data',
            xytext=(-15, sigma_low), textcoords='data',
            arrowprops=dict(arrowstyle="<->",
                            ),
            )
plt.text(-20, sigma_high-(sigma_range/2), f'$\Delta \sigma$={sigma_range:0.3E} kg/s$^2$',
        horizontalalignment='center',
         verticalalignment='center',
         rotation='vertical',
        )

plt.ylabel(r'Surface Tension, $\sigma$ [$\textrm{kg} /\textrm{s}^2$]')
plt.legend(loc=1)
plt.xlabel('Temperature, $T$ [$^\circ C$]')
plt.ylim(0.048,0.058)

# save plot
plot_path = plot_folder.joinpath(''.join(["Plot_", experiment_id, ".", plot_format]))
# plt.savefig(plot_path, dpi=600, bbox_inches='tight')
plt.show()


# # The Accumulator Model
# 

# ## Spring Pressure and Maximum Flow Rates

# In[100]:


# make the plot
fig, ax1 = plt.subplots(1, figsize = [7, 2*GOLDEN_RATIO] , dpi=100)

# plot valve open time as a function of piston position over temperature range.
plt.plot(x_DTB*1000, Pa_to_psi(P_spring_DTB), 'k', label='DTB')
plt.plot(x_UTB*1000, Pa_to_psi(P_spring_UTB), 'k--', label='UTB')
plt.plot(fill_length_DTB*1e3, Pa_to_psi(P_fill_DTB), 'ro', label=f'Pmax DTB = {Pa_to_psi(P_fill_DTB):0.3f} psi')
plt.plot(fill_length_UTB*1e3, Pa_to_psi(P_fill_UTB), 'bo', label=f'Pmax UTB = {Pa_to_psi(P_fill_UTB):0.3f} psi')
plt.plot(fill_length_DTBPMD*1e3, Pa_to_psi(P_fill_DTBPMD), 'r*', label=f'Pmax DTBPMD = {Pa_to_psi(P_fill_DTBPMD):0.3f} psi')
plt.plot(fill_length_UTBPMD*1e3, Pa_to_psi(P_fill_UTBPMD), 'b*', label=f'Pmax UTBPMD = {Pa_to_psi(P_fill_UTBPMD):0.3f} psi')
# plt.axvline(fill_length_DTB*1000, color='red', label=f'DTB max pressure {Pa_to_psi(P_fill_DTB):0.3f} psi')
# plt.axvline(fill_length_UTB*1000, color='red', linestyle='--', label=f'UTB max pressure {Pa_to_psi(P_fill_UTB):0.3f} psi')
# plt.fill_between([0, fill_length*1000], [15, 15], \
#                  alpha=0.1, label=r'Filled Volume $\forall=${0:0.3f} mL'.format(mmm_to_ml(fill_volume)), \
#                  color='black', hatch='', linewidth=0.0, zorder=1)  
plt.legend()
plt.xlabel(r'Piston Position, $x$ [mm]')    
plt.ylabel(r'Pressure, $P_b$ [psi]')
# plt.title(f'Dose = {mmm_to_ml(dose):0.3f} ml, k = {keff:0.0f}, effenciency = {mech_eff:0.2f}')
ax1.set_xlim(0, max(x_DTB.max()*1000, x_UTB.max()*1000))
ax1.set_ylim(0, 30)

# add volume scale to the bottom of the plot
ax3 = ax1.twiny()
ax3.xaxis.set_ticks_position('bottom')
ax3.xaxis.set_label_position('bottom')
ax3.spines['bottom'].set_position(('outward', 40))
ax3.set_xlabel(r'Volume, $\forall_b$ [mL]')
ax3.set_xlim(0, mmm_to_ml(max(x_DTB.max(), x_UTB.max()) * A_bore))
ax3.set_ylim(0, )
ax3.plot(mmm_to_ml(x_DTB * A_bore), np.ones(num)-2, lw=0)

# save and show the plot
experiment_id = f'Pressure_v_pistionPos_compare'
plot_path = plot_folder.joinpath(''.join(["Plot_", experiment_id, ".", plot_format]))
plt.savefig(plot_path, dpi=600, bbox_inches='tight', transparent=True)
plt.show()


# In[81]:


# ranges for color map generation
ES = np.linspace(0, 1, len(temp))
AW = np.arange(0, len(temp))
# normalize color map across temperature range
normal = plt.Normalize(K_to_C(temp.min()), K_to_C(temp.max()))

# make the plot
fig, ax1 = plt.subplots(1, figsize = [7, 2*GOLDEN_RATIO] , dpi=100)

# plot valve open time as a function of piston position over temperature range.
for i,j in zip(AW, ES):
    ax1.plot(x_DTB * 1000, mmm_to_ml(Q_DTB[i]), c=cm.viridis((j)), zorder=-10)
plt.fill_between([0, fill_length_DTB*1000], [.4, .4],                  alpha=0.1, label=r'Filled Volume $\forall=${0:0.3f} mL'.format(mmm_to_ml(fill_volume_DTB)),                  color='black', hatch='', linewidth=0.0, zorder=1)    
plt.title('DTB')
plt.xlabel(r'Piston Position, $x$ [mm]')    
plt.ylabel(r'Max Flow Rate, $Q_{max}$ [ml/s]')
# plt.title(f'Dose = {mmm_to_ml(dose):0.3f} ml, k = {keff:0.0f}, effenciency = {mech_eff:0.2f}')
ax1.set_xlim(0, x_DTB.max()*1000)
ax1.set_ylim(0, .4)

# make the color bar
cax, _ = cbar.make_axes(ax1) 
cb2 = cbar.ColorbarBase(cax, cmap=cm.viridis, norm=normal, label='Temperature, $T$ [$^\circ$C]')

# save and show the plot
experiment_id = f'MaxFlowRate_v_Temp_DTB'
plot_path = plot_folder.joinpath(''.join(["Plot_", experiment_id, ".", plot_format]))
plt.savefig(plot_path, dpi=600, bbox_inches='tight', transparent=True)
plt.show()

