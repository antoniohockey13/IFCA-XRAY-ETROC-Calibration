import os
import math
import ROOT
from Utils import utils as u
from array import array


######################################################
# Helpers                                            #
######################################################

def build_hit_map(df, choose="max_tot"):
    """
    Reduce a dataframe to one entry per event_id.

    Output format:
      event_id -> (ToA, ToT, cal, col, row, l1counter_global, bcid)

    choose:
      - max_tot : keep hit with largest ToT
      - first   : keep first hit found
      - unique  : keep only event_ids with exactly one hit
    """
    needed_cols = [
        "event_id", "ToA", "ToT", "cal", "col", "row"]

    arr = df.AsNumpy(needed_cols)

    n = len(arr["event_id"])
    counts = {}
    hit_map = {}

    for i in range(n):
        ev = int(arr["event_id"][i])
        counts[ev] = counts.get(ev, 0) + 1

    for i in range(n):
        ev = int(arr["event_id"][i])
        toa = float(arr["ToA"][i])
        tot = float(arr["ToT"][i])
        cal = int(arr["cal"][i])
        col = int(arr["col"][i])
        row = int(arr["row"][i])

        value = (toa, tot, cal, col, row)

        if choose == "unique":
            if counts[ev] != 1:
                continue
            hit_map[ev] = value
            continue

        if ev not in hit_map:
            hit_map[ev] = value
            continue

        if choose == "max_tot":
            if tot > hit_map[ev][1]:
                hit_map[ev] = value

        elif choose == "first":
            pass

        else:
            raise ValueError(f"Unknown choose mode: {choose}")

    print(f"[INFO] Events stored with choose='{choose}': {len(hit_map)}")

    if choose == "unique":
        removed = sum(1 for ev in counts if counts[ev] > 1)
        print(f"[INFO] Removed events with multiple hits: {removed}")

    return hit_map

def join_maps_by_event_id(map_k3, map_k2):
    common_ids = sorted(set(map_k3.keys()) & set(map_k2.keys()))
    print(f"[INFO] Common event_id: {len(common_ids)}")
    print(f"[INFO] Only in K3: {len(set(map_k3.keys()) - set(map_k2.keys()))}")
    print(f"[INFO] Only in K2: {len(set(map_k2.keys()) - set(map_k3.keys()))}")
    return common_ids

def build_matched_tree(common, m_k3, m_k2, outpath):

    f = ROOT.TFile(outpath, "RECREATE")
    t = ROOT.TTree("MatchedHits", "MatchedHits")

    arrs = {
        "event_id": array("i", [0]),
        "ToA_k3": array("d", [0.0]),
        "ToT_k3": array("d", [0.0]),
        "cal_k3": array("i", [0]),
        "col_k3": array("i", [0]),
        "row_k3": array("i", [0]),
        "ToA_k2": array("d", [0.0]),
        "ToT_k2": array("d", [0.0]),
        "cal_k2": array("i", [0]),
        "col_k2": array("i", [0]),
        "row_k2": array("i", [0]),
        "delta_ToA": array("d", [0.0]),
        "delta_ToT": array("d", [0.0]),
        "delta_col": array("i", [0]),
        "delta_row": array("i", [0]),
        "delta_r": array("d", [0.0]),
    }

    for name, buf in arrs.items():
        leaf = "D" if buf.typecode == "d" else "I"
        t.Branch(name, buf, f"{name}/{leaf}")

    for ev in common:
        toa_k3, tot_k3, cal_k3, col_k3, row_k3 = m_k3[ev]
        toa_k2, tot_k2, cal_k2, col_k2, row_k2 = m_k2[ev]

        dcol = int(col_k2) - int(col_k3)
        drow = int(row_k2) - int(row_k3)
        dr = math.sqrt(dcol*dcol + drow*drow)

        arrs["event_id"][0] = int(ev)

        arrs["ToA_k3"][0] = float(toa_k3)
        arrs["ToT_k3"][0] = float(tot_k3)
        arrs["cal_k3"][0] = int(cal_k3)
        arrs["col_k3"][0] = int(col_k3)
        arrs["row_k3"][0] = int(row_k3)

        arrs["ToA_k2"][0] = float(toa_k2)
        arrs["ToT_k2"][0] = float(tot_k2)
        arrs["cal_k2"][0] = int(cal_k2)
        arrs["col_k2"][0] = int(col_k2)
        arrs["row_k2"][0] = int(row_k2)

        arrs["delta_ToA"][0] = float(toa_k2 - toa_k3)
        arrs["delta_ToT"][0] = float(tot_k2 - tot_k3)
        arrs["delta_col"][0] = dcol
        arrs["delta_row"][0] = drow
        arrs["delta_r"][0] = dr

        t.Fill()

    t.Write()
    f.Close()
    return outpath


