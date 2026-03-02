import ROOT
import click
import sifca_utils
import os
import math

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Utils import utils as u

sifca_utils.plotting.set_sifca_style()

def build_hit_map(root_file, key="l1counter", choose="max_tot"):
    """
    Build a map: key_value -> (ToA, ToT, cal, event_number, col, row)
    Choose one representative hit per key:
      - choose="max_tot": hit with maximum ToT in that key
      - choose="first": first seen
    """


    base_cut = "cal > 0 && toa_code > 0"
    df = ROOT.RDataFrame("Hits", root_file)
    max_cal = u.get_max_cal(df)
    cal_cut = f"abs(cal - {max_cal}) < 2.5 && cal > 0 && toa_code > 0"

    df.Filter(cal_cut)

    # Calibrated quantities per hit
    df = u.compute_tbin(df)
    df = u.compute_ToA(df)    
    df = u.compute_ToT(df)  

    cols = [key, "ToA", "ToT", "cal", "event_number", "col", "row"]
    arr = df.AsNumpy(cols)

    m = {}
    n = len(arr[key])
    for i in range(n):
        k = int(arr[key][i])
        toa = float(arr["ToA"][i])
        tot = float(arr["ToT"][i])
        cal = int(arr["cal"][i])
        evn = int(arr["event_number"][i])
        col = int(arr["col"][i])
        row = int(arr["row"][i])

        if k not in m:
            m[k] = (toa, tot, cal, evn, col, row)
        else:
            if choose == "max_tot":
                if tot > m[k][1]:
                    m[k] = (toa, tot, cal, evn, col, row)
            elif choose == "first":
                pass
            else:
                raise ValueError(f"Unknown choose mode: {choose}")
    return m

@click.command()
@click.argument("root1", type=click.Path(exists=True))
@click.argument("root2", type=click.Path(exists=True))
@click.option("--key", type=click.Choice(["l1counter", "bcid", "event_number"]), default="l1counter",
              help="Key used to match triggers between files.")
@click.option("--choose", type=click.Choice(["max_tot", "first"]), default="max_tot",
              help="How to pick one hit per key within each file.")
@click.option("--outdir", default="Resolution_Plots", type=str)
@click.option("--nbins", default=200, type=int)
@click.option("--range_ns", default=5.0, type=float,
              help="Histogram range will be [-range_ns, +range_ns] in ns.")
def main(root1, root2, key, choose, outdir, nbins, range_ns):
    os.makedirs(outdir, exist_ok=True)

    print(f"[INFO] Reading 1: {root1}")
    m1 = build_hit_map(root1, key=key, choose=choose)
    print(f"[INFO] Unique {key} in file1: {len(m1)}")

    print(f"[INFO] Reading 2: {root2}")
    m2 = build_hit_map(root2, key=key, choose=choose)
    print(f"[INFO] Unique {key} in file2: {len(m2)}")

    common = sorted(set(m1.keys()) & set(m2.keys()))
    print(f"[INFO] Matched {key}: {len(common)}")

    if len(common) < 50:
        print("[WARN] Very few matched triggers. Check if key is correct (try --key bcid).")

    # Histogram of delta ToA
    ROOT.gStyle.SetOptStat(0)
    c = ROOT.TCanvas("c_dt", "Delta ToA", 900, 700)
    h = ROOT.TH1D("h_dt", f"#Delta ToA = ToA_1 - ToA_2;#Delta ToA [ns];Counts",
                  nbins, -range_ns, range_ns)

    # Fill
    for k in common:
        toa1 = m1[k][0]
        toa2 = m2[k][0]
        h.Fill(toa1 - toa2)

    h.Draw()

    # Gaussian fit around peak (auto: use mean +- 2*RMS)
    mean = h.GetMean()
    rms = h.GetRMS()
    fit_min = mean - 2.0*rms
    fit_max = mean + 2.0*rms

    fgaus = ROOT.TF1("fgaus", "gaus", fit_min, fit_max)
    fit_res = h.Fit(fgaus, "SQR")  # S=return, Q=quiet, R=range

    mu = fgaus.GetParameter(1)
    sigma = fgaus.GetParameter(2)
    mu_err = fgaus.GetParError(1)
    sigma_err = fgaus.GetParError(2)

    # If you assume both sensors have same resolution:
    sigma_single = sigma / math.sqrt(2.0)
    sigma_single_err = sigma_err / math.sqrt(2.0)

    txt = ROOT.TLatex()
    txt.SetNDC()
    txt.SetTextSize(0.035)
    txt.DrawLatex(0.15, 0.85, f"Matched {key}: {len(common)}")
    txt.DrawLatex(0.15, 0.80, f"#mu = {mu:.4f} #pm {mu_err:.4f} ns")
    txt.DrawLatex(0.15, 0.75, f"#sigma(#Delta ToA) = {sigma:.4f} #pm {sigma_err:.4f} ns")
    txt.DrawLatex(0.15, 0.70, f"#sigma(single) #approx {sigma_single:.4f} #pm {sigma_single_err:.4f} ns (if equal)")

    c.Update()

    base1 = os.path.basename(root1).replace(".root", "")
    base2 = os.path.basename(root2).replace(".root", "")
    out_png = os.path.join(outdir, f"deltaToA_{base1}_minus_{base2}_key-{key}_choose-{choose}.png")
    out_root = os.path.join(outdir, f"deltaToA_{base1}_minus_{base2}_key-{key}_choose-{choose}.root")

    c.SaveAs(out_png)

    fout = ROOT.TFile(out_root, "RECREATE")
    h.Write()
    fout.Close()

    print(f"[OK] Saved: {out_png}")
    print(f"[OK] Saved: {out_root}")
    print(f"[RESULT] sigma(ΔToA) = {sigma:.6f} ± {sigma_err:.6f} ns")
    print(f"[RESULT] sigma_single ≈ {sigma_single:.6f} ± {sigma_single_err:.6f} ns (assumes equal sensors)")

    input("Press Enter to continue...")

if __name__ == "__main__":
    main()