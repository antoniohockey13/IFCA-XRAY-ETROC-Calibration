# ETROC Calibration

Scripts for the ETROC Calibration using the X-Ray setup at IFCA. Analysis of the ToA spectrum, Cal values and ToT is done.

## Measurement procedure
- `test_xray.py` is used to launch the measurement in the setup.
The setup produces `.nem` files with the hits information stored as:
```
EH version event_number hits_count num_words
H channel L1Counter Type BCID
D channel EA Row Col Toa Tot Cal
T channel status hits CRC
```
- `translate_data_to_root.py`: converts this information into a ROOT file for storing and analysing purposes.

The `I-V_curve.py` is used to plot the I-V curve of the used sensor, it is the first step to know the high voltage needed to fully deplete the sensor and work with it.
### ToA Analysis
The ToA (Time of Arrival) is analysed. For that different scripts are used.
- `single_run.py`: Plots the result of a single run
- `single_run_different_cuts.py`: Data of a single run but different cuts are applied to compare them
- `different_runs.py`: Data obtained in different runs is compared
- `toa_peaks_analysis.py`: Study the ToA and fits the peaks spectrum to a sin function. Also computes the first minimum and maximum as well as the period of the sin. Then, computes the mean.
- `study_cal_during_run.py`: Studies the evolution of the Cal values during one run. The `event_number` is used to order the hits.
These files use `utils.py` and `plot_functions.py` to show the results. In `utils.py` the ToA, ToT, histogram limits... are computed. The `plot_functions.py` has all the plots used defined there, the cuts are not done here.

To work with these scripts the cuts are set and done in the `single_run.py`, `single_run_different_cuts.py` and `different_runs.py. Then, the other scripts are used to handle the operations and plots. 

### Calibration
__TO DO__
- `find_peaks.py`: Given a ROOT file with TOT data plots and finds the peaks using TSpectrum
-  `plot_peak_calibration.py`: File to plot and fit ToT-Energy calibrations, values are hardcoded in the file