######################################################
# Plots                                              #
######################################################
def get_histogram_limits_from_column(df: ROOT.RDataFrame, column: str, margin=2.5):
    min_val = float(df.Min(column).GetValue())
    max_val = float(df.Max(column).GetValue())

    min_val = min_val - margin
    max_val = max_val + margin
    bin_number = int(max_val - min_val)*100

    return min_val, max_val, bin_number


def plot_tot_correlation(df, outdir, name="ToT_corr", fout=None):
    u.ensure_outdir(outdir)

    c = ROOT.TCanvas(f"c_{name}")
    xmin, xmax, nbins = get_histogram_limits_from_column(df, "ToT_k3")
    h = df.Histo2D((f"h_{name}", ";ToT K3 [ns];ToT K2 [ns]", nbins, xmin, xmax, nbins, xmin, xmax), "ToT_k3", "ToT_k2")
    h2 = h.GetValue()
    h2.SetDirectory(0)
    h2.Draw("COLZ")
    c.Update()

    input("Press Enter to continue...")
    out = os.path.join(outdir, f"{name}.png")
    c.SaveAs(out)
    u.write_to_fout(fout, h2, c)
    return out

def plot_toa_correlation(df, outdir, name="ToA_corr", fout=None):
    u.ensure_outdir(outdir)

    c = ROOT.TCanvas(f"c_{name}")
    h = df.Histo2D((f"h_{name}", ";ToA K3 [ns];ToA K2 [ns]", 125, 0, 12.5, 125, 0, 12.5), "ToA_k3", "ToA_k2")
    h2 = h.GetValue()
    h2.SetDirectory(0)
    h2.Draw("COLZ")
    c.Update()

    input("Press Enter to continue...")
    out = os.path.join(outdir, f"{name}.png")
    c.SaveAs(out)
    u.write_to_fout(fout, h2, c)
    return out

def plot_delta_toa(df, outdir, name="deltaToA", fout=None):
    u.ensure_outdir(outdir)

    c = ROOT.TCanvas(f"c_{name}")
    h = df.Histo1D((f"h_{name}", ";#Delta ToA [ns];Counts", 200, -20, 20), "delta_ToA")
    hh = h.GetValue()
    hh.SetDirectory(0)
    hh.Draw("HIST")

    # Fit range: mean ± 2*RMS
    mean = hh.GetMean()
    rms = hh.GetRMS()
    fit_min = mean - 2.0 * rms
    fit_max = mean + 2.0 * rms

    fgaus = ROOT.TF1(f"fgaus_{name}", "gaus", fit_min, fit_max)
    hh.Fit(fgaus, "SQR")

    mu = fgaus.GetParameter(1)
    sigma = fgaus.GetParameter(2)
    mu_err = fgaus.GetParError(1)
    sigma_err = fgaus.GetParError(2)

    sigma_single = sigma / math.sqrt(2.0)
    sigma_single_err = sigma_err / math.sqrt(2.0)

    txt = ROOT.TLatex()
    txt.SetNDC()
    txt.SetTextSize(0.035)
    txt.DrawLatex(0.15, 0.80, f"#mu = {mu:.4f} #pm {mu_err:.4f} ns")
    txt.DrawLatex(0.15, 0.75, f"#sigma(#Delta ToA) = {sigma:.4f} #pm {sigma_err:.4f} ns")
    txt.DrawLatex(0.15, 0.70, f"#sigma(single) #approx {sigma_single:.4f} #pm {sigma_single_err:.4f} ns")

    input("Press Enter to continue...")
    out_png = None
    if fout is not None:
        out_png = os.path.join(outdir, f"{name}.png")
        c.SaveAs(out_png)
        print(f"[INFO] Saved delta ToA graph: {out_png}")

    u.write_to_fout(fout, hh, c)

    print(f"[RESULT] sigma(ΔToA) = {sigma:.6f} ± {sigma_err:.6f} ns")
    print(f"[RESULT] sigma_single ≈ {sigma_single:.6f} ± {sigma_single_err:.6f} ns (assumes equal sensors)")

    return out_png

def plot_colrow_corr(df, outdir, name="colrow_corr", fout=None):
    u.ensure_outdir(outdir)

    c = ROOT.TCanvas(f"c_{name}", name, 900, 400)
    c.Divide(2, 1)

    c.cd(1)
    hcol_ptr = df.Histo2D(
        (f"hcol_{name}", ";col K3;col K2", 16, -0.5, 15.5, 16, -0.5, 15.5),
        "col_k3", "col_k2"
    )
    hcol = hcol_ptr.GetValue()
    hcol.SetDirectory(0)
    hcol.Draw("COLZ")

    c.cd(2)
    hrow_ptr = df.Histo2D(
        (f"hrow_{name}", ";row K3;row K2", 16, -0.5, 15.5, 16, -0.5, 15.5),
        "row_k3", "row_k2"
    )
    hrow = hrow_ptr.GetValue()
    hrow.SetDirectory(0)
    hrow.Draw("COLZ")

    c.Update()

    input("Press Enter to continue...")
    out = os.path.join(outdir, f"{name}.png")
    c.SaveAs(out)
    u.write_to_fout(fout, hcol, hrow, c)
    return out


