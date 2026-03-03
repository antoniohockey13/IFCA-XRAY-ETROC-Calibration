import os
import math
import ROOT
from Resolution_study import toa_vs_tot as ttv


def matched_events(m1, m2):
    """
    Return sorted list of common event_number between two maps.
    """
    return sorted(set(m1.keys()) & set(m2.keys()))


def plot_tot_correlation_2d(common, m1, m2, outdir, name="ToT_K2_vs_K3", fout=None):
    os.makedirs(outdir, exist_ok=True)

    h2 = ROOT.TH2D(f"h2_{name}", f";ToT file1 [ns];ToT file2 [ns]", 200, 0, 25, 200, 0, 25)
    h2.SetDirectory(0)

    for evn in common:
        h2.Fill(float(m1[evn][1]), float(m2[evn][1]))

    c = ROOT.TCanvas(f"c_{name}", name)
    h2.Draw("COLZ")

    input("Press Enter to continue...")
    out_png = None
    if fout is not None:
        out_png = os.path.join(outdir, f"{name}.png")
        c.SaveAs(out_png)
        print(f"[INFO] Saved ToT vs event graph: {out_png}")

    ttv._write_to_fout(fout, h2, c)

    return out_png


def plot_tot_overlay_1d(common, m1, m2, outdir, name="ToT_overlay", fout=None):
    """
    ToT distributions for matched events (file1 vs file2)
    """
    os.makedirs(outdir, exist_ok=True)

    h1 = ROOT.TH1D(f"h1_{name}_file1", f";ToT [ns];Counts", 200, 0, 25)
    h2 = ROOT.TH1D(f"h1_{name}_file2", f";ToT [ns];Counts", 200, 0, 25)
    h1.SetDirectory(0)
    h2.SetDirectory(0)

    for evn in common:
        h1.Fill(float(m1[evn][1]))
        h2.Fill(float(m2[evn][1]))
    
    h2.SetLineStyle(2)

    c = ROOT.TCanvas(f"c_{name}", name)

    h1.Draw("HIST")
    h2.Draw("HIST SAME")

    leg = ROOT.TLegend()
    leg.AddEntry(h1, "K3", "l")
    leg.AddEntry(h2, "K2", "l")
    leg.Draw()

    input("Press Enter to continue...")
    out_png = None
    if fout is not None:
        out_png = os.path.join(outdir, f"{name}.png")
        c.SaveAs(out_png)
        print(f"[INFO] Saved ToT vs event graph: {out_png}")

    ttv._write_to_fout(fout, h1, h2, c)
    return out_png


def plot_tot_by_event_1d(common, m1, m2, outdir, name="ToT_by_event_1D", fout=None):
    """
    Simple TGraph of ToT vs event_number for matched events, both files on same graph.
    """
    os.makedirs(outdir, exist_ok=True)

    if len(common) == 0:
        print("[WARN] No common events to plot.")
        return None, None

    g1 = ROOT.TGraph(len(common))
    g2 = ROOT.TGraph(len(common))

    for i, evn in enumerate(common):
        g1.SetPoint(i, evn, float(m1[evn][1]))
        g2.SetPoint(i, evn, float(m2[evn][1]))

    g1.SetTitle(f"{name};event_number;ToT [ns]")

    c = ROOT.TCanvas(f"c_{name}", name)
    g1.Draw("AL")
    g2.Draw("L SAME")

    leg = ROOT.TLegend()
    leg.AddEntry(g1, "K3", "l")
    leg.AddEntry(g2, "K2", "l")
    leg.Draw()

    g1.SetName(f"g1_{name}")
    g2.SetName(f"g2_{name}")

    input("Press Enter to continue...")
    out_png = None
    if fout is not None:
        out_png = os.path.join(outdir, f"{name}.png")
        c.SaveAs(out_png)
        print(f"[INFO] Saved ToT vs event graph: {out_png}")

    ttv._write_to_fout(fout, g1, g2, c)

    return out_png


