# toa_vs_tot.py
import os
import sys

from numpy import size
import ROOT
import sifca_utils

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Utils import utils as u  # noqa

sifca_utils.plotting.set_sifca_style()


def make_name(inputfile: str) -> str:
    run_name = os.path.basename(inputfile).replace(".root", "")
    parent = os.path.basename(os.path.dirname(inputfile))
    return f"{parent}_{run_name}"

def _write_to_fout(fout, *objs):
    if fout is None:
        return
    fout.cd()
    for o in objs:
        if o:
            o.Write("", ROOT.TObject.kOverwrite)


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
def plot_cal_1d(df, name, outdir, fout = None):
    os.makedirs(outdir, exist_ok=True)

    c_cal = ROOT.TCanvas(f"c_cal_{name}", f"cal_{name}")
    hcal_ptr = df.Histo1D((f"hcal_{name}", f";cal;Counts", 300, 0, 300), "cal")
    hcal = hcal_ptr.GetValue()
    hcal.SetDirectory(0)
    hcal.Draw()
    c_cal.Update()

    input("Press Enter to continue...")
    out = os.path.join(outdir, f"cal_{name}.png")
    c_cal.SaveAs(out)
    _write_to_fout(fout, hcal, c_cal)
    return out


# ---- 1D ToA ----
def plot_toa_1d(df, name, outdir, fout = None):
    os.makedirs(outdir, exist_ok=True)

    c_toa = ROOT.TCanvas(f"c_toa_{name}", f"ToA_1D_{name}")
    htoa_ptr = df.Histo1D((f"htoa_{name}", f";ToA [ns];Counts", 250, 0, 12.5),"ToA")

    htoa = htoa_ptr.GetValue()
    htoa.SetDirectory(0)
    htoa.Draw("HIST")
    c_toa.Update()

    input("Press Enter to continue...")
    out = os.path.join(outdir, f"ToA_1D_{name}.png")
    c_toa.SaveAs(out)
    _write_to_fout(fout, htoa, c_toa)
    return out

# ---- 1D ToT ----
def plot_tot_1d(df, name, outdir, fout = None):
    os.makedirs(outdir, exist_ok=True)

    c_tot = ROOT.TCanvas(f"c_tot_{name}", f"ToT_1D_{name}")
    htot_ptr = df.Histo1D((f"htot_{name}", f";ToT [ns];Counts", 250, 0, 5),"ToT")
    htot = htot_ptr.GetValue()
    htot.SetDirectory(0)
    htot.Draw("HIST")
    c_tot.Update()

    input("Press Enter to continue...")
    out = os.path.join(outdir, f"ToT_1D_{name}.png")
    c_tot.SaveAs(out)
    _write_to_fout(fout, htot, c_tot)
    return out

# ---- ToA vs CAL ----
def plot_toa_vs_cal_2d(df, name, outdir, fout = None):
    os.makedirs(outdir, exist_ok=True)

    c = ROOT.TCanvas(f"c_toa_vs_cal_{name}", f"ToA_vs_cal_{name}")

    h2_ptr = df.Histo2D((f"h2_toa_vs_cal_{name}", f";ToA [ns];cal", 250, 0, 12.5, 1000, 0, 1000),"ToA", "cal")
    h2 = h2_ptr.GetValue()
    h2.SetDirectory(0)
    h2.Draw("COLZ")
    c.Update()

    input("Press Enter to continue...")
    out = os.path.join(outdir, f"ToA_vs_cal_{name}.png")
    c.SaveAs(out)
    _write_to_fout(fout, h2, c)
    return out


# ---- ToA vs ToT ----
def plot_toa_vs_tot_2d(df, name, outdir, fout = None):
    os.makedirs(outdir, exist_ok=True)

    c_tot = ROOT.TCanvas(f"c_toa_vs_tot_{name}", f"ToA_vs_ToT_{name}")

    h2_ptr = df.Histo2D((f"h2_toa_vs_tot_{name}", f";ToA [ns];ToT [ns]", 250, 0, 12.5, 250, 0, 25),"ToA", "ToT")
    h2_tot = h2_ptr.GetValue()
    h2_tot.SetDirectory(0)
    h2_tot.Draw("COLZ")
    c_tot.Update()

    input("Press Enter to continue...")
    out = os.path.join(outdir, f"ToA_vs_ToT_{name}.png")
    c_tot.SaveAs(out)

    _write_to_fout(fout, h2_tot, c_tot)
    return out