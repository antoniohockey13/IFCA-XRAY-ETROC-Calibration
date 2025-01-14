# ETROC Calibration

Scripts for the ETROC Calibration using the X-Ray setup at IFCA. 

## Code structure
The setup produces `.nem` files with the hits information stored as:
```
EH version event_number hits_count num_words
H channel L1Counter Type BCID
D channel EA Row Col Toa Tot Cal
T channel status hits CRC
```

- `translate_data_to_root.py`: converts this information into a ROOT file for storaging and analysing purposes. 
- `filter_by_cal.py`: Filter the data with the measured `Cal` values. It is expected to have a Delta dirac like distribution. This is not observed, something should be going with the ETROC. Also, it converts the ToA_Code and ToT_Code into ToA and ToT in ns. It creates a new ROOT file with this information called `Filtered_*.root`
- `plot_hit_map_tot_toa.py`: File to plot hit map, ToT and ToA measured. 
-`Find_peaks.py`: Given a ROOT file with TOT data plots and finds the peaks using TSpectrum
-`plot_peak_calibration.py`: File to plot and fit ToT-Energy calibrations, values are hardcoded in the file
-`plot_ToAs.py`: Given files of different Cal values plots the ToA of those files together in a stack way and one on-top of each other
