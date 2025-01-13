import sifca_utils.plotting
import ROOT
import numpy as np
import sifca_utils

sifca_utils.plotting.set_sifca_style()
# Energy peaks in the simulation
#8.366336633663366, 9.686468646864686, 9.95049504950495, 11.303630363036303
"""
WRONG CALIBRATION VALUES due to wrong Cal plot

# # ToT measured in TFM 35kV data, Filtered_2024_06_13-08_37_11.root, analogical = 0
# tot_peaks = [3.4504716981132075, 2.2948113207547167, 3.714622641509434]

# # ToT measured in TFM 35kV data, Filtered_0.5-2024_06_13-08_37_11.root analogical = 1
# tot_peaks = [3.518716556249204, 3.331550993757167, 3.7433152312396487, 3.106952318766722] 
# tot_error = 0.0374251497005988

# ToT measured in TFM 35kV data, Filtered_2.5_Same_Cal-2024_06_13-08_37_11.root analogical = 0
tot_peaks = [3.046297843891024, 3.4351854062701457, 3.6944437811895603]
tot_error = 0.03238341968911917

# ToT measured in TFM 35kV data, Filtered_2.5_Same_Cal-2024_06_13-08_37_11.root analogical = 1
# tot_peaks = [3.331550993757167, 3.518716556249204, 3.7433152312396487]
# tot_error = 0.0374251497005988

# Energy peaks in simulation
if len(tot_peaks) == 3:
    energy_peaks = [8.366336633663366, 11.303630363036303, 9.686468646864686]
if len(tot_peaks) == 4:
    energy_peaks =  [8.366336633663366, 11.303630363036303, 9.686468646864686, 9.95049504950495] 
energy_error = 0.033
"""
# # ToT measured in TFM 35kV data, Filtered_1.5_0-2024_06_13-08_37_11.root analogical = 0
# tot_peaks = [3.074772813927577, 3.4672902164559676, 4.088776103792585]
# tot_error = 0.03238341968911917
# energy_peaks = [8.366336633663366, 9.686468646864686, 11.303630363036303]
# energy_error = 0.033

# # ToT measured in TFM 35kV data, Filtered_1.5_0-2024_06_13-08_37_11.root analogical = 1
# tot_peaks = [2.370970000766336, 3.349462666768845, 3.4623656666922114, 4.741932999157031]
# tot_error = 0.03238341968911917
# energy_peaks = [8.366336633663366, 9.686468646864686, 9.95049504950495, 11.303630363036303]
# energy_error = 0.033

# ToT measured in TFM 35kV data, Filtered_1.5_0_Same_Cal-2024_06_13-08_37_11.root analogical = 0
tot_peaks = [3.060465494791667, 3.4511628327546298, 3.7116277247299387]
tot_error = 0.032552083333333336
energy_peaks = [8.366336633663366, 9.686468646864686, 11.303630363036303]
energy_error = 0.033
# ToT measured in TFM 35kV data, Filtered_1.5_0_Same_Cal-2024_06_13-08_37_11.root analogical = 1
tot_peaks = [3.3675710908148724, 3.556755246793626, 3.7837762339681302, 4.729697013861899]
tot_error = 0.037650602409638564
energy_peaks = [8.366336633663366, 9.686468646864686, 9.95049504950495, 11.303630363036303]
energy_error = 0.033


def main():
    # Order list of peaks
    tot_peaks.sort()
    energy_peaks.sort()
    
    # Get the number of points to plot
    n_points = min(len(tot_peaks), len(energy_peaks))
    # Create TCanvas to plot the data
    c = ROOT.TCanvas()
    
    # Create Graph for better visualization with erros
    graph = ROOT.TGraphErrors(n_points, np.array(energy_peaks[:n_points]), np.array(tot_peaks[:n_points]), np.array([energy_error]*n_points), np.array([tot_error]*n_points))
    graph.GetXaxis().SetLimits(0, 15)
    graph.GetYaxis().SetRangeUser(0, 5)
    graph.SetMarkerStyle(20)
    graph.SetMarkerSize(1)
    graph.SetMarkerColor(ROOT.kBlack)
    graph.SetTitle("ToT vs Energy Peaks;Energy/keV;ToT/ns")
    graph.Draw("AP")

    # Fit the points to a line
    fit = ROOT.TF1("fit", "[0]*x+[1]", 0, 15)
    # fit = ROOT.TF1("fit", "[0]*x", 0, 15)
    # Fit with errors
    graph.Fit(fit, "S")
    fit.Draw("same")

    # Compute R^2
    residuals = []
    for i in range(n_points):
        residuals.append(tot_peaks[i] - fit.Eval(energy_peaks[i]))
    residuals = np.array(residuals)
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((tot_peaks - np.mean(tot_peaks))**2)
    r2 = 1 - (ss_res / ss_tot)
    print(f"R^2: {r2}")
    
    # Add text to the plot
    text = ROOT.TLatex()
    text.SetTextSize(0.03)
    text.DrawLatex(0.5, 4.2, f"Fit: ToT = ({fit.GetParameter(0):.4f} \pm {fit.GetParError(0):.4f}) ns/keV * E "\
                f"+ ({fit.GetParameter(1):.4f} \pm {fit.GetParError(1):.4f}) ns")
    text.DrawLatex(0.5, 4.5, f"R^2: {r2:.2f}")
    c.Update()
    c.Draw()
    input("Press enter to continue...")

if __name__ == "__main__":
    main()
    