def plot_delta_toa_with_fit(common, m1, m2, outdir, base1="file1", base2="file2", name="deltaToA", fout=None):
    """
    Histogram of ΔToA = ToA_1 - ToA_2 for matched events + gaussian fit.
    """
    os.makedirs(outdir, exist_ok=True)

    if len(common) == 0:
        print("[WARN] No common events for delta ToA.")
        return None, None

    c = ROOT.TCanvas(f"c_{name}", "Delta ToA")

    h = ROOT.TH1D(f"h_{name}",";#Delta ToA [ns];Counts", 200, -15, 15)
    h.SetDirectory(0)

    for k in common:
        h.Fill(float(m1[k][0]) - float(m2[k][0]))

    h.Draw()

    # Fit range: mean ± 2*RMS
    mean = h.GetMean()
    rms = h.GetRMS()
    fit_min = mean - 2.0 * rms
    fit_max = mean + 2.0 * rms

    fgaus = ROOT.TF1(f"fgaus_{name}", "gaus", fit_min, fit_max)
    h.Fit(fgaus, "SQR")

    mu = fgaus.GetParameter(1)
    sigma = fgaus.GetParameter(2)
    mu_err = fgaus.GetParError(1)
    sigma_err = fgaus.GetParError(2)

    sigma_single = sigma / math.sqrt(2.0)
    sigma_single_err = sigma_err / math.sqrt(2.0)

    txt = ROOT.TLatex()
    txt.SetNDC()
    txt.SetTextSize(0.035)
    txt.DrawLatex(0.15, 0.85, f"Matched event_number: {len(common)}")
    txt.DrawLatex(0.15, 0.80, f"#mu = {mu:.4f} #pm {mu_err:.4f} ns")
    txt.DrawLatex(0.15, 0.75, f"#sigma(#Delta ToA) = {sigma:.4f} #pm {sigma_err:.4f} ns")
    txt.DrawLatex(0.15, 0.70, f"#sigma(single) #approx {sigma_single:.4f} #pm {sigma_single_err:.4f} ns")

    input("Press Enter to continue...")
    out_png = None
    if fout is not None:
        out_png = os.path.join(outdir, f"{name}.png")
        c.SaveAs(out_png)
        print(f"[INFO] Saved delta ToA graph: {out_png}")

    ttv._write_to_fout(fout, h, c, fgaus)

    print(f"[RESULT] sigma(ΔToA) = {sigma:.6f} ± {sigma_err:.6f} ns")
    print(f"[RESULT] sigma_single ≈ {sigma_single:.6f} ± {sigma_single_err:.6f} ns (assumes equal sensors)")

    return out_png


def plot_colrow_correlations_2d(common, m1, m2, outdir, name="colrow_corr", fout=None):
    """
    2D correlations:
      - col(file1) vs col(file2)
      - row(file1) vs row(file2)
    """
    os.makedirs(outdir, exist_ok=True)

    n_pix = 16
    hcol = ROOT.TH2D(f"hcol_{name}", f";col file1;col file2", n_pix, -0.5, n_pix - 0.5, n_pix, -0.5, n_pix - 0.5)
    hrow = ROOT.TH2D(f"hrow_{name}", f";row file1;row file2", n_pix, -0.5, n_pix - 0.5, n_pix, -0.5, n_pix - 0.5)
    hcol.SetDirectory(0)
    hrow.SetDirectory(0)

    for evn in common:
        col1 = int(m1[evn][3])
        row1 = int(m1[evn][4])
        col2 = int(m2[evn][3])
        row2 = int(m2[evn][4])
        hcol.Fill(col1, col2)
        hrow.Fill(row1, row2)

    c1 = ROOT.TCanvas(f"c_col_{name}", "col corr")
    hcol.Draw("COLZ")

    c2 = ROOT.TCanvas(f"c_row_{name}", "row corr")
    hrow.Draw("COLZ")

    input("Press Enter to continue...")
    out_col = None
    out_row = None
    if fout is not None:
        out_col = os.path.join(outdir, f"{name}_col.png")
        c1.SaveAs(out_col)
        out_row = os.path.join(outdir, f"{name}_row.png")
        c2.SaveAs(out_row)
        print(f"[INFO] Saved col corr: {out_col}")
        print(f"[INFO] Saved row corr: {out_row}")

    ttv._write_to_fout(fout, hcol, hrow, c1, c2)

    return (out_col, out_row)