def plot_tot_overlay(df, outdir, name="ToT_overlay", fout=None):
    u.ensure_outdir(outdir)

    xmin_k3, xmax_k3, _ = get_histogram_limits_from_column(df, "ToT_k3", margin=0.2)
    xmin_k2, xmax_k2, _ = get_histogram_limits_from_column(df, "ToT_k2", margin=0.2)

    xmin = min(xmin_k3, xmin_k2)
    xmax = max(xmax_k3, xmax_k2)
    nbins = max(50, int((xmax - xmin) * 100))

    c = ROOT.TCanvas(f"c_{name}", name)

    h2_ptr = df.Histo1D((f"h1_{name}_K2", ";ToT [ns];Counts", nbins, xmin, xmax), "ToT_k2")
    h1_ptr = df.Histo1D((f"h1_{name}_K3", ";ToT [ns];Counts", nbins, xmin, xmax), "ToT_k3")

    h1 = h1_ptr.GetValue()
    h2 = h2_ptr.GetValue()
    h1.SetDirectory(0)
    h2.SetDirectory(0)

    h2.SetLineStyle(2)

    ymax = 1.10 * max(h1.GetMaximum(), h2.GetMaximum())
    h1.SetMaximum(ymax)

    h1.Draw("HIST")
    h2.Draw("HIST SAME")

    leg = ROOT.TLegend()
    leg.AddEntry(h1, "K3", "l")
    leg.AddEntry(h2, "K2", "l")
    leg.Draw()

    c.Update()

    input("Press Enter to continue...")
    out = os.path.join(outdir, f"{name}.png")
    c.SaveAs(out)
    u.write_to_fout(fout, h1, h2, c)
    return out

def plot_event_by_event_pixel_shift(df, outdir, name="event_by_event_pixel_shift", fout=None):
    u.ensure_outdir(outdir)

    c1 = ROOT.TCanvas(f"c_{name}_dx", f"{name} dx")
    hdx_ptr = df.Histo1D((f"hdx_{name}", ";#Delta col (K2-K3);Counts", 33, -16.5, 16.5), "delta_col")
    hdx = hdx_ptr.GetValue()
    hdx.SetDirectory(0)
    hdx.Draw("HIST")

    c2 = ROOT.TCanvas(f"c_{name}_dy", f"{name} dy")
    hdy_ptr = df.Histo1D((f"hdy_{name}", ";#Delta row (K2-K3);Counts", 33, -16.5, 16.5), "delta_row")
    hdy = hdy_ptr.GetValue()
    hdy.SetDirectory(0)
    hdy.Draw("HIST")

    c3 = ROOT.TCanvas(f"c_{name}_dr", f"{name} dr")
    hdr_ptr = df.Histo1D((f"hdr_{name}", ";Pixel distance;Counts", 50, 0, 20), "delta_r")
    hdr = hdr_ptr.GetValue()
    hdr.SetDirectory(0)
    hdr.Draw("HIST")

    c4 = ROOT.TCanvas(f"c_{name}_dxy", f"{name} dxy")
    h2_ptr = df.Histo2D(
        (f"h2_dxy_{name}", ";#Delta col;#Delta row", 33, -16.5, 16.5, 33, -16.5, 16.5),
        "delta_col", "delta_row"
    )
    h2 = h2_ptr.GetValue()
    h2.SetDirectory(0)
    h2.Draw("COLZ")

    input("Press Enter to continue...")

    out = {}
    if fout is not None:
        out["dx"] = os.path.join(outdir, f"{name}_dx.png"); c1.SaveAs(out["dx"])
        out["dy"] = os.path.join(outdir, f"{name}_dy.png"); c2.SaveAs(out["dy"])
        out["dr"] = os.path.join(outdir, f"{name}_dr.png"); c3.SaveAs(out["dr"])
        out["dxy"] = os.path.join(outdir, f"{name}_dxy.png"); c4.SaveAs(out["dxy"])

    u.write_to_fout(fout, hdx, hdy, hdr, h2, c1, c2, c3, c4)

    print(f"[RESULT] mean dx={hdx.GetMean():.3f}, RMS dx={hdx.GetRMS():.3f}")
    print(f"[RESULT] mean dy={hdy.GetMean():.3f}, RMS dy={hdy.GetRMS():.3f}")
    print(f"[RESULT] mean dr={hdr.GetMean():.3f}, RMS dr={hdr.GetRMS():.3f}")

    return out

