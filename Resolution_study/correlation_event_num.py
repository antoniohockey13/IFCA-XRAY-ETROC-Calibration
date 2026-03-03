import os
import math
import ROOT


def matched_events(m1, m2):
    """
    Return sorted list of common event_number between two maps.
    """
    return sorted(set(m1.keys()) & set(m2.keys()))


def plot_tot_correlation_2d(common, m1, m2, outdir, name="ToT_K2_vs_K3"):
    os.makedirs(outdir, exist_ok=True)

    h2 = ROOT.TH2D(
        f"h2_{name}",
        f"{name};ToT file1 [ns];ToT file2 [ns]",
        200, 0, 25,
        200, 0, 25
    )
    h2.SetDirectory(0)

    for evn in common:
        h2.Fill(float(m1[evn][1]), float(m2[evn][1]))

    c = ROOT.TCanvas(f"c_{name}", name, 900, 750)
    c.SetRightMargin(0.15)
    ROOT.gStyle.SetOptStat(0)
    h2.Draw("COLZ")

    out_png = os.path.join(outdir, f"{name}.png")
    out_root = os.path.join(outdir, f"{name}.root")
    c.SaveAs(out_png)

    fout = ROOT.TFile(out_root, "RECREATE")
    h2.Write()
    fout.Close()

    print(f"[OK] Saved 2D corr: {out_png}")
    print(f"[OK] Saved 2D ROOT: {out_root}")
    return out_png, out_root


def plot_tot_overlay_1d(common, m1, m2, outdir, name="ToT_overlay"):
    """
    1D overlay: ToT distributions for matched events (file1 vs file2)
    """
    os.makedirs(outdir, exist_ok=True)

    h1 = ROOT.TH1D(f"h1_{name}_file1", f"{name};ToT [ns];Counts", 200, 0, 25)
    h2 = ROOT.TH1D(f"h1_{name}_file2", f"{name};ToT [ns];Counts", 200, 0, 25)
    h1.SetDirectory(0)
    h2.SetDirectory(0)

    for evn in common:
        h1.Fill(float(m1[evn][1]))
        h2.Fill(float(m2[evn][1]))

    c = ROOT.TCanvas(f"c_{name}", name, 900, 750)
    ROOT.gStyle.SetOptStat(0)

    h1.SetLineWidth(2)
    h2.SetLineWidth(2)
    h2.SetLineStyle(2)

    h1.Draw("HIST")
    h2.Draw("HIST SAME")

    leg = ROOT.TLegend(0.65, 0.75, 0.88, 0.88)
    leg.AddEntry(h1, "file1 (matched)", "l")
    leg.AddEntry(h2, "file2 (matched)", "l")
    leg.Draw()

    out_png = os.path.join(outdir, f"{name}.png")
    out_root = os.path.join(outdir, f"{name}.root")
    c.SaveAs(out_png)

    fout = ROOT.TFile(out_root, "RECREATE")
    h1.Write()
    h2.Write()

    print(f"[OK] Saved overlay: {out_png}")
    print(f"[OK] Saved overlay ROOT: {out_root}")
    return out_png, out_root


