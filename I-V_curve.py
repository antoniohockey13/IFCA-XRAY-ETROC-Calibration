import matplotlib.pyplot as plt 
import numpy as np

# Bump-bonded ETROC ET2-03 PAIR-16
# Voltages in V
V = 1
volts = np.array([-0, -5, -1, -2, -3, -4, -10, -20, -30, -40, -50, -60, -70, -80, -90, -100, -110, -120, -130, -140, -150, -160, -170, -180, -190, -200, -210, -215, -220, -225, -230, -235, -240, -245, -250, -255, -256,])*V
# Currents in uA
uA = 1
currents = np.array([0.11, -0.53, -0.29, -0.37, -0.43, -0.48, -0.7, -0.96, -1.32, -2.5, -5.96, -6.4, -6.87, -7.37, -7.92, -8.53, -9.23, -10.05, -10.99, -11.97, -13.1, -14.4, -15.93, -17.77, -19.99, -22.9, -26.5, -28.8, -31.4, -34.4, -38.1, -42.6, -48.4, -56.2, -67.4, -86.9, -92.7])*uA

# Plot I-V curve
# Use point markers with lines between them
plt.plot(volts, currents, '-o')
plt.xlabel('Voltage (V)')
plt.ylabel('Current (uA)')
plt.title('I-V ETROC ET2-03 PAIR-16')
plt.show()  

# Plot in the 1st quadrant
# Change the sign of the currents
currents_sign = -currents
# Change the sign of the voltages
volts_sign = -volts
plt.plot(volts_sign, currents_sign, '-o')
plt.xlabel('Voltage (V)')
plt.ylabel('Current (uA)')
plt.title('I-V ETROC ET2-03 PAIR-16')
plt.show()

# Same plot with logarithmic scale
# Currents in absolute value
abs_currents = np.abs(currents)
plt.plot(volts_sign, abs_currents, '-o')
plt.xlabel('Voltage (V)')
plt.ylabel('Current (uA)')
plt.title('I-V ETROC ET2-03 PAIR-16')
plt.yscale('log')
plt.show()