def compute_costheta_hist(df, dz_mm=100.0, pitch_mm=1.3, outdir=".", name="costheta", fout=None):
    u.ensure_outdir(outdir)

    df2 = df.Define(
        "costheta",
        f"{dz_mm}/sqrt((delta_col*{pitch_mm})*(delta_col*{pitch_mm}) + (delta_row*{pitch_mm})*(delta_row*{pitch_mm}) + {dz_mm}*{dz_mm})"
    ).Define(
        "theta_deg",
        "acos(costheta)*180.0/3.141592653589793"
    )

    c = ROOT.TCanvas(f"c_{name}", name, 800, 800)
    c.Divide(1, 2)

    c.cd(1)
    h_costh_ptr = df2.Histo1D((f"h_costh_{name}", ";cos(#theta);Counts", 200, 0.0, 1.0), "costheta")
    h_costh = h_costh_ptr.GetValue()
    h_costh.SetDirectory(0)
    h_costh.Draw("HIST")

    c.cd(2)
    h_acos_ptr = df2.Histo1D((f"h_acos_{name}", ";arccos(cos(#theta)) [deg];Counts", 180, 0.0, 90.0), "theta_deg")
    h_acos = h_acos_ptr.GetValue()
    h_acos.SetDirectory(0)
    h_acos.Draw("HIST")

    c.Update()
    input("Press Enter to continue...")

    out = os.path.join(outdir, f"{name}.png")
    c.SaveAs(out)
    u.write_to_fout(fout, h_costh, h_acos, c)
    return out

C_MM_PER_NS = 299.792458

def compare_theta_methods(df, pitch_mm=1.3, z_cm=9.0, outdir=".", name="theta_comparison", fout=None):
    u.ensure_outdir(outdir)

    z_mm = z_cm * 10.0

    df2 = df.Define(
        "rT_mm",
        f"sqrt((delta_col*{pitch_mm})*(delta_col*{pitch_mm}) + (delta_row*{pitch_mm})*(delta_row*{pitch_mm}))"
    ).Define(
        "theta_geo",
        f"atan(rT_mm/{z_mm})"
    ).Define(
        "L_mm",
        f"{C_MM_PER_NS}*delta_ToA"
    ).Define(
        "valid_theta_time",
        f"abs(L_mm) >= {z_mm}"
    )

    c = ROOT.TCanvas(f"c_{name}", name, 900, 800)
    c.Divide(1, 2)

    c.cd(1)
    h_dt_ptr = df2.Histo1D((f"h_dt_{name}", ";#DeltaToA = ToA2-ToA1 [ns];Counts", 200, -20, 20), "delta_ToA")
    h_dt = h_dt_ptr.GetValue()
    h_dt.SetDirectory(0)
    h_dt.Draw("HIST")

    f = ROOT.TF1(f"f_dt_{name}", "gaus", -10, 10)
    h_dt.Fit(f, "RQ")

    mu_dt = f.GetParameter(1)
    sig_dt = f.GetParameter(2)

    print(f"[DT] mu = {mu_dt:.4f} ns, sigma = {sig_dt:.4f} ns")

    c.cd(2)
    h_theta_geo_ptr = df2.Histo1D((f"h_theta_geo_{name}", ";#theta [rad];Counts", 500, 0, 2*math.pi), "theta_geo")
    h_theta_geo = h_theta_geo_ptr.GetValue()
    h_theta_geo.SetDirectory(0)
    h_theta_geo.SetLineColor(ROOT.kBlack)
    h_theta_geo.SetLineWidth(2)
    h_theta_geo.Draw("HIST")

    df_time = df2.Filter("valid_theta_time").Define(
        "theta_time",
        f"acos({z_mm}/L_mm)"
    )

    h_theta_time_ptr = df_time.Histo1D((f"h_theta_time_{name}", ";#theta [rad];Counts", 500, 0, 2*math.pi), "theta_time")
    h_theta_time = h_theta_time_ptr.GetValue()
    h_theta_time.SetDirectory(0)
    h_theta_time.SetLineColor(ROOT.kBlue)
    h_theta_time.SetLineWidth(2)
    h_theta_time.Draw("HIST SAME")

    leg = ROOT.TLegend(0.6, 0.7, 0.88, 0.88)
    leg.AddEntry(h_theta_geo, "#theta geometric (z fixed)", "l")
    leg.AddEntry(h_theta_time, "#theta from timing", "l")
    leg.Draw()

    c.Update()
    input("Press Enter to continue...")

    out = os.path.join(outdir, f"{name}.png")
    c.SaveAs(out)
    u.write_to_fout(fout, h_dt, h_theta_geo, h_theta_time, c)

    return out, mu_dt, sig_dt