def plot_tot_by_event_1d(common, m1, m2, outdir, name="ToT_by_event_1D"):
    """
    Simple TGraph of ToT vs event_number (two graphs in same canvas).
    Useful if you don't want TH3.
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
    g1.SetLineWidth(2)
    g2.SetLineWidth(2)
    g2.SetLineStyle(2)

    c = ROOT.TCanvas(f"c_{name}", name, 1100, 600)
    ROOT.gStyle.SetOptStat(0)
    g1.Draw("AL")
    g2.Draw("L SAME")

    leg = ROOT.TLegend(0.70, 0.80, 0.90, 0.90)
    leg.AddEntry(g1, "file1", "l")
    leg.AddEntry(g2, "file2", "l")
    leg.Draw()

    out_png = os.path.join(outdir, f"{name}.png")
    out_root = os.path.join(outdir, f"{name}.root")
    c.SaveAs(out_png)

    fout = ROOT.TFile(out_root, "RECREATE")
    g1.Write("g_file1")
    g2.Write("g_file2")

    print(f"[OK] Saved ToT vs event graph: {out_png}")
    print(f"[OK] Saved graph ROOT: {out_root}")
    return out_png, out_root


def plot_delta_toa_with_fit(common, m1, m2, outdir,
                            base1="file1", base2="file2",
                            name="deltaToA"):
    """
    Histogram of ΔToA = ToA_1 - ToA_2 for matched events + gaussian fit.

    Saves:
      - PNG
      - ROOT (hist)
    """
    os.makedirs(outdir, exist_ok=True)

    if len(common) == 0:
        print("[WARN] No common events for delta ToA.")
        return None, None

    ROOT.gStyle.SetOptStat(0)
    c = ROOT.TCanvas(f"c_{name}", "Delta ToA", 900, 700)

    h = ROOT.TH1D(
        f"h_{name}",
        f"#Delta ToA = ToA_1 - ToA_2;#Delta ToA [ns];Counts",
        200, -15, 15
    )
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

    out_png = os.path.join(outdir, f"{name}_{base1}_minus_{base2}_key-event_number.png")
    out_root = os.path.join(outdir, f"{name}_{base1}_minus_{base2}_key-event_number.root")
    c.SaveAs(out_png)

    fout = ROOT.TFile(out_root, "RECREATE")
    h.Write()

    print(f"[OK] Saved: {out_png}")
    print(f"[OK] Saved: {out_root}")
    print(f"[RESULT] sigma(ΔToA) = {sigma:.6f} ± {sigma_err:.6f} ns")
    print(f"[RESULT] sigma_single ≈ {sigma_single:.6f} ± {sigma_single_err:.6f} ns (assumes equal sensors)")

    return out_png, out_root


def plot_colrow_correlations_2d(common, m1, m2, outdir, name="colrow_corr"):
    """
    2D correlations:
      - col(file1) vs col(file2)
      - row(file1) vs row(file2)
    Z axis is counts (how many times selected), as desired.
    """
    os.makedirs(outdir, exist_ok=True)

    n_pix = 16
    hcol = ROOT.TH2D(
        f"hcol_{name}",
        f"{name};col file1;col file2",
        n_pix, -0.5, n_pix - 0.5,
        n_pix, -0.5, n_pix - 0.5
    )
    hrow = ROOT.TH2D(
        f"hrow_{name}",
        f"{name};row file1;row file2",
        n_pix, -0.5, n_pix - 0.5,
        n_pix, -0.5, n_pix - 0.5
    )
    hcol.SetDirectory(0)
    hrow.SetDirectory(0)

    for evn in common:
        col1 = int(m1[evn][3])
        row1 = int(m1[evn][4])
        col2 = int(m2[evn][3])
        row2 = int(m2[evn][4])
        hcol.Fill(col1, col2)
        hrow.Fill(row1, row2)

    ROOT.gStyle.SetOptStat(0)

    c1 = ROOT.TCanvas(f"c_col_{name}", "col corr", 900, 750)
    c1.SetRightMargin(0.15)
    hcol.Draw("COLZ")
    out_col = os.path.join(outdir, f"{name}_col.png")
    c1.SaveAs(out_col)

    c2 = ROOT.TCanvas(f"c_row_{name}", "row corr", 900, 750)
    c2.SetRightMargin(0.15)
    hrow.Draw("COLZ")
    out_row = os.path.join(outdir, f"{name}_row.png")
    c2.SaveAs(out_row)

    out_root = os.path.join(outdir, f"{name}_colrow.root")
    fout = ROOT.TFile(out_root, "RECREATE")
    hcol.Write()
    hrow.Write()

    print(f"[OK] Saved col corr: {out_col}")
    print(f"[OK] Saved row corr: {out_row}")
    print(f"[OK] Saved col/row ROOT: {out_root}")
    return (out_col, out_row, out_root)