# toa_vs_tot.py
import os
import sys
import ROOT
import sifca_utils

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Utils import utils as u  # noqa

sifca_utils.plotting.set_sifca_style()


def make_name(inputfile: str) -> str:
    run_name = os.path.basename(inputfile).replace(".root", "")
    parent = os.path.basename(os.path.dirname(inputfile))
    return f"{parent}_{run_name}"


def compute_t(inputfile, cut=None):
    """
    Return df with derived columns: tbin, ToA, ToT (and any columns needed for plots).
    """
    df = ROOT.RDataFrame("Hits", inputfile)
    if cut is not None:
        df = df.Filter(cut)

    df = u.compute_tbin(df)
    df = u.compute_ToA(df)
    df = u.compute_ToT(df)
    return df


def get_cuts_and_cal_info(df0):
    max_cal = u.get_max_cal(df0)
    rel01, rel0m1, rel01m1 = u.get_Cal_relation(df0)
    mean_cal, sigma_cal = u.get_mean_cal(df0)

    base_cut = "cal > 0 && toa_code > 0"
    cal_cut = f"cal == {max_cal} && toa_code > 0"

    print(f"  max_cal (modo)  = {max_cal}")
    print(f"  mean_cal (fit)  = {mean_cal:.4f}")
    print(f"  sigma_cal (fit) = {sigma_cal:.4f}")
    print(f"  rel01   = {rel01:.4f}")
    print(f"  rel0m1  = {rel0m1:.4f}")
    print(f"  rel01m1 = {rel01m1:.4f}")
    print(f"  base_cut: {base_cut}")
    print(f"  cal_cut : {cal_cut}")

    return max_cal, rel01, rel0m1, rel01m1, mean_cal, sigma_cal, base_cut, cal_cut


# ---- 1D CAL ----
def plot_cal_1d(df, name, outdir):
    os.makedirs(outdir, exist_ok=True)

    c_cal = ROOT.TCanvas(f"c_cal_{name}", f"cal_{name}", 900, 750)
    hcal_ptr = df.Histo1D((f"hcal_{name}", f"{name};cal;Counts", 400, 0, 2000), "cal")
    hcal = hcal_ptr.GetValue()
    hcal.SetDirectory(0)
    hcal.Draw()
    c_cal.Update()

    out = os.path.join(outdir, f"cal_{name}.png")
    #c_cal.SaveAs(out)

    return out


# ---- 1D ToA ----
def plot_toa_1d(df, name, outdir):
    os.makedirs(outdir, exist_ok=True)

    c_toa_all = ROOT.TCanvas(f"c_toa_all_{name}", f"ToA_1D_all_{name}", 900, 750)
    htoa_all_ptr = df.Histo1D(
        (f"htoa_all_{name}", f"{name} (all);ToA [ns];Counts", 250, 0, 12.5),
        "ToA"
    )
    htoa_all = htoa_all_ptr.GetValue()
    htoa_all.SetDirectory(0)
    htoa_all.Draw("HIST")
    c_toa_all.Update()

    out = os.path.join(outdir, f"ToA_1D_all_{name}.png")
    #c_toa_all.SaveAs(out)
    return out


# ---- ToA vs CAL ----
def plot_toa_vs_cal_2d(df, name, outdir):
    os.makedirs(outdir, exist_ok=True)

    c = ROOT.TCanvas(f"c_toa_vs_cal_{name}", f"ToA_vs_cal_{name}", 900, 750)
    c.SetRightMargin(0.15)
    ROOT.gStyle.SetOptStat(0)

    h2_ptr = df.Histo2D(
        (f"h2_toa_vs_cal_{name}", f"{name};ToA [ns];cal", 200, 0, 12.5, 2000, 0, 2000),
        "ToA", "cal"
    )
    h2 = h2_ptr.GetValue()
    h2.SetDirectory(0)
    h2.Draw("COLZ")
    c.Update()

    out = os.path.join(outdir, f"ToA_vs_cal_{name}.png")
    #c.SaveAs(out)

    return out


# ---- ToA vs ToT ----
def plot_toa_vs_tot_2d(df, name, outdir):
    os.makedirs(outdir, exist_ok=True)

    c_tot = ROOT.TCanvas(f"c_toa_vs_tot_{name}", f"ToA_vs_ToT_{name}", 900, 750)
    c_tot.SetRightMargin(0.15)
    ROOT.gStyle.SetOptStat(0)

    h2_ptr = df.Histo2D(
        (f"h2_toa_vs_tot_{name}", f"{name};ToA [ns];ToT [ns]", 250, 0, 12.5, 250, 0, 25),
        "ToA", "ToT"
    )
    h2_tot = h2_ptr.GetValue()
    h2_tot.SetDirectory(0)
    h2_tot.Draw("COLZ")
    c_tot.Update()

    out = os.path.join(outdir, f"ToA_vs_ToT_{name}.png")
    #c_tot.SaveAs(out)

    return out